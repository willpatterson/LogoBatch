import unittest

from logobatch.batches import Batch, SshBatch, SlurmBatch
from logobatch.logobatch import BatchManager

BATCH_BASE = "test/test_batch_base"
BBATCH = "test/t_bbatch.yml"

class TestBatchManager(unittest.TestCase):
    """ Test Class for BatchManager"""

    def setUp(self):
        self.bm = BatchManager(BBATCH, BATCH_BASE)

    def tearDown(self):
        pass

    def test_parse_bbatch(self):
        """tests parse_bbatch method"""
        batches, addresses = self.bm.parse_bbatch(BBATCH)
        assert(isinstance(batches, list))
        assert(isinstance(batches[0], SshBatch))
        assert(isinstance(batches[1], SlurmBatch))
        assert(batches[0].name)
        assert(isinstance(batches[0].inputs, list))
        assert(isinstance(addresses, list))
        assert(addresses[0] == 'wpatt2@pdx.edu')

