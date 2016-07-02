#!/bin/sh

##
## Slurm SBATCH configuration options start here.
##

##DISABLED:
##SBATCH --cpus-per-task=8

##ENABLED:
#SBATCH --nodes 1
#SBATCH --time=144:00:00
#SBATCH -n 1
#SBATCH --partition main,main2
#SBATCH --mem-per-cpu=4000

## Commands start here
