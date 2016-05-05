"""Run the linting rules on the playbook with given args"""

import multiprocessing

from ansible.cli.playbook import PlaybookCLI  # pylint: disable=E0611,F0401
from collections import defaultdict
from interceptor import intercept

from linter.utils import isLTS, suppressConsoleOut
from linter.utils.composite_queue import CompositeQueue

# Override multiprocess Queue to accommodate interceptor's queue.
multiprocessing.Queue = CompositeQueue


class Runner(object):
    """Run playbook in check mode to lint with given rules"""
    def __init__(self, ansible_pbook_args, rules):
        """Initialise runner with playbook args, rules to be run and the error data store"""
        self.ansible_pbook_args = ansible_pbook_args
        self.rules = rules
        self.errors = defaultdict(set)

    def apply_rules(self):
        """Apply lint rules

        Intercept classes using the aspects, both, declared by rules.
        """
        for rule in self.rules:
            rule_obj = rule(self.errors)
            for target_classes, aspects in rule_obj.aspects.iteritems():
                if not isLTS(target_classes):
                    target_classes = [target_classes]
                for _class in target_classes:
                    intercept(aspects)(_class)

    @suppressConsoleOut
    def run_pbook(self):
        """Run playbook in check mode with console-stdout suppressed"""
        for flag in ('--check',):
            if flag not in self.ansible_pbook_args:
                self.ansible_pbook_args.append(flag)
        obj = PlaybookCLI(self.ansible_pbook_args)
        obj.parse()
        obj.run()

    def format_errors(self):
        """Output formatting for errors, if there are."""
        if not self.errors:
            print "Valid Playbook"
            return 0
        for task, errors in self.errors.items():
            print 'Task: {1}{0}{2}{0}'.format('\n', task, '\n'.join(errors))
        return 1

    def run(self):
        """Method to invoke playbook and apply linters."""
        self.apply_rules()
        self.run_pbook()
        self.format_errors()
