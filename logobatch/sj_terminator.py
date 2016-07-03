import os
import subprocess
import paramiko

def count_lines(path):
    with open(path, 'r') as pfile:
        return len(pfile.readlines())

exe = "/share/apps/user/stow/netlogo-5.2.1/netlogo-headless.sh"
out_dir = '/home/wpatt2/Alex_out'

out_files = os.listdir(out_dir)

out_files = [os.path.join(out_dir, f) for f in out_files]

finished_files = []
for item in out_files:
    if (not item.endswith('.txt')) and os.path.isfile(item):
        line_number = count_lines(item)
        if count_lines(item) >= 225:
            print(item + " " + str(line_number))
            finished_files.append(item)


#for i in finished_files:
#    print(i)

for cabinet in range(0, 3):
    for node in range(0, 10):
        cmd = 'ps -F -u wpatt2'
        hostname = 'compute-{cab}-{nod}'.format(cab=cabinet, nod=node)
        processes = subprocess.Popen(['ssh', hostname, "ps -F -u wpatt2"], shell=False, stdout=subprocess.PIPE).communicate()[0]
        for process in processes.splitlines():
            for ffile in finished_files:
                dprocess = process.decode("utf-8")
                if (ffile in dprocess) and not (exe in dprocess):
                    try:
                        tabs = dprocess.split(' ')
                        print(tabs)
                        pid = tabs[1]
                        print('----')
                        print(ffile)
                        print(dprocess)
                        print(type(dprocess))
                        print()
                        #kill_out = subprocess.Popen(['ssh', hostname, "kill -9 {}".format(pid)], shell=False, stdout=subprocess.PIPE).communicate()[0]
                    except IndexError:
                        print("INDEX ERROR!!!!")

                        print(dprocess)
                        print()
                        print()



"""



        out = ssh.exec_command(cmd)[1]
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('compute-{cab}-{nod}'.format(cab=cabinet, nod=node), username="wpatt2", allow_agent=False, look_for_keys=False)
"(ssh compute-{cab}-{nod} '{cmd}')&".format(cab=cabinet, nod=node, cmd=double_commands.pop(0)))
processes = subprocess.Popen(['ps', '-F', '-u', 'wpatt2'], stdout=subprocess.PIPE).communicate()[0]
for line in processes.splitlines():
    if (cmd_exe in line) and (
"""
