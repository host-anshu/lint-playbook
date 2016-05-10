"""Test suites"""

import sys
import unittest

from StringIO import StringIO


class CaptureConsoleOut(unittest.TestCase):
    """Base testcase to capture stdout and stderr

    Capture console out by reassigning sys.stdout and sys.stderr for the duration of the test
    """
    def setUp(self):
        self.saved_stdout = sys.stdout
        sys.stdout = StringIO()
        self.saved_stderr = sys.stderr
        sys.stderr = StringIO()

    def tearDown(self):
        sys.stdout = self.saved_stdout
        sys.stderr = self.saved_stderr
