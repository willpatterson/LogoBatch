.. README.rst

********
LogoPipe
********

``LogoPipe`` is a simple software pipeline that is designed to automate the process of running NetLogo analyses in the ``Slurm Scheduler`` and managing output. 

Model Directory
---------------

LogoPipe takes a model directory as input that is searched for input CSV files containing command parameters.

Model Directory structure:
==========================

::

    model_directory
    |
    +NetLogo input files
    |
    +in
    |  |
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
    

The ``out`` directory is created by ``LogoPipe`` when you run your analysis. Output can be directed elsewhere if desired using command line flags.



