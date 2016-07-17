import unittest

from logobatch.resources import Launcher
from logobatch.resources import LocalLauncher
from logobatch.resources import RemoteLauncher

class TestLauncherBase(unittest.TestCase):
    def test__new__factory(self):
        assert(isinstance(Launcher(None), LocalLauncher))

if __name__ == '__main__':
    test_classes = (TestLauncherBase)
    test_suite = unittest.TestSuite()
    for test_class in test_classes:
        test_suite.addTest(test_class())

    runner = unittest.TextTestRunner()
    runner.run(test_suite)
