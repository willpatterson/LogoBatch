"""Unit Test File"""
import unittest
import os
import warnings
from collections import namedtuple

from logobatch.batches import Batch
from logobatch.batches import SlurmBatch
from logobatch.batches import SshBatch
from logobatch.batches import LocalBatch
from logobatch.batches import ThreadTest
from logobatch.batches import InputsError
from logobatch.batches import InvalidBatchTypeError
from logobatch.batches import MissingAttributeError

from logobatch.logobatch import BatchManager

#LogoBatch Config Testing variables
LB_CONFIG = 'tests/t_lbconfig.yml'
LB_CONFIG_BAD_FORMAT = 'tests/t_lbconfig_bad_f.yml'
LB_CONFIG_EMPTY = 'tests/t_lbconfig_empty'
LBConfigData = namedtuple('LBConfigData',
                          ['compute', 'storage', 'default_email'])

#BBatch testing variables
BATCH_BASE = 'tests/test_batch_base'
BBATCH = 'tests/t_bbatch.yml'
BAD_FORMAT_BB = 'tests/bad_form_t_bbatch.yml'
EMPTY_BBATCH = 'tests/empty_t_bbatch.yml'

class TestBatchManager(unittest.TestCase):
    """Base test class for BatchManager"""
    bm = None
    @classmethod
    def setUpClass(cls):
        """Creates class BatchManager object"""
        cls.bm = BatchManager(BBATCH, BATCH_BASE)

class TestLogoBatchConfigParse(TestBatchManager):
    """"""
    def setUpClass(cls):
        """Creates class BatchManager object"""
        cls.bm = BatchManager(BBATCH, BATCH_BASE)

    def test_parse_logobatch_config_namedtuple_type(self):
        """tests type of named tuple from parse_logobatch_config"""
        lbconf_data = self.bm.parse_logobatch_config(config_yml=LB_CONFIG)
        assert(isinstance(lbconf_data, BatchManager.LBConfigData))

class TestBatchManagerParseBBatch(TestBatchManager):
    def test_parse_bbatch(self):
        """tests parse_bbatch method"""

        #Test Good BBatch Format
        batches, addresses = self.bm.parse_bbatch(bbatch_yml=BBATCH)
        assert(isinstance(batches, list))
        assert(isinstance(batches[0], SshBatch))
        assert(isinstance(batches[1], SlurmBatch))
        assert(batches[0].name == 'sshb')
        assert(isinstance(batches[0].inputs, list))
        assert(isinstance(addresses, list))
        assert(addresses[0] == 'wpatt2@pdx.edu')

    def test_parse_bbatch_bad_format_error(self):
        """Test Bad formatted BB file"""
        self.assertRaises(AttributeError,
                          lambda: self.bm.parse_bbatch(BAD_FORMAT_BB))

    def test_parse_bbatch_empty_bbatch(self):
        """Test Empty BB file error"""
        self.assertRaises(RuntimeError,
                          lambda: self.bm.parse_bbatch(EMPTY_BBATCH))

if __name__ == '__main__':
    test_classes = (TestBatchManagerParseBBatch, TestLogoBatchConfigParse)
    test_suite = unittest.TestSuite()
    for test_class in test_classes:
        test_suite.addTest(test_class())

    runner = unittest.TextTestRunner()
    runner.run(test_suite)
