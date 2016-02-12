import os
import yaml
import argparse
import datetime
from collections import namedtuple

class InvalidExecutableError(Exception):
    """Error thrown when executable doesn't exist"""
    def __init__(self, message):
        super(InvalidExecutableError, self).__init__(message)

class InvalidBatchTypeError(Exception):
    """Error thrown when batch type isn't supported"""
    def __init__(self, message):
        super(InvalidBatchTypeError, self).__init__(message)

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
                 output_path=None,
                 yaml_path=None):
        """Initalizes all class variables for run"""

        self.name = name
        self.model_path = model_path
        self.ntasks = ntasks

        if output_path is None:
            self.output_path = os.path.join(self.model_path, 'out', self.name)
        else:
            self.output_path = os.path.join(output_path, self.name)

        if yaml_path is None:
            self.yaml_paths = self._get_yaml_files()
        else:
            self.yaml_paths = [yaml_path]

        self.batches = []

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
            ydata = yaml.load(yfile)

        #TODO catch incorrect yml format error here
        for batch in ydata:
            try:
                self.add_batch(batch)
            except InvalidBatchTypeError:
                btype = batch.keys()[0]
                bname = batch[btype]['name']
                print("Error: Batch type {bt} is invalid. Batch {bn} ignored".format(bt=btype,
                                                                                     bn=bname))
            except InvalidExecutableError:
                btype = batch.keys()[0]
                bname = batch[btype]['name']
                exe = batch[btype]['exe']
                print("Error: Executable {exe} is invalid. Batch {bn} ignored".format(exe=exe,
                                                                                      bn=bname))

    def add_batch(self, batch):
        """
        Creates and the correct Batch object and adds it to the batch list
        throws errors caught by read_yaml_file if format is not correct
        """

        btype = batch.keys()[0]
        if batch[btype]["enabled"] is True:
            if btype == 'analysis':
                batch = Analysis(batch[btype], model_path, out_path=self.out_path)
            elif btype == 'thread_test':
                batch = ThreadTest(batch[btype], model_path, out_path=self.out_path)
            else:
                raise InvalidBatchTypeError("Batch type {btype} is invalid".format(btype))

            self.batches.append(batch)

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
            batch.create_job_files(self.ntasks)

    def schedule_batches(self):
        """Triggers Batch objects to schedule their job files"""

        for batch in self.batches:
            batch.schedule_batch()


class Batch:
    """Base class for analysis and threadtest"""

    def __init__(self, yaml_data, model_path, out_path=None):
        """Init method attempts to build output and unquie paths"""

        commands = []
        job_files = []

        self.name = yaml_data['name']
        self.command_base = yaml_data['command']
        self.model_path = model_path
        self.cpus = 1

        try:
            self.unique_path = self.build_unique_path(yaml_data['unique'])
        except KeyError:
            self.unique_path = None

        if out_path is None:
            self.out_path = os.path.join(model_path, "out", self.name)
        else:
            self.out_path = os.path.join(out_path, self.name)

        self.executable = yaml_data['exe']
        if not (os.path.isfile(fpath) and os.access(fpath, os.X_OK)):
            raise InvalidExecutableError("") #TODO add message

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
        if '{in}' in self.unique:
            inserts["in"] = self.make_in()
        unique = unique.format(**inserts)

        if not os.path.isfile(self.unique):
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
            inserts["out"] = self.out_path
        if '{mod}' in self.command_base:
            inserts["mod"] = self.model_path

        if '{in}' in self.command_base:
            inserts["in"] = self.make_in()
        if '{unique}' in self.command_base:
            inserts["unique"] = unique_item

        if '{cpus}' in self.command_base:
            inserts["cpus"] = self.cpus

         commands.append(command_base.format(**inserts))

    def generate_unique(self, unique_path):
        """Opens a file with unique entries and yields them"""
        #TODO Possibly make this use the class variable

        with open(unique_path, "r") as uni:
            for line in uni:
                yield line.split(",")[0].replace("\n", "")

    def create_job_file(self, ntasks):
        """
        Creates job files from the batches' command list
        also populates the job_files list
        """

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
                job_name = "{name}-job-{count}".format(name=self.name, count=file_count)
                job_file = os.path.join(job_dir, ".".join([job_name, "sh"]))
                self.job_files.append(job_file)

                with open(job_file, 'w') as bfile:
                    for line in template: #Write Template file
                        bfile.write(line) #

                    #Write automated parameters to file
                    bfile.write("#SBATCH -J {analysis}\n".format(analysis=self.name))
                    bfile.write("#SBATCH --cpus-per-task={cpus}\n".format(cpus=self.cpus))
                    bfile.write("#SBATCH -o {slurm}/{job_name}-%j.out\n".format(slurm=slurm_dir,
                                                                                job_name=job_name))
            #Clean up job name string formatting when files are opened
            with open(job_file, 'a') as bfile:
                bfile.write(com + '\n')
                print(com)

    #Might not need this
    def make_in(self):
        """
        Returns standard 'in' directory.
        this is used to reduce data redundency within the batches
        """

        return os.path.join(self.model_path, 'in')

    def schedule_batch(self):
        """Schedules the batches' job files in slurm"""

        for job_file in self.job_files:
            os.system("sbatch {}".format(job_files))

class Analysis(Batch):
    """ A Batch object with unique command parameters"""

    def __init__(self, yaml_data, model_path, out_path=None):
        """Init fucntion adds the sets the cpu number"""
        #TODO Possibly implement a default cpu number here

        super().__init__(yaml_data, model_path, out_path)
        self.cpus = yaml_data['cpus']

    def create_commands(self):
        """Creates and adds commands with the format_command method"""

        for unique_item in self.generate_unique(self.unique_path):
            self.format_command(self.model_path, unique_item)

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
            for _ in generate_cpu_range():
                self.format_command()

    def generate_cpu_range():
        """Changes the self.cpus class var and yields nothing"""

        for ncpu in range(self.cpus, self.upper):
            self.cpus = ncpu
            yield


def get_args():
    """Get arguments"""

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
    parser.add_argument("-i",
                        "--input_path",
                        type=str,
                        default=None
                        help="Specify an input path file outside of the model directory")
    parser.add_argument("-o",
                        "--output_path",
                        default=None,
                        help="Specify where to save output")

    return parser.parse_args()


def main():
    pass

if __name__ == "__main__":
    main()

