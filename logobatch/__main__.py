"""Command line interface for logobatch"""

import argparse

import os
import sys

sys.path.append(os.path.abspath('..'))

from logobatch.logobatch import BatchManager


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

