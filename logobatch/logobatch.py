"""File for Batch managment classes"""
import yaml
import datetime
from collections import namedtuple

import os, sys
sys.path.append(os.path.abspath(".."))

from logobatch.batches import Batch

class BBatchFormatError(Exception):
    """Error thrown when yaml format is incorrect"""
    def __init__(self, message):
        super(BBatchFormatError, self).__init__(message)

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

    def __init__(self, bbatch, outpath=None):
        """Initalizes all attributes """

        self.batches, self.addresses = self.parse_bbatch(bbatch)

    @staticmethod
    def parse_bbatch(bbatch):
        """ reads bbatch yaml file into batches """

        with open(bbatch, 'r') as yfile:
            ydata = yaml.load(yfile)

        batches = ydata.get('Batches', None)
        if not isinstance(batches, list):
            raise BBatchFormatError('batches must be in a list')
        batches = [Batch(**b) for b in batches if b.get('enabled', False)]
        addresses = ydata.get('Email', None).get('addresses', None)

        BBatchData = namedtuple('BBatchData', ['batches', 'addresses'])
        return BBatchData(batches, addresses)

    def launch_batches(self):
        """Triggers Batch objects to schedule their job files"""

        for batch in self.batches:
            batch.launch_batch()
