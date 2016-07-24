"""File for Batch managment classes"""
import yaml
import datetime
import warnings
from collections import namedtuple

import os, sys
sys.path.append(os.path.abspath(".."))

from logobatch.batches import Batch

class BatchManager:
    """
    The BatchManager class contains and manages all Batch objects

    BatchManager is responsible for:
       - parsing yaml files
       - creating Batch objects from yaml data
       - setting the base output path
       - building Batch objects
       - running Batch objects
    """
    LBConfigData = namedtuple('LBConfigData',
                              ['compute', 'storage', 'default_email'])
    BBatchData = namedtuple('BBatchData', ['batches', 'addresses'])

    def __init__(self, bbatch, outpath=None):
        """Initalizes all attributes """

        self.batches, self.addresses = self.parse_bbatch(bbatch)

    @staticmethod
    def parse_logobatch_config(config_yml=None, **kwds):
        """
        Parses config file for logobatch's main settings from a config file,
        typically found at: ~/.logobatch.yml
        INPUT:
            config_yml: path to the logobatch config file
            **kwds: raw dictionary
        OUTPUT: logobatch config data (compute/storage resources, email)
        """
        try:
            with open(config_yml, 'r') as yfile:
                kwds = yaml.safe_load(yfile)
        except TypeError:
            pass

        compute = kwds.get('compute', None)
        compute = kwds.get('compute', None)
        if compute and not isinstance(compute, list):
            raise TypeError('Resources must be defined in YAML list')
        storage = kwds.get('storage', None)
        default_email = kwds.get('default_email', None)

        return BatchManager.LBConfigData(compute, storage, default_email)

    @staticmethod
    def parse_bbatch(bbatch_yml=None, **kwds):
        """ reads bbatch yaml file into batches """
        try:
            with open(bbatch_yml, 'r') as yfile:
                kwds = yaml.load(yfile)
        except TypeError:
            pass

        batches = kwds.get('Batches', None)
        if isinstance(batches, list) or\
           isinstance(batches, set) or\
           isinstance(batches, tuple):
            batches = [Batch(**b) for b in batches if b.get('enabled', False)]
        elif batches is None:
            raise RuntimeError('No batches specified')
        else:
            warnings.warn(('batches were defined in a non-standard way,'
                           ' some settings might be lost'), RuntimeWarning)
            if isinstance(batches, dict):
                batches = [Batch(**val) for _, val in batches.items()]
            else:
                batches = [Batch(**batches)]

        addresses = kwds.get('Email', None).get('addresses', None)

        return BatchManager.BBatchData(batches, addresses)

    def launch_batches(self):
        """Triggers Batch objects to schedule their job files"""

        for batch in self.batches:
            batch.launch_batch()
