#!/bin/sh

##
## Slurm SBATCH configuration options start here.
##

##DISABLED:
##SBATCH --nodes 1

##ENABLED:
#SBATCH --time=30:00:00
#SBATCH -n 1
#SBATCH --partition main,main2
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=1500

## Commands start here
