""" For classes managing computing and storage resources """

import os
import sys
import socket
import paramiko
import subprocess

from collections import namedtuple

class Launcher:
    """
    Base class for the lancher objects used to dispatch shell commands
    to local and remote resources
    """
    JobOut = namedtuple('JobOut', ['output', 'error'])
    def __new__(cls, hostname):
        if hostname is None:
            return super(Launcher, cls).__new__(LocalLauncher)
        else:
            return super(Launcher, cls).__new__(RemoteLauncher)

    def create_background_command(self, commands):
        """
        Recievces a single command or a set of commands as input
        Makes a single command out of the command(s) that will run in
        background
        """
        """
        if not isinstance(commands, str):
            try:
                command = ' '.join(command)
            except TypeError:
                command = str(command)

        for i in range(0, len(tmp_commands), command_number):
            command_set = raw_commands[i:i+command_number]

        commands.append('({})&'.format('; '.join(command_set)))
        return compound_commands
        """
        pass

    def launch_command(self, command):
        """Virtual Abstract method"""
        raise NotImplementedError

class RemoteLauncher(Launcher):
    """
    Used to launch shell commands on remote machines via ssh as well
    as deal with input file and resulting output file transfers
    """
    def __init__(self, hostname):
        """ """
        #Test and setup ssh connection
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname)

    def launch_command(self, command):
        """ """
        if not isinstance(command, str):
            try:
                command = ' '.join(command)
            except TypeError:
                raise TypeError('Launch job requires a string or iterable')

        ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command(command)
        return self.JobOut(ssh_stdout, ssh_stderr)


class LocalLauncher(Launcher):
    """Used to launch shell commands on the local machine"""
    def launch_command(self, command):
        """ """
        process = subprocess.Popen(command,
                                   shell=False,
                                   stdout=subprocess.PIPE)
        return self.JobOut(process.communicate())

class Resource(object):
    """
    Base class for Resource objects used to launch jobs on different types
    of remote and local computing resources
    Base class acts as a factory for computing resources
    """

    type_names = {}
    def __new__(cls, **kwds):
        """Creates and returns proper resource object type"""
        resource_type = kwds.get('resource_type', 'local')
        for sub_cls in cls.__subclasses__():
            if resource_type in sub_cls.type_names:
                return super(Resource, cls).__new__(sub_cls)
        raise TypeError("Resource doesn't exist: {}".format(resource_type))

    def __init__(self, name, hostname=None, **kwds):
        self.name = name
        self.launcher = Launcher(hostname)

class ComputeServer(Resource):
    """
    Resource subclass for dispactching jobs to a single, logical
    unix computer
    """

    type_names = {'compute_server'}
    def __init__(self, name, hostname=None, **kwds):
        super().__init__(self, name, hostname=hostname, **kwds)
        self.command_number = kwds.get('command_number', 1)

class SlurmCluster(ComputeServer):
    """Resource subclass for dispactching jobs to a slurm cluster"""

    type_names = {'slurm_cluster'}
    def __init__(self, name, hostname=None, **kwds):
        super().__init__(self, name, hostname=hostname, **kwds)
