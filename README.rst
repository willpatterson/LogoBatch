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
As the name suggests, a BBatch is a set of batches defined in a YAML file
to be passed to LogoBatch, which distributes them over your defined 
computing resources.

Batch Image
-----------

Batch Images are packages to be used to save and distribute batches. Batch
Images can be created with using LogoBatch's utility ``makebimg``.

Batch Image structure
=====================

::

    batch_image
    |
    +required_input_files #Input files required by batch programs (optional)
    |
    +in
    | |
    |  +bbatch_1.yml #There can be as many bbatches as necessary
    |  +bbatch_2.yml #
    |  +inputs.csv   #There can be as many input csv files as necessary
    |
    +out
       |
       +bbatch_1
       |  |    
       |  +batch_1
       |  |  |
       |  |  +Job1
       |  |  |  |
       |  |  |  +outfile(s).whatever 
       |  |  |  +slurm.out
       |  |  |  +jobfile.sh
       |  |  |
       |  |  +Job2 ...
       |  |  
       |  +batch_2 ...  
       |
       +bbatch_2 ...
    

The ``out`` directory is created when you run LogoBatch. Output can be 
directed elsewhere if desired using command line flags.
