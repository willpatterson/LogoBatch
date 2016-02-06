import os
import yaml
import argparse
import datetime

def create_commands(model_path, run_name):
    in_path = os.path.join(model_path, "in")

    in_files = os.listdir(in_path)
    in_files = [os.path.join(in_path, infile) for infile in in_files]

    yaml_files = [infile for infile in in_files if infile.endswith(".yml")]

    with open(yaml_files[0], 'r') as yfile:
        ydata = yaml.load(yfile)

    command_data = []
    for analysis in ydata:
        if analysis["analysis"]["enabled"] is True:
            command_data.append(analysis["analysis"])


    for analysis in command_data:
        analysis["out_path"] = os.path.join(model_path, 'out', run_name, analysis["name"])
        unique_path = os.path.join(in_path, analysis["unique"])
        commands = []
        with open(unique_path, "r") as uni:
            for count, line in enumerate(uni):
                unique = line.split(",")[2]
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
        os.makedirs(analysis["job_dir"])
        os.makedirs(slurm_dir)

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
                    bfile.write("#SBATCH -o {slurm}/{job_name}%j.out\n".format(slurm=slurm_dir,
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
        jobs = os.listdir(analysis["job_dir"])
        jobs = [os.path.join(analysis["job_dir"], x) for x in jobs]

        for job in jobs:
            os.system("sbatch {}".format(job))



def get_args():
    """Get arguments"""
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-m", "--model_path", type=str, default=os.getcwd(), help="Directory containing models")
    parser.add_argument("-n", "--ntasks", type=int, default=1, help="Number of tasks per batch")
    parser.add_argument("-r", "--run_name", type=str, default=str(datetime.datetime.now().time()).replace(":", "-"), help="Name of the batch run")

    return parser.parse_args()

def main():
    args = get_args()
    command_data = create_commands(args.model_path, args.run_name)
    command_data = create_job_files(command_data, args.model_path, args.ntasks, args.run_name)
    schedule_jobs(args.model_path, run_name)

if __name__ == "__main__":
    main()
