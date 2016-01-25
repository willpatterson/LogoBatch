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
    |NetLogo input files
    |
    |in
    |  |Analysis_directory
    |  |  |netlogo_commands.csv
    |  |
    |  |Analysis_directory_2
    |
    |out
    |   |Analysis_directory_out
    |   |  |outfiles
    |   |
    |   |Analysis_directory_2_out
    |   |  |outfiles

The ``out`` directory is created by ``LogoPipe`` when you run your analysis. Output can be directed elsewhere if desired (see Input CSV Files).

Input CSV Files
---------------
The input csv files must be located in ``model_dir/in/analysis_name/``. You can have mulitiple analysis directories inside the ``in`` directory and mulitple csv files in each analysis directory.

Input CSV file format:
======================

Each row in an input csv file is a single command to be scheduled in slurm. The first collumn is the executable to call, and every following column is an argument for that executable. The commands are compiled left-to-right in the order outlined in the csv.

Every input csv must have a header line indicating the flags, if any, for every argument value in it's corrisponding file. The first value in the csv header doesn't matter because the first collumn is assumed to be the executable being called. If an argument is positional and has no flag, leave the header for that collumn blank and put it in the correct order.


