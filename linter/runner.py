"""Run the linting rules on the playbook with given args"""

import argparse
import multiprocessing
import sys

from ansible.cli.playbook import PlaybookCLI  # pylint: disable=E0611,F0401
from collections import defaultdict
from interceptor import intercept
from os.path import dirname, isdir, relpath

from linter import rules as R
from linter.version import __version__
from linter.utils import isListTupleSet
from linter.utils.composite_queue import CompositeQueue

# Override multiprocess Queue to accommodate interceptor's queue.
multiprocessing.Queue = CompositeQueue


class Linter(object):
    """Run and analyse playbook for logical pitfalls.

    The tool intercepts ansible-playbook at runtime and applies rules that find the pitfalls.
    It runs playbook compulsorily in check mode(no explicit --check required).
    """
    # Exit codes
    success = 0
    error = 1

    def __init__(self, pb_args):
        self.default_rules_dir = dirname(R.__file__)
        self.lp_args = None
        self.pb_args = pb_args
        self.rules = None

    @staticmethod
    def set_usage(parser):
        # parser usage with whitespace and 'usage:' on left, both stripped.
        usage = parser.format_usage().strip()[len("usage: "):]
        pb_usage_ref = " -- <ansible-playbook options> your_playbook.yml\n"
        added_info = "\n".join([
            "Use '--' to separate <lint-pbook options> and <ansible-playbook options>",
            "Not required if given flags aren't used to lint playbook."])
        parser.usage = usage + pb_usage_ref + added_info

    def parse(self):
        def existing_path(_path):
            if isdir(_path):
                return _path
            raise argparse.ArgumentError(("Invalid directory path: {0}".format(_path)))

        parser = argparse.ArgumentParser(
            add_help=False,
            # docstring with 4 space as tabs removed
            description=Linter.__doc__.replace(' ' * 4, ''),
            epilog="Default rules at: %s" % relpath(self.default_rules_dir),
            formatter_class=argparse.RawTextHelpFormatter,
        )
        parser.add_argument(
            '-v', '--version', action='version', version='%(prog)s ' + __version__,
            help="Show program's version number and exit")
        parser.add_argument('-h', '--help', action='help', help='Show help and exit')
        parser.add_argument(
            "-l", action="store_true", dest="list_rules", help="List all the rules and exit")
        parser.add_argument(
            '-T', action='store_true', dest='list_tags', help="List all the tags and exit")
        parser.add_argument(
            "-r", nargs="+", dest="rules_dirs", default=[], type=existing_path,
            help="Use one or more rules directories.\nIf -R isn't used, ignore the default rules")
        parser.add_argument(
            "-R", action="store_true", dest="use_default_rules",
            help="Use the default rules as well.\nIt isn't needed if -r not used")
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            # Validate argument later
            "-t", nargs="+", dest="tags", help="Use rules whose id/tags match these values")
        group.add_argument(
            # Validate argument later
            "-x", nargs="+", dest="skip_tags", help="Skip rules whose id/tags match these values")
        self.set_usage(parser)
        self.lp_args = parser.parse_args(sys.argv[1:])

        # Missing playbook args and no listrules
        if len(self.pb_args) == 1 and not (self.lp_args.list_rules or self.lp_args.list_tags):
            parser.error("No args for playbook found.")
            parser.print_usage(file=sys.stderr)
            sys.exit(Linter.error)

    def import_rules(self):
        if self.lp_args.use_default_rules:
            rules_dirs = [self.default_rules_dir] + self.lp_args.rules_dirs
        else:
            rules_dirs = self.lp_args.rules_dirs or self.default_rules_dir

        self.rules = R.RulesCollection(create_from_dirs=rules_dirs)
        if self.lp_args.list_rules:
            print self.rules
            sys.exit(Linter.success)

        if self.lp_args.list_tags:
            print self.rules.listtags()
            sys.exit(Linter.success)
        #
        # if isinstance(options.tags, basestring):
        #     options.tags = options.tags.split(",")
        # if isinstance(options.skip_list, basestring):
        #     options.skip_list = options.skip_list.split(",")

    def run(self):
        self.import_rules()
        print self.lp_args


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
                if not isListTupleSet(target_classes):
                    target_classes = [target_classes]
                for _class in target_classes:
                    intercept(aspects)(_class)

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
        return self.format_errors()
