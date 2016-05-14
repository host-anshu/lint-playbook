import imp
import inspect
import os
import re

from abc import ABCMeta, abstractproperty
from collections import defaultdict

from linter.utils import isListTupleSet


class RulesCollection(object):

    def __init__(self, create_from_dirs=None):
        self.rules = []
        if create_from_dirs:
            self.create_from_directory(create_from_dirs)

    def register(self, obj):
        self.rules.append(obj)

    def __iter__(self):
        return iter(self.rules)

    def __len__(self):
        return len(self.rules)

    def extend(self, more):
        self.rules.extend(more)

    def apply(self, tags=set(), skip_list=set()):
        for rule in self.rules:
            if not tags or not set(rule.tags).union([rule.id]).isdisjoint(tags):
                rule_definition = set(rule.tags)
                rule_definition.add(rule.id)
                if set(rule_definition).isdisjoint(skip_list):
                    rule.apply()

    def __repr__(self):
        return "\n".join([rule.verbose()
                          for rule in sorted(self.rules, key=lambda x: x.id)])

    def listtags(self):
        tags = defaultdict(list)
        for rule in self.rules:
            for tag in rule.tags:
                tags[tag].append("[{0}]".format(rule.id))
        results = []
        for tag in sorted(tags):
            results.append("{0} {1}".format(tag, tags[tag]))
        return "\n".join(results)

    @staticmethod
    def load_rules_from_dir(rule_dir):
        # Make issubclass work. There is namespace difference than the LintRule in this module.
        from linter.rules import LintRule
        rules, handled = [], set()
        for root, dirs, files in os.walk(rule_dir):
            for _file in files:
                if _file.endswith(".pyc"):
                    continue
                mod_name = _file.replace(".py", "")
                try:
                    fh, filename, desc = imp.find_module(mod_name, [root])
                    mod_obj = imp.load_module(mod_name, fh, filename, desc)
                except ImportError:
                    fh = None
                    continue
                finally:
                    if fh:
                        fh.close()
                for _name in dir(mod_obj):
                    if _name in handled:
                        continue
                    handled.add(_name)
                    obj = getattr(mod_obj, _name)
                    if obj == LintRule:
                        continue
                    if not inspect.isclass(obj):
                        continue
                    if issubclass(obj, LintRule):
                        rules.append(obj)
        return rules

    def create_from_directory(self, rules_dirs):
        if isinstance(rules_dirs, basestring):
            rules_dirs = [rules_dirs]
        elif not isListTupleSet(rules_dirs):
            raise ValueError(
                "Expected a list of directories containing rules. Got: %s" % type(rules_dirs))

        for rule_dir in rules_dirs:
            self.extend(self.load_rules_from_dir(rule_dir))


class LintRule(object):
    class __metaclass__(ABCMeta):
        @property
        def description(cls):
            return cls.__doc__

        @property
        def formatted_id(cls):
            try:
                return 'R%02d' % cls.id
            except TypeError:
                raise TypeError("Rule id must be a unique integer.")

        @property
        def valid_code(cls):
            """Code must be a str of min length 2, lower alphabets and underscore if required."""
            try:
                code = re.match(r'(^[a-z][a-z_]*[a-z]$)', cls.code).group(1)
            except TypeError:
                raise TypeError(LintRule.valid_code.__doc__)
            except AttributeError:
                raise ValueError(LintRule.valid_code.__doc__)
            return code

        @property
        def valid_tags(cls):
            """Tags must be a list or tuple or set of keywords"""
            if not isListTupleSet(cls.tags):
                raise TypeError(LintRule.valid_tags.__doc__)
            return cls.tags

    def id(self):
        raise NotImplementedError("You must implement unique integer ID in your rule")

    def code(self):
        raise NotImplementedError(
            "You must implement unique string code, with no whitespace, in your rule.")

    def short_desc(self):
        raise NotImplementedError("You must add a short description for your rule")

    def aspects(self):
        raise NotImplementedError("You must implement aspects for your rule")

    # This signature helps autocomplete.
    id = abstractproperty(id)
    code = abstractproperty(code)
    short_desc = abstractproperty(short_desc)
    aspects = abstractproperty(aspects)
    tags = []

    def __repr__(self):
        return "%s(%s): %s" % (self.valid_code, self.formatted_id, self.short_desc)

    @classmethod
    def verbose(cls):
        return "%s(%s): %s\n%s" % (
            cls.valid_code, cls.formatted_id, cls.short_desc, cls.description)
