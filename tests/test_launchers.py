import unittest
import socket

from logobatch.resources import Launcher
from logobatch.resources import LocalLauncher
from logobatch.resources import RemoteLauncher

class TestLauncherBase(unittest.TestCase):
    def test__new__factory_local(self):
        assert(isinstance(Launcher(None), LocalLauncher))

    def test__new__factory_remote(self):
        """
        Cannot test for instance type because class throws an error if it
        cannot connect to the device specifed by the hostname and I don't
        want to setup a host with sshkeys just for testing so I test for an
        error instead
        """
        self.assertRaises(socket.gaierror, lambda: Launcher(' '))

if __name__ == '__main__':
    test_classes = (TestLauncherBase)
    test_suite = unittest.TestSuite()
    for test_class in test_classes:
        test_suite.addTest(test_class())

    runner = unittest.TextTestRunner()
    runner.run(test_suite)
