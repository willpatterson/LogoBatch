import unittest
import os
import warnings
from collections import namedtuple
import sys

sys.path.append(os.path.abspath('..'))

from logobatch.batches import Batch
from logobatch.batches import InputsError
from logobatch.batches import InvalidBatchTypeError
from logobatch.batches import MissingAttributeError

from logobatch.batches import Command

TEST_CSV = 'tests/input_test.csv'
TEST_SINGLE_FILE = 'tests/t_bbatch.yml'
TEST_DIR = 'tests/input_dir_test'
INPUTS = ('0', '1', '2', '3')


class TestBatch(unittest.TestCase):
    """Test Class for Batch"""

    def test__init__no_args(self):
        """No Args"""
        self.assertRaises(AttributeError, lambda: Batch.__init__(Batch))

    def test__init__empty_command(self):
        """Empty command"""
        batch_params = {'command': ''}
        self.assertRaises(ValueError,
                          lambda: Batch.__init__(Batch, **batch_params))

    #TEST GENERATE INPUTS######################################################
    def test_generate_inputs_csv_yield(self):
        """CSV input parsing"""
        split_csv = list(Batch.generate_inputs(TEST_CSV))
        assert(split_csv == [('1','2','3','4'),('a','b','c','df')])

    def test_generate_inputs_file_yield(self):
        """Single file path yield"""
        file_path = list(Batch.generate_inputs(TEST_SINGLE_FILE))
        assert(file_path == [os.path.realpath(TEST_SINGLE_FILE)])

    def test_generate_inputs_directory_yield(self):
        """Direcotry file yield"""
        dir_list = list(Batch.generate_inputs(TEST_DIR))
        assert(dir_list == [os.path.realpath(os.path.join(TEST_DIR, 't1')),
                            os.path.realpath(os.path.join(TEST_DIR, 't2')),
                            os.path.realpath(os.path.join(TEST_DIR, 't3'))])

    def test_generate_inputs_bad_input(self):
        """Test bad input"""
        self.assertRaises(InputsError,
                          lambda: list(Batch.generate_inputs('asdf')))

class TestBatchFormatCommand(unittest.TestCase):
    """Test class for Batch format_command method"""
    sshb = None

    @classmethod
    def setUpClass(cls):
        class_attr_params = {'batch_type': 'ssh',
                             'hostnames': ['test.local'],
                             'command': '{batch_base} {name}'}
        cls.sshb = Batch(**class_attr_params)


    def test_format_command_attribute_input_markers(self):
        """Test class attribute input markers"""
        command = self.sshb.format_command(1)
        assert(command == '{} {}'.format(self.sshb.batch_base, self.sshb.name))

    def test_format_command_csv_inputs(self):
        """Test CSV input markers"""
        self.sshb.command_base = '{id} {i0} {i1} {i2} {i3}'
        command = self.sshb.format_command(1, inputs=INPUTS)
        assert(command == '1 0 1 2 3')

    def test_format_command_csv_inputs_with_batch_base(self):
        self.sshb.command_base = '{batch_base} {id} {i0} {i1} {i2} {i3}'
        command = self.sshb.format_command(1, inputs=INPUTS)
        assert(command == '{} 1 0 1 2 3'.format(self.sshb.batch_base))

    def test_format_command_csv_bad_index(self):
        """Test CSV index exception"""
        self.sshb.command_base = '{i10}'
        self.assertRaises(IndexError,
                          lambda: self.sshb.format_command(1, inputs=INPUTS))

    def test_format_command_makers_but_not_inputs(self):
        """Test input markers and no inputs"""
        self.sshb.command_base = '{i0} {i1} {i2} {i3}'
        self.assertRaises(InputsError,
                          lambda: self.sshb.format_command(1))

    def test_format_command_input_but_no_markers(self):
        """Test input and not input markers"""
        self.sshb.command_base = '{batch_base}'
        self.assertRaises(InputsError,
                          lambda: self.sshb.format_command(1, inputs=INPUTS))

    def test_format_command_index_warning_ignore_true(self):
        """Test Index warning: Ignore True"""
        self.sshb.command_base = '{i0} {i1} {i2} {i6}'
        with warnings.catch_warnings(record=True) as w:
            command = self.sshb.format_command(1,
                                               inputs=INPUTS,
                                               ignore_index=True)
            assert(command == '0 1 2 ')
            assert(len(w) == 1)
            assert(issubclass(w[-1].category, Warning))
            assert('Index' in str(w[-1].message))

    def test_format_command_index_warning_ignore_flase(self):
        """Test Index warning: Ignore False"""
        self.sshb.command_base = '{i0} {i1} {i2} {i6}'
        self.assertRaises(IndexError,
                          lambda: self.sshb.format_command(1, inputs=INPUTS))

EXECUTABLE = 'which'
BODY = 'which'
VALID_STR_COMMAND = EXECUTABLE + ' ' + BODY
VALID_ITER = [EXECUTABLE, BODY]
class TestCommand(unittest.TestCase):
    """Tests Command class"""
    cmd = None
    @classmethod
    def setUpClass(cls):
        cls.cmd = Command(EXECUTABLE, BODY)

    def test__str__(self):
        """Tests __str__ method of Command"""
        self.assertEqual(str(self.cmd), VALID_STR_COMMAND)

    def test__iter__(self):
        """Tests if __iter__ yields attributes in the right order"""
        self.assertEqual(list(self.cmd), VALID_ITER)

if __name__ == '__main__':
    test_classes = (TestBatch, TestBatchFormatCommand, TestCommand)
    test_suite = unittest.TestSuite()
    for test_class in test_classes:
        test_suite.addTest(test_class())

    runner = unittest.TextTestRunner()
    runner.run(test_suite)
