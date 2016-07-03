"""
Author: William Patterson
"""

import yaml
import argparse
import datetime
from collections import namedtuple

import os, sys
sys.path.append(os.path.abspath(".."))

from logopipe.batches import ThreadTest, Analysis
from logopipe.logo_exceptions import InvalidBatchTypeError, InvalidExecutableError

class LogoPipe:
    """
    The LogoPipe class contains and manages all Batch objects

    LogoPipe is responsible for:
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
        """Initalizes all attributes LogoPipe"""

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
                if y_obj.name == "email":
                    self.email_info = y_obj.data
                else:
                    self.add_batch(y_obj)

            except InvalidBatchTypeError:
                print("Error: Object type {otype} is invalid. Object ignored".format(otype=y_obj.name))
            except InvalidExecutableError:
                print("Error: Executable {exe} is invalid. Batch {bn} ignored".format(exe=y_obj.data["exe"],
                                                                                      bn=y_obj.data["name"]))

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
            if batch.name == 'slurm_batch':
                batch = SlurmBatch(batch.data, self.model_path, out_path=self.out_path)
            elif batch.name == 'ssh_batch':
                batch = SshBatch(batch.data, self.model_path, out_path=self.out_path)
            elif batch.name == 'thread_test':
                batch = ThreadTest(batch.data, self.model_path, out_path=self.out_path)
            else:
                raise InvalidBatchTypeError("Batch type {btype} is invalid".format(btype=batch.name))

            self.batches.append(batch)
        else:
            print("Ignoring: {name}".format(name=batch.name))

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
            batch.create_job_file(self.ntasks, self.email_info, self.name)

    def schedule_batches(self):
        """Triggers Batch objects to schedule their job files"""

        for batch in self.batches:
            batch.schedule_batch()


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
    pipe = LogoPipe(args.run_name,
                    args.model_path,
                    ntasks=args.ntasks,
                    yaml_path=args.yaml_path,
                    out_path=args.output_path)

    pipe.create_batches()
    pipe.create_commands()
    pipe.create_slurm_jobs()
    pipe.schedule_batches()

if __name__ == "__main__":
    main()

