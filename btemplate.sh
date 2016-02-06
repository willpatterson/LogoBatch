#!/bin/sh

##
## Slurm SBATCH configuration options start here.
##

##DISABLED:
##SBATCH --nodes 1
##SBATCH --cpus-per-task=8

##ENABLED:
#SBATCH --time=30:00:00
#SBATCH -n 1
#SBATCH --partition main,main2
#SBATCH --mem-per-cpu=4000

## Commands start here
