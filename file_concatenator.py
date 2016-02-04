import os

files = os.listdir(".")

job_files = [x for x in files if x.startswith("job-")]
print(job_files)

try:
    os.mkdir("./batch_scripts")
except:
    pass

for job in job_files:
    os.system("cat ../btemplate.sh {j} >> ./batch_scripts/{j}b.sh".format(j=job))
