"""Dummy dataset to test runner"""

# pylint: disable=R0201,W0613


class DummyPrimaryConcern(object):
    """Dummy primary concern"""
    def true(self):
        """Notify inside function"""
        print "In true"


def before(*args, **kwargs):
    """Before advice"""
    print "Before true"


def after(*args, **kwargs):
    """After advice"""
    print "After true"


class DummyRule(object):
    """Test rule"""
    def __init__(self, errors):
        """Init rule with error container"""
        self.errors = errors

    @property
    def aspects(self):
        """Return aspects for the rule"""
        return {DummyPrimaryConcern: {r'true': dict(before=before, after_finally=after)}}
