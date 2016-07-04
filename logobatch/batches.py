"""
This file contains the batch classes
"""

import os
import sys
import re

from datetime import datetime

sys.path.append("..")
from logobatch.email_notice import Email

class NoSlurmTemplateError(Exception):
    """Error when no batchfile is found"""
    def __init__(self, message):
        super(NoSlurmTemplateError, self).__init__(message)

class InvalidExecutableError(Exception):
    """Error thrown when executable doesn't exist"""
    def __init__(self, message):
        super(InvalidExecutableError, self).__init__(message)

class NoInputsError(Exception):
    """Error when no input sources are found"""
    def __init__(self, message):
        super(NoInputsError, self).__init__(message)

class InvalidBatchTypeError(Exception):
    """Error thrown when batch type isn't supported"""
    def __init__(self, message):
        super(InvalidBatchTypeError, self).__init__(message)

class MissingAttributeError(Exception):
    """Error thrown when batch type isn't supported"""
    def __init__(self, message):
        super(MissingAttributeError, self).__init__(message)


class Batch(object):
    """
    Base class for analysis and threadtest
    TODO:
        get rid of yaml_data!!! Get it its vairables into class attributes
    """

    type_names = {}

    def __new__(cls, **kwds):
        """Creates and returns proper batch type"""
        batch_type = kwds.get('batch_type', 'local')
        if batch_type in cls.type_names: return super(Batch, cls).__new__(cls, **kwds)
        for sub_cls in cls.__subclasses__():
            if batch_type in sub_cls.type_names:
                return super(Batch, cls).__new__(sub_cls)
        raise InvalidBatchTypeError("bad batch type: {}".format(batch_type)) #TDDO: Add message

    def __init__(self, **kwds):
        """ """
        self.command_base = kwds.get('command', None) #Required
        if self.command_base is None: raise MissingAttributeError("Missing command")

        self.executable = kwds.get('executable', '')
        self.batch_base = kwds.get('batch_base', '.')
        self.name = kwds.get('name', str(datetime.now()).replace(' ', '-'))
        #TODO add check and warning if data will be overwritten
        self.output = kwds.get('batch_base', os.path.join(self.batch_base, self.name))
        self.inputs = kwds.get('inputs', None)
        self.email = kwds.get('email', False)
        self.cpus = kwds.get('cpus', 1)

        if re.match(r'\{i[0-9]+\}', self.command_base) and self.inputs is None:
            raise NoinputsFileFoundError(("No 'inputs' file was specifed in your"
                                          " yaml object but {inputs} was found"
                                          " in your command"))

    def build_inputs_path(self, inputs):
        """
        Builds a path for the inputs file
        Throws an error if inputs path isn't valid
        """

        inserts = {}
        if '{mod}' in inputs:
            inserts["mod"] = self.batch_base
        if '{in}' in inputs:
            inserts["in"] = os.path.join(self.batch_base, 'in')
        inputs = inputs.format(**inserts)

        if not os.path.isfile(inputs):
            raise NoInputsFileFoundError("message goes here") #TODO add message

        return inputs


    def format_command(self, inputs_item=None):
        """
        Formats a command from the base command with class variables
        and adds them the the batches' command list
        """

        inserts = {}
        inputs = set(re.findall(r'\{i[0-9]*\}', self.command_base))
        other = set(re.findall(r'\{.+\}', self.command_base)) - inputs
        #TODO left off here.

        if '{exe}' in self.command_base:
            inserts["exe"] = self.executable
        if '{out}' in self.command_base:
            inserts["out"] = '{out}'
        if '{mod}' in self.command_base:
            inserts["mod"] = self.batch_base

        if '{in}' in self.command_base:
            inserts["in"] = os.path.join(self.batch_base, 'in')
        if '{inputs}' in self.command_base:
            inserts["inputs"] = inputs_item

        if '{cpus}' in self.command_base:
            inserts["cpus"] = self.cpus

        self.commands.append(self.command_base.format(**inserts))

    @staticmethod
    def generate_inputs(inputs_path):
        """Opens a file with inputs entries and yields them"""
        #TODO Possibly make this use the class variable

        with open(inputs_path, "r") as uni:
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
    """ A Batch object with inputs command parameters"""

    type_names = {'slurm'}
    def __init__(self, **kwds):
        """Init fucntion adds the sets the cpu number"""
        super().__init__(**kwds)

    # BEGIN Implemented Virtual Methods vvvvvvvvvvvvvvvvvv
    def create_commands(self):
        """Creates and adds commands with the format_command method"""

        for inputs_item in self.generate_inputs(self.inputs_path):
            self.format_command(inputs_item=inputs_item)

    def launch_batch(self):
        self.create_commands()
        self.create_job_file("""...""")
        self.schedule_batch()

    # END Implemented Virtual Methods ^^^^^^^^^^^^^^^^^^

    def create_job_file(self, ntasks, email_info, run_name):
        """
        Creates job files from the batches' command list
        also populates the job_files list

        TODO:
            REFACTOR!
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

class NoHostNameError(Exception):
    """Error for when no hostnames are passed into SshBatch"""
    def __init__(self, message):
        super(NoHostNameError, self).__init__(message)

class SshBatch(Batch):
    """
    TODO:
        Possibly add a ~/.logobatch file which is read for
            hostnames if not specified in bbfile.yml
    """

    type_names = {'ssh'}
    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.command_number = kwds.get('command_number', 1)
        self.hostnames = kwds.get('hostnames', None) #Required
        if isinstance(self.hostnames, str): self.hostnames = [self.hostnames]
        elif self.hostnames is None: raise NoHostNameError("") #TODO Message
        elif not isinstance(self.hostnames, list): raise TypeError()

    def create_commands(self, command_number=None):
        """Creates command to be sent over ssh"""
        if command_number is None:
            try: command_number = self.command_number
            except AttributeError: command_number = 1

        raw_commands = []
        for inputs_item in self.generate_inputs():
            raw_commands.append(self.format_command(inputs_item))

        commands = []
        for i in range(0, len(tmp_commands), command_number):
            command_set = raw_commands[i:i+command_number]
            commands.append('({})&'.format('; '.join(command_set)))

        return compound_commands

    def launch_batch(self):
        """Launches batch over SSH"""
        compound_commands = self.create_commands(self.command_number)

class ThreadTest(Batch):
    """
    A batch object that is used to run identical commands with
    a different numbers of CPUs or threads within a specified range

    This Batch obejct is intended to figure out where the point of
    deminishing returns related to the number of alloacted threads

    Thread test objects can use also run thread test ranges
    with inputs parameters
    """

    type_names = {'threadtest'}
    def __init__(self, **kwds):
        """
        Sets the self.upper class var
        sets the self.cpus class var as lower. This is done to allow
        ThreadTest batches to use the format_command method
        """

        super().__init__(**kwds)
        self.upper = kwds.get('upper', raise_invalid_attribute(""))
        self.cpus = kwds.get('lower', 1)

    def create_commands(self):
        """Creats and adds commands to the batch"""

        try:
            for inputs_item in self.generate_inputs(self.inputs_path):
                for _ in self.generate_cpu_range():
                    self.format_command(inputs_item=inputs_item)
        except Exception as err: #TODO add exception
            for _ in self.generate_cpu_range():
                self.format_command()
            raise err

    def generate_cpu_range(self):
        """Changes the self.cpus class var and yields nothing"""

        for ncpu in range(self.cpus, self.upper):
            self.cpus = ncpu
            yield

class LocalBatch(Batch):
    """ """
    type_names = {'local'}
    def __init__(self, **kwds):
        super().__init__(**kwds)

    def launch_batch(self):
        raise NotImplementedError
