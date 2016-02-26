import os

command = "{exe} --model {mod}/BUPwithMUASimple1.nlogo --experiment {unique} --table /home/wpatt2/CapDoc_out/{unique} --threads 8 > {stdo}{unique}.output"
exe = "/share/apps/user/stow/netlogo-5.2.1/netlogo-headless.sh"
mod = "/home/wpatt2/allExp"
stdout = "/home/wpatt2/CapDoc_out/stdout/"

commands = []
with open("/home/wpatt2/allExp/CapExps.csv", 'r') as cfile:
    for line in cfile:
        uni = line.replace("\n", "")
        tmp_cmd = command.format(exe=exe, unique=uni, mod=mod, stdo=stdout)
        commands.append(tmp_cmd)
print(len(commands))

double_cmd = '({cmd1}; {cmd2};)&'
double_commands = []
for count, cmd in enumerate(commands):
    try:
        if (count % 2) == 0:
            new_cmd = double_cmd.format(cmd1=cmd, cmd2=commands[count+1])
            double_commands.append(new_cmd)
    except IndexError:
        double_commands.append("{cmd} &".format(cmd=cmd))

print(len(double_commands))

#for i in double_commands:
    #print(i)
	

for cabinet in range(0, 3):
    for node in range(0, 10):
        os.system("(ssh compute-{cab}-{nod} '{cmd}')&".format(cab=cabinet, nod=node, cmd=double_commands.pop(0)))
        #os.system("ssh compute-{cab}-{nod} 'killall -u wpatt2 /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.65-0.b17.el6_7.x86_64/jre/bin/java'".format(cab=cabinet, nod=node))
        #print("compute-{cab}-{nod}".format(cab=cabinet, nod=node))
        #print("ssh compute-{cab}-{nod} '{cmd}'&".format(cab=cabinet, nod=node, cmd=double_commands.pop(0)))

print()
print("++++++++++++++++++++++++++++")
print()

unrun_cmds = "/home/wpatt2/Alex_out/EXPIREMENTS_NOT_YET_RUN.txt"
with open(unrun_cmds, 'w') as efile:
    for cmd in double_commands:
        print(cmd)
        efile.write(cmd + '\n')
