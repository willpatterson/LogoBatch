"""
Author: William Patterson
"""

import yaml
import argparse
import datetime
from collections import namedtuple

import os, sys
sys.path.append("..")

from email_notice import Email

class InvalidExecutableError(Exception):
    """Error thrown when executable doesn't exist"""
    def __init__(self, message):
        super(InvalidExecutableError, self).__init__(message)

class InvalidBatchTypeError(Exception):
    """Error thrown when batch type isn't supported"""
    def __init__(self, message):
        super(InvalidBatchTypeError, self).__init__(message)

class InvalidYAMLFormatError(Exception):
    """Error thrown when yaml format is incorrect"""
    def __init__(self, message):
        super(InvalidYAMLFormatError, self).__init__(message)

class NoUniqueFileFoundError(Exception):
    """Error when no unique file can be found"""
    def __init__(self, message):
        super(NoUniqueFileFoundError, self).__init__(message)

class Run:
    """
    The run class contains and manages all Batch objects

    The Run class is responsible for:
       - parsing yaml files
       - creating Batch objects from yaml data
       - setting the base output path
       - building Batch objects
       - running Batch objects
    """

    def __init__(self,
                 name,
                 model_path,
                 ntasks=1,
                 out_path=None,
                 yaml_path=None):
        """Initalizes all class variables for run"""

        self.name = name
        self.model_path = model_path
        self.ntasks = ntasks

        if out_path is None:
            self.out_path = os.path.join(self.model_path, 'out', self.name)
        else:
            self.out_path = os.path.join(out_path, self.name)

        if yaml_path is None:
            self.yaml_paths = self._get_yaml_files()
        else:
            self.yaml_paths = [yaml_path]

        self.batches = []
        self.email_info = {}

    #vvvvvvvvvvvvvvv Yaml file input Parsing vvvvvvvvvvvvvvvvvvvvvvvvvv
    def create_batches(self):
        """Reads all yaml files into the Batch objects"""

        for yaml_path in self.yaml_paths:
            #TODO catch incorrect yml format error here
            self.read_yaml_file(yaml_path)

    def read_yaml_file(self, yaml_path):
        """
        Reads a single yaml file into the Run object
         - Opens yaml file
         - catches errors when creating a batch object
        """

        with open(yaml_path, 'r') as yfile:
            raw_ydata = yaml.load(yfile)

        #Converts yaml nested dictionaries into namedtuples
        YmlObj = namedtuple('YmlObj', ['name', 'data'])
        ydata = []
        for y_obj in raw_ydata:
            try:
                if not (len(y_obj.keys()) > 1):
                    for key in y_obj.keys():
                        name = key
                    ydata.append(YmlObj(name=name, data=y_obj[name]))
                else:
                    print("Error: Invalid object format.. to many object names. Skipping")
            except AttributeError:
                print("Error: Invalid object format.. object not a dictionary. Sikpping")

        #TODO catch incorrect yml format error here
        for y_obj in ydata:
            try:
                if y_obj == "email":
                    self.email_info = y_obj.data
                else:
                    self.add_batch(y_obj)

            except InvalidBatchTypeError:
                print("Error: Object type {otype} is invalid. Object ignored".format(otype=y_obj.name))
            except InvalidExecutableError:
                print("Error: Executable {exe} is invalid. Batch {bn} ignored".format(exe=y_obj.data["exe"],
                                                                                      bn=y_obj.name))

    def add_batch(self, batch):
        """
        Creates and the correct Batch object and adds it to the batch list
        throws errors caught by read_yaml_file if format is not correct
        """
        try:
            add_flag = batch.data["enabled"]
        except KeyError:
            add_flag = True

        if add_flag is True:
            if batch.name == 'analysis':
                batch = Analysis(batch.data, self.model_path, out_path=self.out_path)
            elif batch.name == 'thread_test':
                batch = ThreadTest(batch.data, self.model_path, out_path=self.out_path)
            else:
                raise InvalidBatchTypeError("Batch type {btype} is invalid".format(btype=batch.name))

            self.batches.append(batch)
        else:
            print("Ignoring: {name}".format(name=batch.name))

    def add_email_info(self, email_obj):
        try:
            if isinstance(email_obj, dict) is True:
                if isinstance(email_obj["email"], dict) is True:
                    if isinstance(email_obj["email"]["addresses"], list) is True:
                        pass
        except:
            pass

    def _get_yaml_files(self):
        """Gets all yaml files from a directory"""

        in_path = os.path.join(self.model_path, "in")
        in_files = os.listdir(in_path)
        in_files = [os.path.join(in_path, infile) for infile in in_files]

        return [infile for infile in in_files if infile.endswith(".yml")]

    #^^^^^^^^^^^^^^^^^^ Yaml file input Parsing ^^^^^^^^^^^^^^^^^^^^^^^^^

    #vvvvvvvvvvvvvvvvvvvvvvvvvv PipeLining vvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def create_commands(self):
        """Triggers batch objects to create their commands"""

        for batch in self.batches:
            batch.create_commands()

    def create_slurm_jobs(self):
        """Triggers Batch objects to create their job files"""

        for batch in self.batches:
            batch.create_job_files(self.ntasks, self.email_info)

    def schedule_batches(self):
        """Triggers Batch objects to schedule their job files"""

        for batch in self.batches:
            batch.schedule_batch()


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
            raise InvalidExecutableError("") #TODO add message
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
        if '{in}' in self.unique_path:
            inserts["in"] = os.path.join(self.model_path, 'in')
        unique = unique.format(**inserts)

        if not os.path.isfile(self.unique_path):
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
        #if '{out}' in self.command_base:
            #inserts["out"] = self.out_path
        if '{mod}' in self.command_base:
            inserts["mod"] = self.model_path

        if '{in}' in self.command_base:
            inserts["in"] = os.path.join(self.model_path, 'in')
        if '{unique}' in self.command_base:
            inserts["unique"] = unique_item

        if '{cpus}' in self.command_base:
            inserts["cpus"] = self.cpus

        self.commands.append(self.command_base.format(**inserts))

    def generate_unique(self, unique_path):
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
        #TODO Break this function up

        template = ""
        with open("btemplate.sh", "r") as btemplate: #TODO implement different template options
            template = btemplate.readlines()

        job_dir = os.path.join(self.out_path, 'jobs')
        slurm_dir = os.path.join(self.out_path, 'slurm')
        try:
            os.makedirs(job_dir)
            os.makedirs(slurm_dir)
        except FileExistsError:
            pass

        file_count = 0
        for count, com in enumerate(self.commands):
            if count % ntasks == 0:
                file_count += 1

                #Adds email lines
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
                    try:
                        with open(job_file, 'a') as jfile:
                            for email_obj in email_objs:
                                jfile.write(generate_email_command() + '\n')
                    except: #TODO fix
                        pass

                job_name = "{name}-job-{count}".format(name=self.name, count=file_count)
                job_out_path = os.path.join(self.out_path, job_name)

                slurm_file = "{job_name}-%j.out".format(job_name=job_name)
                slurm_file_path = os.path.join(job_out_path, slurm_file)

                job_file_path = os.path.join(job_out_path, ".".join([job_name, "sh"]))
                self.job_files.append(job_file_path)

                with open(job_file_path, 'w') as bfile:
                    for line in template: #Write Template file
                        bfile.write(line) #

                    #Write automated parameters to file
                    bfile.write("#SBATCH -J {analysis}\n".format(analysis=self.name))
                    bfile.write("#SBATCH --cpus-per-task={cpus}\n".format(cpus=self.cpus))
                    bfile.write("#SBATCH -o {slurm_file}\n".format(slurm_file=slurm_file_path))

            #Clean up job name string formatting when files are opened
            with open(job_file_path, 'a') as bfile:
                if '{out}' in com:
                    com = com.format(out=job_file_path)
                bfile.write(com + '\n')
                print(com)

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
                for _ in generate_cpu_range():
                    self.format_command(unique_item=unique_item)
        except: #TODO add exception
            for _ in self.generate_cpu_range():
                self.format_command()

    def generate_cpu_range(self):
        """Changes the self.cpus class var and yields nothing"""

        for ncpu in range(self.cpus, self.upper):
            self.cpus = ncpu
            yield


def get_args():
    """Get arguments"""

    #TODO add defaults to help outputs
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-m",
                        "--model_path",
                        type=str,
                        default=os.getcwd(),
                        help="Directory containing models")
    parser.add_argument("-n",
                        "--ntasks",
                        type=int,
                        default=1,
                        help="Number of tasks per slurm file")
    parser.add_argument("-r",
                        "--run_name",
                        type=str,
                        default=str(datetime.datetime.now().time()).replace(":", "-"),
                        help="Name of the batch run")
    parser.add_argument("-y",
                        "--yaml_path",
                        type=str,
                        default=None,
                        help="Specify an input path file outside of the model directory")
    parser.add_argument("-o",
                        "--output_path",
                        default=None,
                        help="Specify where to save output")

    return parser.parse_args()


def main():
    args = get_args()
    run = Run(args.run_name,
              args.model_path,
              ntasks=args.ntasks,
              yaml_path=args.yaml_path,
              out_path=args.output_path)

    run.create_batches()
    run.create_commands()
    run.create_slurm_jobs()
    run.schedule_batches()

if __name__ == "__main__":
    main()

