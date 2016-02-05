import os

#executable = "/share/apps/user/stow/netlogo-5.2.1/netlogo-headless.sh"
executable = "/share/apps/user/stow/netlogo-5.2.1/behaviorsearch/behaviorsearch_headless.sh"
model_path = "/home/wpatt2/ARC/DevBench/LogoPipe/Models/SuperSimple1"
model_name = "BUPwithMUASimple1.nlogo"

#csv_path = os.path.join(model_path, "in", "OneWaySA77.csv")
csv_path = os.path.join(model_path, "in", "bsearchSA.csv")

commands = []
ncommand = "{exe} --model {mod}BUPwithMUASimple1.nlogo --experiment {exp} --table {mod}/out/{exp}.out --threads 5"
bcommand = "{exe} -n 3 -p {mod}/{prot} -o {mod}/out/{prot}.out --threads 5"
"""
with open(csv_path, "r") as csv:
    for count, line in enumerate(csv):
        if count != 0:
            experiment = line.split(",")[1]
            commands.append(command.format(exe=executable,
                                           exp=experiment,
                                           mod=model_path))
"""

with open(csv_path, "r") as csv:
    for count, line in enumerate(csv):
        if count != 0:
            protocol = line.split(",")[2]
            commands.append(bcommand.format(exe=executable,
                                            prot=protocol,
                                            mod=model_path))


for com in commands:
    print(com)

template = ""
with open("btemplate.sh", "r") as btemplate:
    template = btemplate.readlines()


job_dir = "./jobs"
try:
    os.mkdir(job_dir)
except:
    pass

file_count = 0
for count, com in enumerate(commands):
    if count % 3 == 0:
        file_count += 1
        with open(os.path.join(job_dir, "job-{}.sh".format(file_count)), 'w') as bfile:
            for line in template:
                bfile.write(line)
    with open(os.path.join(job_dir, "job-{}.sh".format(file_count)), 'a') as bfile:
        bfile.write(com + '\n')

jobs = os.listdir(job_dir)
jobs = [os.path.join("./jobs", x) for x in jobs]

try:
    os.mkdir(os.path.join(model_path, "out"))
except:
    pass
for job in jobs:
    os.system("sbatch {}".format(job))
