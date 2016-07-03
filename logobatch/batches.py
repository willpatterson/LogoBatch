"""
This file contains the batch classes
"""

from datetime import datetime
import os
import sys
sys.path.append("..")

from logobatch.logo_exceptions import NoUniqueFileFoundError,
                                     InvalidExecutableError,
                                     BatchTemplateFileNotFoundError,
                                     InvalidBatchTypeError
from logobatch.email_notice import Email

class Batch(object):
    """
    Base class for analysis and threadtest
    TODO:
        get rid of yaml_data!!! Get it its vairables into class attributes
    """

    def __init__(self, **kwds):
        """ """
        self.name = kwds.get('name', str(datetime.now()).replace(' ', '-'))
        self.batch_root = kwds.get('batch_base', self.raise_invalid_attribute(''))
        self.output = kwds.get('batch_base', os.path.join(self.batch_base,
                                                          self.name))
        self.command_base = kwds.get('command', self.raise_invalid_attribute(''))
        self.cpus = kwds.get('cpus', 1)
        self.unique = kwds.get('unique', None)
        self.email = kwds.get('email', False)

        if '{unique}' in self.command_base and self.unique is None:
            raise NoUniqueFileFoundError(("No 'unique' file was specifed in your"
                                          " yaml object but {unique} was found"
                                          " in your command"))

    def __new__(cls, **kwds):
        """Creates and returns proper batch type"""
        batch_type = kwds.get('batch_type', 'local')
        for cls in Batch.__subclasses__():
            if batch_type in cls.batch_type:
                return cls(**kwds)
        raise InvalidBatchTypeError

    @staticmethod
    def raise_invalid_attribute(message):
        """Raises error for invalid attribute settings"""
        raise Exception(message) #TODO add real exception


    def build_unique_path(self, unique):
        """
        Builds a path for the unique file
        Throws an error if unique path isn't valid
        """

        inserts = {}
        if '{mod}' in unique:
            inserts["mod"] = self.batch_base
        if '{in}' in unique:
            inserts["in"] = os.path.join(self.batch_base, 'in')
        unique = unique.format(**inserts)

        if not os.path.isfile(unique):
            raise NoUniqueFileFoundError("message goes here") #TODO add message

        return unique

    def format_command(self, unique_item=None):
        """
        Formats a command from the base command with class variables
        and adds them the the batches' command list
        """

        inserts = {}
        if '{exe}' in self.command_base:
            inserts["exe"] = self.executable
        if '{out}' in self.command_base:
            inserts["out"] = '{out}'
        if '{mod}' in self.command_base:
            inserts["mod"] = self.batch_base

        if '{in}' in self.command_base:
            inserts["in"] = os.path.join(self.batch_base, 'in')
        if '{unique}' in self.command_base:
            inserts["unique"] = unique_item

        if '{cpus}' in self.command_base:
            inserts["cpus"] = self.cpus

        self.commands.append(self.command_base.format(**inserts))

    @staticmethod
    def generate_unique(unique_path):
        """Opens a file with unique entries and yields them"""
        #TODO Possibly make this use the class variable

        with open(unique_path, "r") as uni:
            for line in uni:
                yield line.split(",")[0].replace("\n", "")

    # Virtual Methods vvvvvvvvvvvvvvvvvvv
    def create_commands(self):
        """
        Virtual method that, when implemented, will create the
        commands for the batch
        """

        raise NotImplementedError()

    def launch_batch(self):
        """
        """

        raise NotImplementedError()

