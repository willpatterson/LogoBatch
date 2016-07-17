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

for cabinet in range(0, 3):
    for node in range(0, 10):
        cmd = 'ps -F -u wpatt2'
        hostname = 'compute-{cab}-{nod}'.format(cab=cabinet, nod=node)
        processes = subprocess.Popen(['ssh', hostname, "ps -F -u wpatt2"],
                                     shell=False,
                                     stdout=subprocess.PIPE).communicate()[0]
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
                        cmd = subprocess.Popen(['ssh',
                                                hostname,
                                                "kill -9 {}".format(pid)],
                                               shell=False,
                                               stdout=subprocess.PIPE)
                        kill_out, kill_err = cmd.communicate()
                    except IndexError:
                        print("INDEX ERROR!!!!")
                        print(dprocess)
                        print()
