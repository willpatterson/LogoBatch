.. image:: https://travis-ci.org/willpatterson/LogoPipe.svg?branch=master 
    :target: https://travis-ci.org/willpatterson/LogoPipe
********
LogoPipe
********

``LogoPipe`` is a simple software pipeline originally designed to automate the process
of running thousands of NetLogo models on a beowulf cluster using 
``Slurm`` or ``SSH``.

**LogoPipe should be considered pre-release software.**
LogoPipe is currently being refactored.


Model Directory
---------------

LogoPipe takes a model directory as input. The input directory is searched 
for CSV files containing parameters to be passed to headless netlogo.

Model Directory structure:
==========================

::

    model_directory
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
    

The ``out`` directory is created when you run LogoPipe. Output can be 
directed elsewhere if desired using command line flags.
