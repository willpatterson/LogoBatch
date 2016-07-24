import unittest

from logobatch.resources import Launcher
from logobatch.resources import LocalLauncher
from logobatch.resources import RemoteLauncher

VALID_BG_CMD = '(echo test)&'
VALID_BG_CMD_MULTI = '(echo test; echo test2; )&'
class TestLauncherBase(unittest.TestCase):
    """Tests for Lancher, the base class of RemoteLauncher and LocalLauncher"""

    @staticmethod
    def test__new__factory_local():
        """tests if Lanucher passed None creates LocalLauncher object"""
        assert isinstance(Launcher(None), LocalLauncher)

    def test__new__factory_remote(self):
        """
        TODO:
            * test connects via ssh
            * test for connection error
        """
        #self.assertRaises(socket.gaierror, lambda: Launcher(' '))
        pass

    def test_launch_command_error(self):
        """Tests that launch_command is not Implemented """
        self.assertRaises(NotImplementedError,
                          lambda: Launcher.launch_command(Launcher, ''))

    def test_create_bg_cmd_str(self):
        """Test create_background_command method for a single string"""
        self.assertEqual(VALID_BG_CMD,
                         Launcher.create_background_command('echo test'))

    def test_create_bg_cmd_multi(self):
        """Test create_background_command"""
        self.assertEqual(VALID_BG_CMD_MULTI,
                         Launcher.create_background_command(('echo test',
                                                             'echo test2')))


if __name__ == '__main__':
    TEST_CLASSES = (TestLauncherBase,)
    TEST_SUITE = unittest.TestSuite()
    for test_class in TEST_CLASSES:
        TEST_SUITE.addTest(test_class())

    RUNNER = unittest.TextTestRunner()
    RUNNER.run(TEST_SUITE)
