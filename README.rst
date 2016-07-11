.. image:: https://travis-ci.org/willpatterson/LogoBatch.svg?branch=master
    :target: https://travis-ci.org/willpatterson/LogoBatch

*********
LogoBatch
*********

``LogoBatch`` is a simple utility for distributing shell commands on a beowulf
cluster using ``Slurm`` or ``SSH``. LogoBatch was originally designed to 
automate the process of running thousands of NetLogo models. 

**LogoBatch should be considered pre-release software.**
LogoBatch is currently being refactored.

Batch Of Batches (BBatch)
-------------------------
As the name suggests, a BBatch is a set of batches defined in a YAML file to be passed to LogoBatch, which distributes them over your defined computing resources.

Batch Directory structure:
==========================

::

    batch
    |
    +NetLogo input files
    |
    +in
    | |
    |  +run.yml    #There can be multiple run.yml files.
    |  +unique.csv #There can be multiple unique.csv files.
    |
    +out
       |
       +Run1
       |  |    
       |  +Analysis1
       |  |  |
       |  |  +Job1
       |  |  |  |
       |  |  |  +outfile(s).whatever 
       |  |  |  +slurm.out
       |  |  |  +jobfile.sh
       |  |  |
       |  |  +Job2 ...
       |  |  
       |  +Analysis2 ...  
       |
       +Run2 ...
    

The ``out`` directory is created when you run LogoBatch. Output can be 
directed elsewhere if desired using command line flags.
