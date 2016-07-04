"""
Author: William Patterson
"""

import yaml
import argparse
import datetime
from collections import namedtuple

import os, sys
sys.path.append(os.path.abspath(".."))

from logobatch.batches import Batch

class NoBatchesError(Exception):
    """Error when no batches are found in a bbatch file"""
    def __init__(self, message):
        super(NoBatchesError, self).__init__(message)

class BBatchFormatError(Exception):
    """Error thrown when yaml format is incorrect"""
    def __init__(self, message):
        super(BBatchFormatError, self).__init__(message)


class BatchManager:
    """
    The BatchManager class contains and manages all Batch objects

    BatchManager is responsible for:
       - parsing yaml files
       - creating Batch objects from yaml data
       - setting the base output path
       - building Batch objects
       - running Batch objects
    """

    def __init__(self, bbatch, outpath=None):
        """Initalizes all attributes """

        self.batches, self.addresses = self.parse_bbatch(bbatch)

    @staticmethod
    def parse_bbatch(bbatch):
        """ reads bbatch yaml file into batches """

        BBatchData = namedtuple('BBatchData', ['batches', 'addresses'])
        def raise_no_batch_error():
            message = "Error: No batches were found in {}".format(bbatch)
            raise NoBatchesError(message)

        with open(bbatch, 'r') as yfile:
            ydata = yaml.load(yfile)

        print(ydata["Batches"])
        batches = ydata.get('Batches', None)
        if not isinstance(batches, list): raise BBatchFormatError("") #TODO add message
        batches = [Batch(**batch) for batch in batches if batch.get('enabled',
                                                                    False)]
        addresses = ydata.get('Email', None).get('addresses', None)

        return BBatchData(batches, addresses)


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
    bm = BatchManager(args.run_name,
                      args.model_path,
                      ntasks=args.ntasks,
                      yaml_path=args.yaml_path,
                      out_path=args.output_path)

    bm.create_batches()
    bm.create_commands()
    bm.create_slurm_jobs()
    bm.schedule_batches()

if __name__ == "__main__":
    main()

