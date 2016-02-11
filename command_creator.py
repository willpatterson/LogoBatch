import os
import yaml
import argparse
import datetime
from collections import namedtuple

def read_yaml(yaml_path, batches={}):
    with open(yaml_path, 'r') as yfile:
        ydata = yaml.load(yfile)

    for batch in ydata:
        btype = batch.keys()[0]
        if batch[btype]["enabled"] is True:
            if btype == 'analysis':
                try:
                    batches['analysis'] = [batch["analysis"]]
                except: #fix this
                    batches['analysis'].append(batch['analysis'])
            elif btype == 'thread_test':
                 try:
                    batches['thread_test'] = [batch["thread_test"]]
                 except: #fix this
                    batches['thread_test'].append(batch['thread_test'])
            else:
                print('Unrecogized batch type: "{}"'.format(btype))

            batches.append(analysis[y_object_name])

    return batches

def search_model_dir(model_path):
    in_path = os.path.join(model_path, "in")

    in_files = os.listdir(in_path)
    in_files = [os.path.join(in_path, infile) for infile in in_files]

    yaml_files = [infile for infile in in_files if infile.endswith(".yml")]

    batches = {}
    for yfile in yaml_files:
        read_yaml(yfile, batches=batches)

    return batches

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

def format_command(model_path, analysis_data, unique):
    command = analysis.analysis_data["command"]
    inserts = {}
    if '{exe}' in command:
        inserts["exe"] = analysis_data["exe"]
    if '{cpus}' in command:
        inserts["cpus"] = analysis_data["cpus"]
    if '{out}' in command:
        inserts["out"] = analysis_data["out_path"]
    if '{mod}' in command:
        inserts["mod"] = run_data.model_path
    if '{unique}' in command:
        inserts["unique"] = unique

    return command.format(**inserts))

def create_commands_new(run_data):

    #Creates regular analysis commands
    for name, analysis in run_data.batch_data["analysis"].items():
        unique_path = os.path.join(run_data.model_path, 'in', analysis["unique"])
        with open(unique_path, "r") as uni:
            for count, line in enumerate(uni):
                unique = line.split(",")[0].replace("\n", "")
                analysis.commands.append(format_command(run_data.model_path,
                                                        analysis.analysis_data,
                                                        unique))

    #Creates thread test commands
    for name, test in run_data.batch_data["thread_test"].items():
        try:
            unique_path = os.path.join(run_data.model_path, 'in', test["unique_path"])
            with open(unique_path, "r") as uni:
                for count, line in enumerate(uni):
                    unique = line.split(",")[0].replace("\n", "")
                    for ncpu in range(test.analysis_data["lower"], test.analysis_data["upper"]):
                        test.analysis_data["cpus"] = ncpu
                        analysis.commands.append(format_command(run_data.model_path,
                                                                test.analysis_data,
                                                                unique))
    return run

def create_job_files_new(run):
    """Creats sbatch files and puts them in their own folder"""
    template = ""
    with open("btemplate.sh", "r") as btemplate:
        template = btemplate.readlines()

    for name, analysis in run.batch_data["analysis"].items():
        job_dir = os.path.join(analysis.out_path, 'jobs')
        slurm_dir = os.path.join(analysis.out_path, 'slurm')
        try:
            os.makedirs(job_dir)
            os.makedirs(slurm_dir)
        except FileExistsError:
            pass

        file_count = 0
        for count, com in enumerate(analysis.commands):
            if count % run.ntasks == 0:
                file_count += 1
                job_name = "{name}-job-{count}".format(name=analysis["name"], count=file_count)

                with open(os.path.join(analysis["job_dir"], ".".join([job_name, "sh"])), 'w') as bfile:
                    for line in template: #Write Template file
                        bfile.write(line) #

                    #Write automated parameters to file
                    bfile.write("#SBATCH -J {analysis}\n".format(analysis=name]))
                    bfile.write("#SBATCH --cpus-per-task={cpus}\n".format(cpus=analysis.analysis_data["cpus"]))
                    bfile.write("#SBATCH -o {slurm}/{job_name}-%j.out\n".format(slurm=slurm_dir,
                                                                                job_name=job_name))
            #Clean up job name string formatting when files are opened
            with open(os.path.join(analysis["job_dir"], "{}-job-{}.sh".format(name,
                                                                              file_count)), 'a') as bfile:
                bfile.write(com + '\n')
                print(com)

    return run

def schedule_jobs_new(run):
    """Schedules all of the batch files created in slurm"""

    for analysis in :
        print("asdfasdf")
        print(analysis["job_dir"])
        jobs = os.listdir(analysis["job_dir"])
        jobs = [os.path.join(analysis["job_dir"], x) for x in jobs]

        for job in jobs:
            os.system("sbatch {}".format(job))

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

def schedule_jobs(command_data):
    """Schedules all of the batch files created in slurm"""

    for analysis in command_data:
        print("asdfasdf")
        print(analysis["job_dir"])
        jobs = os.listdir(analysis["job_dir"])
        jobs = [os.path.join(analysis["job_dir"], x) for x in jobs]

        for job in jobs:
            os.system("sbatch {}".format(job))

def thread_test(batches):
    for test in batches:
        for ncpu in range(test["range"]["lower"], test["range"]["upper"]):
            pass #left off here
    pass

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
