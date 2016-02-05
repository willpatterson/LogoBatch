import os
import yaml

#executable = "/share/apps/user/stow/netlogo-5.2.1/netlogo-headless.sh"
#executable = "/share/apps/user/stow/netlogo-5.2.1/behaviorsearch/behaviorsearch_headless.sh"
#model_name = "BUPwithMUASimple1.nlogo"
#csv_path = os.path.join(model_path, "in", "OneWaySA77.csv")
#csv_path = os.path.join(model_path, "in", "bsearchSA.csv")

model_path = "/home/wpatt2/ARC/DevBench/LogoPipe/Models/SuperSimple1"
in_path = os.path.join(model_path, "in")

in_files = os.listdir(in_path)
in_files = [os.path.join(in_path, infile) for infile in in_files]

yaml_files = [infile for infile in in_files if infile.endswith(".yml")]

with open(yaml_files[0], 'r') as yfile:
    ydata = yaml.load(yfile)


command_data = []
for analysis in ydata:
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

print(command_data)


template = ""
with open("btemplate.sh", "r") as btemplate:
    template = btemplate.readlines()

job_dir = "./jobs"
try:
    os.mkdir(job_dir)
except:
    pass

file_count = 0
for analysis in command_data:
    for count, com in enumerate(analysis["commands"]):
        if count % 1 == 0:
            file_count += 1
            with open(os.path.join(job_dir, "{}-job-{}.sh".format(analysis["name"], file_count)), 'w') as bfile:
                for line in template:
                    bfile.write(line)
        with open(os.path.join(job_dir, "{}-job-{}.sh".format(analysis["name"], file_count)), 'a') as bfile:
            bfile.write(com + '\n')


jobs = os.listdir(job_dir)
jobs = [os.path.join("./jobs", x) for x in jobs]

try:
    os.mkdir(os.path.join(model_path, "out"))
except:
    pass
for job in jobs:
    os.system("sbatch {}".format(job))
