import os

batches = os.listdir("./batch_scripts")
batches = [os.path.join("./batch_scripts", x) for x in batches]
print(batches)

for b in batches:
    os.system("sbatch {}".format(b))
