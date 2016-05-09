"""Utilities"""


import os
import sys
from functools import wraps


def suppressConsoleOut(meth):
    """Disable stdout and stderr during the method is run."""
    @wraps(meth)
    def decorate(*args, **kwargs):
        """Decorate"""
        # Disable console output
        _stdout = sys.stdout
        _stderr = sys.stderr
        fptr = open(os.devnull, 'w')
        sys.stdout = fptr
        sys.stderr = fptr
        try:
            return meth(*args, **kwargs)
        finally:
            # Enable console output
            sys.stdout = _stdout
            sys.stderr = _stderr
    return decorate


def isLTS(obj):
    """Check if instance of list, tuple, set"""
    return isinstance(obj, (list, tuple, set))
