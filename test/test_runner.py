"""Test runner class and its methods"""
import sys
import unittest

from linter.runner import Runner
from test import CaptureConsoleOut
from test.runner_data_setup import DummyRule, DummyPrimaryConcern


class RunnerTest(CaptureConsoleOut):
    """Should test runner methods"""
    def test_formatting_if_error(self):
        """Should test formatting of errors"""
        obj = Runner([], [])
        # Introducing error
        obj.errors['A task'] = {"Error A", "Error B"}
        obj.format_errors()
        expected_out = "\n".join(("Task: A task", "Error A", "Error B"))
        self.assertEqual(sys.stdout.getvalue().strip(), expected_out)

    def test_formatting_no_error(self):
        """Should test formatting of errors"""
        obj = Runner([], [])
        obj.format_errors()
        expected_out = "Valid Playbook"
        self.assertEqual(sys.stdout.getvalue().strip(), expected_out)

    def test_apply_rules(self):
        """Should test if rules are being applied"""
        obj = Runner([], [DummyRule])
        obj.apply_rules()  # Applying
        pc_obj = DummyPrimaryConcern()
        pc_obj.true()  # So when primary concern is run, rule should work.
        expected_out = "\n".join(("Before true", "In true", "After true"))
        self.assertEqual(sys.stdout.getvalue().strip(), expected_out)


if __name__ == '__main__':
    unittest.main()
