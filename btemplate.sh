#!/bin/sh

## Run this file with the command line "sbatch example.sh" for a working demo.

## See http://slurm.schedmd.com/sbatch.html for all options
## The SBATCH lines are commented out but are still read by the Slurm scheduler
## ***Leave them commented out with a single hash mark!***

## To disable SBATCH commands, start the line with anything other than "#SBATCH"
##SBATCH       # this is disabled
####SBATCH     # so is this
# SBATCH       # disabled
 #SBATCH       # disabled

##
## Slurm SBATCH configuration options start here.
##

## The name of the job that will appear in the output of squeue, qstat, etc.
#SBATCH --job-name=nlogo


## max run time HH:MM:SS

#SBATCH --time=20:00:00


## -N, --nodes=<minnodes[-maxnodes]>
## Request that a minimum of minnodes nodes (servers) be allocated to this job.
## A maximum node count may also be specified with maxnodes.

##SBATCH --nodes 1


## -n, --ntasks=<number>
## This option advises the SLURM controller that job steps run within the
## allocation will launch a maximum of number tasks and to provide for
## sufficient resources. The default is one task per node, but note
## that the --cpus-per-task option will change this default.

#SBATCH -n 3

#SBATCH --partition main,main2
#SBATCH --cpus-per-task=5
#SBATCH --mem-per-cpu=1500

##
## Commands start here
##
