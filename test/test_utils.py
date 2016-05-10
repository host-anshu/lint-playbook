"""Test utilities"""
# import logging
import sys
import unittest

from linter.utils import isLTS, suppressConsoleOut
from test import CaptureConsoleOut


class IsLTSTest(unittest.TestCase):
    """Test is instance of a list, tuple or set"""
    def test(self):
        """Should test if an object is list, tuple or set."""
        for obj in (list(), tuple(), set()):
            self.assertTrue(isLTS(obj))
        for obj in (str(), dict(), frozenset()):
            self.assertFalse(isLTS(obj))


class DemonstrateConsoleOutSuppression(object):
    """Demonstrating class for suppressConsoleOut decorator"""
    @staticmethod
    def normal_print():
        """Print to console"""
        print "I print"
    # TODO: Clear the confusion related to logging way of console out.
    # def log_warning(self):
    #     logging.warning("Be warned!")
    #
    # def log_error(self):
    #     logging.error("Error!")

    @staticmethod
    def stderr_write():
        """Write to stderr"""
        sys.stderr.write("I write to stderr")


class SuppressConsoleOutTest(CaptureConsoleOut):
    """Should test suppressConsoleOut decorator"""
    def setUp(self):
        self.obj = DemonstrateConsoleOutSuppression()
        self.expected_normal_print = "I print"
        self.expected_stderr_write = "I write to stderr"
        # self.expected_error_out = "ERROR:root:Error!"
        # self.expected_warn_out = "WARNING:root:Be warned!"
        super(SuppressConsoleOutTest, self).setUp()

    def test_normal(self):
        """Shouldn't suppress print, sys.stderr"""
        self.obj.normal_print()
        self.assertEqual(sys.stdout.getvalue().strip(), self.expected_normal_print)
        self.obj.stderr_write()
        self.assertEqual(sys.stderr.getvalue().strip(), self.expected_stderr_write)
        # self.obj.log_warning()
        # self.assertEqual(sys.stderr.getvalue().strip(), "".join(
        #     (self.expected_stderr_write, self.expected_warn_out)))
        # self.obj.log_error()
        # self.assertEqual(sys.stderr.getvalue().strip(), "".join(
        #     (self.expected_stderr_write, self.expected_warn_out, "\n",
        #      self.expected_error_out)))

    def test_suppressed_np(self):
        """Should suppress print"""
        npm = DemonstrateConsoleOutSuppression.normal_print
        npm = suppressConsoleOut(npm)
        npm()
        self.assertNotEqual(sys.stdout.getvalue().strip(), self.expected_normal_print)
        self.assertEqual(sys.stdout.getvalue().strip(), "")

    def test_suppressed_sw(self):
        """Should suppress sys.stderr"""
        swm = DemonstrateConsoleOutSuppression.stderr_write
        swm = suppressConsoleOut(swm)
        swm()
        self.assertNotEqual(sys.stderr.getvalue().strip(), self.expected_stderr_write)
        self.assertEqual(sys.stderr.getvalue().strip(), "")

    # def test_suppressed_lw(self):
    #     lwm = DemonstrateConsoleOutSuppression.log_warning
    #     # lwm = suppressConsoleOut(lwm)
    #     lwm(self.obj)
    #     self.assertNotEqual(sys.stderr.getvalue().strip(), self.expected_warn_out)
    #     self.assertEqual(sys.stderr.getvalue().strip(), "")
    #
    # def test_suppressed_le(self):
    #     lem = DemonstrateConsoleOutSuppression.log_error
    #     # lem = suppressConsoleOut(lem)
    #     lem(self.obj)
    #     self.assertNotEqual(sys.stderr.getvalue().strip(), self.expected_error_out)
    #     self.assertEqual(sys.stderr.getvalue().strip(), "")


if __name__ == '__main__':
    unittest.main()