class SlurmBatch(Batch):
    """ A Batch object with unique command parameters"""

    batch_type = ['slurm']
    def __init__(self, **kwds):
        """Init fucntion adds the sets the cpu number"""
        super().__init__(**kwds)

    # BEGIN Implemented Virtual Methods vvvvvvvvvvvvvvvvvv
    def create_commands(self):
        """Creates and adds commands with the format_command method"""

        for unique_item in self.generate_unique(self.unique_path):
            self.format_command(unique_item=unique_item)

    def launch_batch(self):
        self.create_commands()
        self.create_job_file("""...""")
        self.schedule_batch()

    # END Implemented Virtual Methods ^^^^^^^^^^^^^^^^^^

    def create_job_file(self, ntasks, email_info, run_name):
        """
        Creates job files from the batches' command list
        also populates the job_files list
        """

        template = self.read_btemplate()
        """
        with open("btemplate.sh", "r") as btemplate:
            template = btemplate.readlines()
        """

        file_count = 0
        count = 0
        while count < len(self.commands):
            job_name = "{name}-job-{count}".format(name=self.name,
                                                   count=file_count)
            job_out_path = os.path.join(self.out_path, job_name)
            print(job_out_path)

            slurm_file = "{job_name}-%j.out".format(job_name=job_name)
            slurm_file_path = os.path.join(job_out_path, slurm_file)

            job_file_path = os.path.join(job_out_path,
                                         ".".join([job_name, "sh"]))
            self.job_files.append(job_file_path)

            try:
                os.makedirs(job_out_path)
            except FileExistsError:
                pass

            with open(job_file_path, 'w') as bfile:
                #Write Slurm settings to slurm batch file ####################
                for line in template: #Write Template file
                    bfile.write(line) #

                #Write automated parameters to file
                bfile.write("#SBATCH -J {}\n".format(self.name))
                bfile.write("#SBATCH --cpus-per-task={}\n".format(self.cpus))
                bfile.write("#SBATCH -o {}\n".format(slurm_file_path))

                #Write commands###############################################
                try:
                    for _ in range(ntasks):
                        command = self.commands[count]
                        if '{out}' in command:
                            command = command.format(out=job_out_path)
                        bfile.write(command + '\n')

                        self.commands[count] = command
                        count += 1
                except IndexError:
                    pass

                #Write email commands #######################################
                if self.email is True:
                    email_objs = []
                    for email in email_info["addresses"]:
                        email_objs.append(Email(email,
                                                job_name,
                                                self.name,
                                                run_name,
                                                slurm_file,
                                                job_out_path,
                                                ntasks))
                        for email_obj in email_objs:
                            bfile.write(email_obj.generate_email_command() + '\n')

            file_count += 1

    def read_btemplate(self):
        """Reads btemplate file from a variety of locations"""

        template = ""
        paths = [os.path.join(self.batch_base, 'in', 'btemplate.sh'),
                 os.path.join(os.getcwd(), 'btemplate.sh'),
                 os.path.join(os.path.expanduser('~'), 'btemplate.sh')]
        for path in paths:
            try:
                with open(path, "r") as btemplate:
                    template = btemplate.readlines()
                return template
            except FileNotFoundError:
                pass

        raise BatchTemplateFileNotFoundError

    def schedule_batch(self):
        """Schedules the batches' job files in slurm"""

        for job_file in self.job_files:
            os.system("sbatch {job}".format(job=job_file))


class SshBatch(Batch):
    """ """

    batch_type = ['ssh']
    def __init__(self, **kwds):
        super().__init__(**kwds)

    def create_commands(self, command_number):
        """Creates command to be sent over ssh"""

        raw_commands = []
        for unique_item in self.generate_unique():
            raw_commands.append(self.format_command(unique_item))

        commands = []
        for i in range(0, len(tmp_commands), command_number):
            command_set = raw_commands[i:i+command_number]
            commands.append('({})&'.format('; '.join(command_set)))

        return compound_commands

    def launch_batch(self):
        """Schedules the batch job files over SSH"""
        pass

class ThreadTest(Batch):
    """
    A batch object that is used to run identical commands with
    a different numbers of CPUs or threads within a specified range

    This Batch obejct is intended to figure out where the point of
    deminishing returns related to the number of alloacted threads

    Thread test objects can use also run thread test ranges
    with unique parameters
    """

    batch_type = ['threadtest']
    def __init__(self, **kwds):
        """
        Sets the self.upper class var
        sets the self.cpus class var as lower. This is done to allow
        ThreadTest batches to use the format_command method
        """

        super().__init__(**kwds)
        self.upper = kwds.get('upper', raise_invalid_attribute("")
        self.cpus = kwds.get('lower', 1)

    def create_commands(self):
        """Creats and adds commands to the batch"""

        try:
            for unique_item in self.generate_unique(self.unique_path):
                for _ in self.generate_cpu_range():
                    self.format_command(unique_item=unique_item)
        except Exception as err: #TODO add exception
            for _ in self.generate_cpu_range():
                self.format_command()
            raise err

    def generate_cpu_range(self):
        """Changes the self.cpus class var and yields nothing"""

        for ncpu in range(self.cpus, self.upper):
            self.cpus = ncpu
            yield
