"""Utilities"""


import os
import sys
from functools import wraps


def suppressConsoleOut(meth):
    """Disable console output during the method is run."""
    @wraps(meth)
    def decorate(self, *args, **kwargs):
        """Decorate"""
        # Disable ansible console output
        _stdout = sys.stdout
        fptr = open(os.devnull, 'w')
        sys.stdout = fptr
        try:
            return meth(self, *args, **kwargs)
        finally:
            # Enable console output
            sys.stdout = _stdout
    return decorate


def isLTS(obj):
    """Check if instance of list, tuple, set"""
    return isinstance(obj, (list, tuple, set))
