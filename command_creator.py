import os

model_path = "/home/wpatt2/ARC/DevBench/LogoPipe/SuperSimple/"
csv_path = os.path.join(model_path, "in", "OneWaySA77.csv")

commands = []
command = "/share/apps/user/stow/netlogo-5.2.1/netlogo-headless.sh --model /home/wpatt2/ARC/DevBench/LogoPipe/SuperSimple/BUPwithMUASimple.nlogo --experiment {exp} --table /home/wpatt2/ARC/DevBench/LogoPipe/SuperSimple/out/{exp}.out --threads 5"
with open(csv_path, "r") as csv:
    for count, line in enumerate(csv):
        if count != 0:
            experiment = line.split(",")[1]
            commands.append(command.format(exp=experiment))

for com in commands:
    print(com)

file_count = 0
for count, com in enumerate(commands):
    if count % 3 == 0:
        file_count += 1
    with open("job-{}.sh".format(file_count), 'a') as bfile:
        bfile.write(com + '\n')

