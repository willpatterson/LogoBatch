import os
import yaml
import argparse
import datetime

def create_commands(model_path):
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
        unique_path = os.path.join(in_path, analysis["unique"])
        commands = []
        with open(unique_path, "r") as uni:
            for count, line in enumerate(uni):
                if count != 0:
                    unique = line.split(",")[0]
                    commands.append(analysis["command"].format(exe=analysis["exe"],
                                                               unique=unique,
                                                               mod=model_path))
        analysis["commands"] = commands

    return command_data

def create_job_files(command_data, model_path, ntasks, run_name):
    """Creats sbatch files and puts them in their own folder"""
    template = ""
    with open("btemplate.sh", "r") as btemplate:
        template = btemplate.readlines()

    job_dir = os.path.join(model_path, "in/jobs", run_name)

    for analysis in command_data:
        file_count = 0
        for count, com in enumerate(analysis["commands"]):
            if count % ntasks == 0:
                file_count += 1
                job_name = "{name}-job-{count}".format(name=analysis["name"], count=file_count)

                with open(os.path.join(job_dir, ".".join([job_name, "sh"])), 'w') as bfile:
                    for line in template:
                        bfile.write(line)

                    bfile.write("#SBATCH -J {analysis}\n".format(analysis=analysis["name"]))
                    bfile.write("#SBATCH --cpus-per-task={cpus}\n".format(cpus=analysis["cpus"]))
                    bfile.write("#SBATCH -o {mod}/out/slurm/{run_name}/{job_name}.out\n".format(mod=model_path,
                                                                                                run_name=run_name,
                                                                                                job_name=job_name))

            with open(os.path.join(job_dir, "{}-job-{}.sh".format(analysis["name"],
                                                                  file_count)), 'a') as bfile:
                bfile.write(com + '\n')

    return run_name

def schedule_jobs(model_path, run_name):
    """Schedules all of the batch files created in slurm"""
    job_dir os.path.join(model_path, "in/jobs", run_name)
    jobs = os.listdir(job_dir)
    jobs = [os.path.join(job_dir, x) for x in jobs]

    try:
        os.makedirs(os.path.join(model_path, "out/slurm", run_name))
    except FileExistsError:
        pass

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
    command_data = create_commands(args.model_path)
    run_name = create_job_files(command_data, args.model_path, args.ntasks, args.run_name)
    schedule_jobs(args.model_path, run_name)

if __name__ == "__main__":
    main()
