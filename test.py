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
LB_CONFIG = 'test/t_lbconfig.yml'
LB_CONFIG_BAD_FORMAT = 'test/t_lbconfig_bad_f.yml'
LB_CONFIG_EMPTY = 'test/t_lbconfig_empty'
LBConfigData = namedtuple('LBConfigData',
                          ['compute', 'storage', 'default_email'])

#BBatch testing variables
BATCH_BASE = 'test/test_batch_base'
BBATCH = 'test/t_bbatch.yml'
BAD_FORMAT_BB = 'test/bad_form_t_bbatch.yml'
EMPTY_BBATCH = 'test/empty_t_bbatch.yml'

class TestBatchManager(unittest.TestCase):
    """ Test Class for BatchManager"""
    bm = None

    @classmethod
    def setUpClass(cls):
        cls.bm = BatchManager(BBATCH, BATCH_BASE)

    def test_parse_logobatch_config_namedtuple_type(self):
        """ """
        lbconf_data = self.bm.parse_logobatch_config(config_yml=LB_CONFIG)
        assert(isinstance(lbconf_data, BatchManager.LBConfigData))

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

TEST_CSV = 'test/input_test.csv'
TEST_SINGLE_FILE = 'test/t_bbatch.yml'
TEST_DIR = 'test/input_dir_test'
INPUTS = ('0', '1', '2', '3')

class TestBatch(unittest.TestCase):
    """Test Class for Batch"""

    def test__new__factory(self):
        """Test subclass object creation with Batch.__new__"""
        ssh_params = {'batch_type': 'ssh',
                      'hostnames': ['test.local'],
                      'command': 'test'}
        slurm_params = {'batch_type': 'slurm',
                        'command': 'test'}
        tt_params = {'batch_type': 'threadtest',
                     'command': 'test',
                     'upper': 4}
        local_params = {'batch_type': 'local',
                        'command': 'test'}
        typeless_params = {'command': 'test'}

        #Test batch type creation
        assert(isinstance(Batch(**ssh_params), SshBatch))
        assert(isinstance(Batch(**slurm_params), SlurmBatch))
        assert(isinstance(Batch(**tt_params), ThreadTest))
        assert(isinstance(Batch(**local_params), LocalBatch))
        assert(isinstance(Batch(**typeless_params), LocalBatch))

        #Test incorrect batch type error
        bad_type_params = {'batch_type': 'bad',
                           'command': 'test'}
        self.assertRaises(InvalidBatchTypeError,
                          lambda: Batch(**bad_type_params))

    def test__init__no_args(self):
        """No Args"""
        self.assertRaises(AttributeError, lambda: Batch.__init__(Batch))

    def test__init__empty_command(self):
        """Empty command"""
        batch_params = {'command': ''}
        self.assertRaises(ValueError,
                          lambda: Batch.__init__(Batch, **batch_params))

    def test_generate_inputs(self):
        """tests three outcomes of the generate inputs static method"""

        #CSV input parsing
        split_csv = list(Batch.generate_inputs(TEST_CSV))
        assert(split_csv == [('1','2','3','4'),('a','b','c','df')])

        #Single file path yield
        file_path = list(Batch.generate_inputs(TEST_SINGLE_FILE))
        assert(file_path == [os.path.realpath(TEST_SINGLE_FILE)])

        #Direcotry file yield
        dir_list = list(Batch.generate_inputs(TEST_DIR))
        assert(dir_list == [os.path.realpath(os.path.join(TEST_DIR, 't1')),
                            os.path.realpath(os.path.join(TEST_DIR, 't2')),
                            os.path.realpath(os.path.join(TEST_DIR, 't3'))])

        #Test bad input
        self.assertRaises(InputsError,
                          lambda: list(Batch.generate_inputs('asdf')))

    def test_format_command(self):
        """
        Tests format_command
        """

        #Test class attribute input markers
        class_attr_params = {'batch_type': 'ssh',
                             'hostnames': ['test.local'],
                             'command': '{batch_base} {name}'}
        sshb = Batch(**class_attr_params)
        command = sshb.format_command(1)
        assert(command == '{} {}'.format(sshb.batch_base, sshb.name))

        #Test CSV input markers
        sshb.command_base = '{id} {i0} {i1} {i2} {i3}'
        command = sshb.format_command(1, inputs=INPUTS)
        assert(command == '1 0 1 2 3')

        sshb.command_base = '{batch_base} {id} {i0} {i1} {i2} {i3}'
        command = sshb.format_command(1, inputs=INPUTS)
        assert(command == '{} 1 0 1 2 3'.format(sshb.batch_base))

        #Test CSV index exception
        sshb.command_base = '{i10}'
        self.assertRaises(IndexError,
                          lambda: sshb.format_command(1, inputs=INPUTS))

        #Test input markers and no inputs
        sshb.command_base = '{i0} {i1} {i2} {i3}'
        self.assertRaises(InputsError,
                          lambda: sshb.format_command(1))

        #Test input and not input markers
        sshb.command_base = '{batch_base}'
        self.assertRaises(InputsError,
                          lambda: sshb.format_command(1, inputs=INPUTS))

        #Test Index warning: Ignore True
        sshb.command_base = '{i0} {i1} {i2} {i6}'
        with warnings.catch_warnings(record=True) as w:
            command = sshb.format_command(1, inputs=INPUTS, ignore_index=True)
            assert(command == '0 1 2 ')
            assert(len(w) == 1)
            assert(issubclass(w[-1].category, Warning))
            assert('Index' in str(w[-1].message))

        #Test Index warning: Ignore False
        self.assertRaises(IndexError,
                          lambda: sshb.format_command(1, inputs=INPUTS))

class TestSshBatch(unittest.TestCase):
    """ """
    def setUp(self):
        bm = BatchManager(BBATCH, BATCH_BASE)
        self.ssh_batch = bm.batches[0]

class TestSlurmBatch(unittest.TestCase):
    """ """
    def setUp(self):
        bm = BatchManager(BBATCH, BATCH_BASE)
        self.slurm_batch = bm.batches[1]

if __name__ == '__main__':
    test_classes = (TestBatch, TestBatchManager)
    test_suite = unittest.TestSuite()
    for test_class in test_classes:
        test_suite.addTest(test_class())

    runner = unittest.TextTestRunner()
    runner.run(test_suite)
