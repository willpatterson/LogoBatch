""" For classes managing computing and storage resources """

import os
import sys
import socket
import paramiko

class Launcher:
    def create_background_command(self, command_number=None):
        """Creates command to be sent over ssh"""
        if command_number is None:
            try: command_number = self.command_number
            except AttributeError: command_number = 1

        raw_commands = []
        for inputs_item in self.generate_inputs():
            raw_commands.append(self.format_command(inputs_item))

        commands = []
        for i in range(0, len(tmp_commands), command_number):
            command_set = raw_commands[i:i+command_number]
            commands.append('({})&'.format('; '.join(command_set)))

        return compound_commands

    def launch_job(self, command):
        """Virtual Abstract method"""
        raise NotImplementedError

class RemoteLauncher(Launcher):
    """
    Remote Launcher is class used to launch shell commands on remote
    machines via ssh as well as deal with resulting output transfers
    """
    def __init__(self, hostname):
        """ """
        #Test ssh connection
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname)

class LocalLauncher(Launcher):
    pass

class Resource(object):
    type_names = {}
    def __new__(cls, **kwds):
        """Creates and returns proper resource object type"""
        resource_type = kwds.get('resource_type', 'local')
        for sub_cls in cls.__subclasses__():
            if resource_type in sub_cls.type_names:
                return super(resource, cls).__new__(sub_cls)
        raise TypeError("Resource type doesn't exist: {}".format(batch_type))

    def __init__(self, name, hostname=None, **kwds):
        self.name = name

        if hostname is None: self.launcher = LocalLauncher()
        else: self.launcher = RemoteLauncher(hostname)

class ComputeServer(Resource):
    type_names = {'compute_server'}
    def __init__(self, name, **kwds):
        super.__init__(self, name)
        self.hostname = hostname
        self.command_number = kwds.get('command_number', 1)

class SlurmCluster(ComputeCompute):
    type_names = {'slurm_cluster'}

