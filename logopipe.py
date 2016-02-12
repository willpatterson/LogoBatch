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

class Run:
    def __init__(self,
                 name,
                 model_path,
                 ntasks=1,
                 output_path=None,
                 yaml_path=None):

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
    def read_batches(self):
        for yaml_path in self.yaml_paths:
            #TODO catch incorrect yml format error here
            self.read_yaml_file(yaml_path)

    def read_yaml_file(self, yaml_path):
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
        for batch in self.batches:
            batch.create_job_files(self.ntasks)


class Batch:
    """Base class for analysis and threadtest"""

    def __init__(self, yaml_data, model_path, out_path=None):
        commands = []
        job_files = []

        self.name = yaml_data['name']
        self.command_base = yaml_data['command']
        self.unique = yaml_data['unique']
        self.model_path = model_path
        self.cpus = 1

        if out_path is None:
            self.out_path = os.path.join(model_path, "out", self.name)
        else:
            self.out_path = os.path.join(out_path, self.name)

        self.executable = yaml_data['exe']
        if not (os.path.isfile(fpath) and os.access(fpath, os.X_OK)):
            raise InvalidExecutableError("") #TODO add message

    def create_commands(self):
        raise NotImplementedError()

    def format_command(self, unique_item):
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
        with open(unique_path, "r") as uni:
            for line in uni:
                yield line.split(",")[0].replace("\n", "")

    def create_job_file(self, ntasks)
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
        return os.path.join(self.model_path, 'in')

class Analysis(Batch):
    def __init__(self, yaml_data, model_path, out_path=None):
        super().__init__(yaml_data, model_path, out_path)
        self.cpus = yaml_data['cpus']

    def create_commands(self, model_path, unique_path)
        for unique_item in self.generate_unique(unique_path):
            self.format_command(model_path, unique_item)

class ThreadTest(Batch):
    def __init__(self, yaml_data, model_path, out_path=None):
        super().__init__(yaml_data, model_path, out_path)
        self.upper = yaml_data['upper']
        self.cpus = yaml_data['lower']

    def create_commands(self, unique_path):
        for unique_item in self.generate_unique(unique_path):
            for ncpu in range(self.lower, self.upper):
                self.cpus = ncpu
                self.format_command(model_path, unique_item)


def schedule_jobs(command_data):
    """Schedules all of the batch files created in slurm"""

    for analysis in command_data:
        print(analysis["job_dir"])
        jobs = os.listdir(analysis["job_dir"])
        jobs = [os.path.join(analysis["job_dir"], x) for x in jobs]

        for job in jobs:
            os.system("sbatch {}".format(job))


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
    args = get_args()
    command_data = create_commands(args.model_path, args.run_name)
    command_data = create_job_files(command_data, args.model_path, args.ntasks, args.run_name)
    schedule_jobs(command_data)

def main_new():
    args = get_args()
    run = build_run_type(args.model_path,
                         args.run_name,
                         outpath_base=args.output_path,
                         yaml_path=args.yaml_path)
    run = create_commands_new(run)
    run = create_job_files_new(run)
    schedule_jobs_new(run)


if __name__ == "__main__":
    main()


#OLD########################

def build_run_type(run_name, model_path, ntasks, outpath_base=None, yaml_path=None):
    #create namedtuple containding batch data model path and run name
    Run = namedtuple('Run', ['run_name', 'model_path', 'ntasks', 'batch_data'])
    Analysis = namedtuple('Analysis', ['outpath', 'commands', 'analysis_data'])

    if yaml_path is None:
        batch_data = search_model_dir(model_path)
    else:
        batch_data = read_yaml(yaml_path)

    for _, analysis_type in batch_data.items():
        for name, analysis in analysis_type.itmes():
            if outpath_base is None:
                outpath = os.path.join(model_path, 'out', run_name, name)
            else:
                outpath = os.path.join(outpath_base, run_name, name)

            analysis = Analysis(outpath=outpath,
                                commands=[],
                                analysis_data=analysis)

    currrent_run = Run(run_name=run_name,
                       model_path=model_path,
                       ntasks=ntasks,
                       batch_data=batch_data)

    return currrent_run

def create_job_files(command_data, model_path, ntasks, run_name):
    """Creats sbatch files and puts them in their own folder"""
    template = ""
    with open("btemplate.sh", "r") as btemplate:
        template = btemplate.readlines()

    for analysis in command_data:
        analysis["job_dir"] = os.path.join(analysis['out_path'], 'jobs')
        slurm_dir = os.path.join(analysis['out_path'], 'slurm')
        try:
            os.makedirs(analysis["job_dir"])
            os.makedirs(slurm_dir)
        except FileExistsError:
            pass

        file_count = 0
        for count, com in enumerate(analysis["commands"]):
            if count % ntasks == 0:
                file_count += 1
                job_name = "{name}-job-{count}".format(name=analysis["name"], count=file_count)

                with open(os.path.join(analysis["job_dir"], ".".join([job_name, "sh"])), 'w') as bfile:
                    for line in template: #Write Template file
                        bfile.write(line) #

                    #Write automated parameters to file
                    bfile.write("#SBATCH -J {analysis}\n".format(analysis=analysis["name"]))
                    bfile.write("#SBATCH --cpus-per-task={cpus}\n".format(cpus=analysis["cpus"]))
                    bfile.write("#SBATCH -o {slurm}/{job_name}-%j.out\n".format(slurm=slurm_dir,
                                                                             job_name=job_name))
            #Clean up job name string formatting when files are opened
            with open(os.path.join(analysis["job_dir"], "{}-job-{}.sh".format(analysis["name"],
                                                                  file_count)), 'a') as bfile:
                bfile.write(com + '\n')
                print(com)

    return command_data

def create_commands(model_path, run_name):
    """opens yaml file from model directory and uses it to create ommands for slurm"""
    in_path = os.path.join(model_path, "in")

    in_files = os.listdir(in_path)
    in_files = [os.path.join(in_path, infile) for infile in in_files]

    yaml_files = [infile for infile in in_files if infile.endswith(".yml")]

    with open(yaml_files[0], 'r') as yfile:
        ydata = yaml.load(yfile)

    command_data = []
    for analysis in ydata:
        try:
            if analysis["analysis"]["enabled"] is True:
                command_data.append(analysis["analysis"])
        except: #FIX this
            pass

    for analysis in command_data:
        analysis["out_path"] = os.path.join(model_path, 'out', run_name, analysis["name"])
        unique_path = os.path.join(in_path, analysis["unique"])
        commands = []
        with open(unique_path, "r") as uni:
            for count, line in enumerate(uni):
                unique = line.split(",")[0].replace("\n", "")
                command = analysis["command"]
                inserts = {}
                if '{exe}' in command:
                    inserts["exe"] = analysis["exe"]
                if '{cpus}' in command:
                    inserts["cpus"] = analysis["cpus"]
                if '{out}' in command:
                    inserts["out"] = analysis["out_path"]
                if '{mod}' in command:
                    inserts["mod"] = model_path
                if '{unique}' in command:
                    inserts["unique"] = unique
                command = command.format(**inserts)

                commands.append(command)
        analysis["commands"] = commands

    return command_data


