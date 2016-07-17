"""
This file contains the batch classes
"""

import os
import sys
import re
import warnings

from datetime import datetime

sys.path.append("..")
from logobatch.email_notice import Email

class NoSlurmTemplateError(Exception):
    """Error when no batchfile is found"""
    def __init__(self, message):
        super(NoSlurmTemplateError, self).__init__(message)

class InvalidExecutableError(Exception):
    """Error thrown when executable doesn't exist"""
    def __init__(self, message):
        super(InvalidExecutableError, self).__init__(message)

class NoInputsError(Exception):
    """Error when no input sources are found"""
    def __init__(self, message):
        super(NoInputsError, self).__init__(message)

class InvalidBatchTypeError(Exception):
    """Error thrown when batch type isn't supported"""
    def __init__(self, message):
        super(InvalidBatchTypeError, self).__init__(message)

class MissingAttributeError(Exception):
    """Error thrown when batch type isn't supported"""
    def __init__(self, message):
        super(MissingAttributeError, self).__init__(message)

class InputsError(Exception):
    """
    Error when incorrect combination of inputs and input markers
    are passed into format_command
    """
    def __init__(self, message):
        super(InputsError, self).__init__(message)

class Batch(object):
    """Base class for analysis and threadtest"""

    def __init__(self, **kwds):
        """ """
        self.command_base = kwds.get('command', None) #Required
        if self.command_base is None:
            raise AttributeError('Missing command')
        elif self.command_base == '':
            raise ValueError("command must not be empty")

        self.executable = kwds.get('executable', '')
        self.batch_base = kwds.get('batch_base', '.')
        self.name = kwds.get('name', str(datetime.now()).replace(' ', '-'))
        #TODO add check and warning if data will be overwritten
        self.output = kwds.get('batch_base',
                               os.path.join(self.batch_base, self.name))
        self.inputs = kwds.get('inputs', None)
        self.email = kwds.get('email', False)
        self.cpus = kwds.get('cpus', 1)
        self.commands = []

        if re.match(r'\{i[0-9]+\}', self.command_base) and self.inputs is None:
            raise NoInputsFileFoundError(("'inputs' was specifed in your"
                                          " yaml object but input markers"
                                          " were found in your command"))

    def format_command(self, command_id, inputs=None, ignore_index=False):
        """
        Formats a command from the base command with class variables
        and adds them the the batches' command list
        """

        inserts = {}
        input_markers = set(re.findall(r'\{(i[0-9]+)\}', self.command_base))

        if inputs and input_markers:
            for marker in input_markers:
                try:
                    inserts.update({marker: inputs[int(marker.strip('i'))]})
                except IndexError as ie:
                    if ignore_index is False: raise ie #TODO maybe message
                    else:
                        warnings.warn(("Index {} is out of bounds, replacing"
                                       " with empty string").format(marker))
                        inserts.update({marker: ''})
        elif input_markers and not inputs:
            raise InputsError(("Error: Input markers where found in"
                              " command_base but no inputs were passed"))
        elif inputs and not input_markers:
            raise InputsError(("Error: Inputs were passed but no input"
                               "markers were found"))

        if '{id}' in self.command_base: inserts.update({'id': command_id})

        standard_markers = set(re.findall(r'\{(.+?)\}', self.command_base))
        standard_markers = standard_markers - input_markers - {'id'}

        for sub in standard_markers:
            format_var = self.__dict__.get(sub, '')
            inserts.update({sub: format_var})

        return self.command_base.format(**inserts)

    @staticmethod
    def generate_inputs(path):
        """Opens a file with inputs entries and yields them"""
        #If file csv yeild split lines
        if os.path.isfile(path) and path.endswith('.csv'):
            with open(path, 'r') as uni:
                for line in uni:
                    yield tuple(line.strip('\n ,\t').split(','))

        #If file but not csv yield path to file
        elif os.path.isfile(path):
            yield os.path.realpath(path)

        #If path dir yield all file paths in dir
        elif os.path.isdir(path):
            for fi in os.listdir(path):
                fipath = os.path.join(os.path.realpath(path), fi)
                if os.path.isfile(fipath):
                    yield fipath

        else: raise InputsError(("Inputs path doesn't lead to a valid"
                                 " file, csv file or directory"))

class Command(object):
    """Represents a valid shell command"""
    def __init__(self, executable, body):
        self.executable = executable
        self.body = body

    def __str__(self):
        """Str function for creating command string"""
        return ' '.join([self.executable, self.body])

    def __iter__(self):
        """Iterator for running with subprocess"""
        yield self.executable
        yield self.body



class ThreadTest(Batch):
    """
    A batch object that is used to run identical commands with
    a different numbers of CPUs or threads within a specified range

    This Batch obejct is intended to figure out where the point of
    deminishing returns related to the number of alloacted threads

    Thread test objects can use also run thread test ranges
    with inputs parameters
    """

    type_names = {'threadtest'}
    def __init__(self, **kwds):
        """
        Sets the self.upper class var
        sets the self.cpus class var as lower. This is done to allow
        ThreadTest batches to use the format_command method
        """

        super().__init__(**kwds)
        self.upper = kwds.get('upper', "")
        if self.upper is None or self.upper == "":
            raise MissingAttributeError(("Attribute 'upper' is required for"
                                         "Thread Test"))
        self.cpus = kwds.get('lower', 1)

    def create_commands(self):
        """Creats and adds commands to the batch"""

        try:
            for inputs_item in self.generate_inputs(self.inputs_path):
                for _ in self.generate_cpu_range():
                    self.format_command(inputs_item=inputs_item)
        except Exception as err: #TODO add exception
            for _ in self.generate_cpu_range():
                self.format_command()
            raise err

    def generate_cpu_range(self):
        """Changes the self.cpus class var and yields nothing"""

        for ncpu in range(self.cpus, self.upper):
            self.cpus = ncpu
            yield

