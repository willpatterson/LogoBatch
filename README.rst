.. image:: https://travis-ci.org/willpatterson/ImageFudge.svg?branch=master
    :target: https://travis-ci.org/willpatterson/ImageFudge

*********
LogoBatch
*********

``LogoBatch`` is a simple utility for distributing shell commands on a beowulf
cluster using ``Slurm`` or ``SSH``. LogoBatch was originally designed to 
automate the process of running thousands of NetLogo models. 

**LogoBatch should be considered pre-release software.**
LogoBatch is currently being refactored.


Batch Directory
---------------

LogoBatch takes a batch directory as input. `batch_directory/in` is searched 
for CSV files containing parameters to be passed to set shell commands.

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
