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
        TODO:
            * test connects via ssh
            * test for connection error
        """
        #self.assertRaises(socket.gaierror, lambda: Launcher(' '))
        pass

    def test_launch_command(self):
        self.assertRaises(NotImplementedError,
                          lambda: Launcher.launch_command(Launcher, ''))

if __name__ == '__main__':
    test_classes = (TestLauncherBase)
    test_suite = unittest.TestSuite()
    for test_class in test_classes:
        test_suite.addTest(test_class())

    runner = unittest.TextTestRunner()
    runner.run(test_suite)
