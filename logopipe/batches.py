"""
This file contains the batch classes
"""

import os
import sys
M
sys.path.append("..")

from logo_exceptions import NoUniqueFileFoundError, InvalidExecutableError, BatchTemplateFileNotFoundError
from email_notice import Email

class Batch:
    """Base class for analysis and threadtest"""

    def __init__(self, yaml_data, model_path, out_path=None):
        """Init method attempts to build output and unquie paths"""

        self.commands = []
        self.job_files = []

        self.name = yaml_data['name']
        self.command_base = yaml_data['command']
        self.model_path = model_path
        self.cpus = 1

        if '{unique}' in self.command_base:
            try:
                self.unique_path = self.build_unique_path(yaml_data['unique'])
            except KeyError:
                raise NoUniqueFileFoundError("No 'unique' file was specifed in your yaml object but {unique} was found in your command")
        else:
            self.unique_path = None

        try:
            self.email = yaml_data["email"]
        except KeyError:
            self.email = False

        if out_path is None:
            self.out_path = os.path.join(model_path, "out", self.name)
        else:
            self.out_path = os.path.join(out_path, self.name)

        self.executable = yaml_data['exe']
        if not (os.path.isfile(self.executable) and os.access(self.executable, os.X_OK)):
            raise InvalidExecutableError("Error Executable {} is was not found. Aborting job".format(self.executable)) 
        #TODO add case for command in path

    def create_commands(self):
        """
        Virtual method that, when implemented, will create the
        commands for the batch
        """

        raise NotImplementedError()

    def build_unique_path(self, unique):
        """
        Builds a path for the unique file
        Throws an error if unique path isn't valid
        """

        inserts = {}
        if '{mod}' in unique:
            inserts["mod"] = self.model_path
        if '{in}' in unique:
            inserts["in"] = os.path.join(self.model_path, 'in')
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
            inserts["mod"] = self.model_path

        if '{in}' in self.command_base:
            inserts["in"] = os.path.join(self.model_path, 'in')
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
            job_name = "{name}-job-{count}".format(name=self.name, count=file_count)
            job_out_path = os.path.join(self.out_path, job_name)
            print(job_out_path)

            slurm_file = "{job_name}-%j.out".format(job_name=job_name)
            slurm_file_path = os.path.join(job_out_path, slurm_file)

            job_file_path = os.path.join(job_out_path, ".".join([job_name, "sh"]))
            self.job_files.append(job_file_path)

            try:
                os.makedirs(job_out_path)
            except FileExistsError:
                pass

            with open(job_file_path, 'w') as bfile:
                #Write Slurm settings to slurm batch file #############################
                for line in template: #Write Template file
                    bfile.write(line) #

                #Write automated parameters to file
                bfile.write("#SBATCH -J {analysis}\n".format(analysis=self.name))
                bfile.write("#SBATCH --cpus-per-task={cpus}\n".format(cpus=self.cpus))
                bfile.write("#SBATCH -o {slurm_file}\n".format(slurm_file=slurm_file_path))

                #Write commands#########################################################
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

                #Write email commands ####################################################
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
        paths = [os.path.join(self.model_path, 'in', 'btemplate.sh'),
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


class Analysis(Batch):
    """ A Batch object with unique command parameters"""

    def __init__(self, yaml_data, model_path, out_path=None):
        """Init fucntion adds the sets the cpu number"""
        #TODO Possibly implement a default cpu number here

        super().__init__(yaml_data, model_path, out_path)
        try:
            self.cpus = yaml_data['cpus']
        except KeyError:
            self.cpus = 1

    def create_commands(self):
        """Creates and adds commands with the format_command method"""

        for unique_item in self.generate_unique(self.unique_path):
            self.format_command(unique_item=unique_item)

class ThreadTest(Batch):
    """
    A batch object that is used to run identical commands with
    a different numbers of CPUs or threads within a specified range

    This Batch obejct is intended to figure out where the point of
    deminishing returns related to the number of alloacted threads

    Thread test objects can use also run thread test ranges with unique parameters
    """

    def __init__(self, yaml_data, model_path, out_path=None):
        """
        Sets the self.upper class var
        sets the self.cpus class var as lower. This is done to allow
        ThreadTest batches to use the format_command method
        """

        super().__init__(yaml_data, model_path, out_path)
        self.upper = yaml_data['upper']
        self.cpus = yaml_data['lower']

    def create_commands(self):
        """Creats and adds commands to the batch"""

        try:
            for unique_item in self.generate_unique(self.unique_path):
                for _ in self.generate_cpu_range():
                    self.format_command(unique_item=unique_item)
        except: #TODO add exception
            for _ in self.generate_cpu_range():
                self.format_command()

    def generate_cpu_range(self):
        """Changes the self.cpus class var and yields nothing"""

        for ncpu in range(self.cpus, self.upper):
            self.cpus = ncpu
            yield


