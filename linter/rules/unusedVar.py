"""Rule to detect unused vars in playbook."""

import collections

from ansible.executor.task_executor import TaskExecutor  # pylint: disable=E0611,F0401
from copy import deepcopy


def cache_key_gets(*arg, **kw):  # pylint: disable=W0613
    """Capture all the vars for the task which get accessed.

    Override the task var to add all the keys to a set that can be read later to find the ones
    which haven't been accessed resulting in unused variables set.
    """
    class TransformedDict(collections.MutableMapping):
        """A dictionary that adds keys accessed to a set bound to the worker instance."""

        def __init__(self, *args, **kwargs):
            self.store = dict()
            self.update(dict(*args, **kwargs))  # use the free update to set keys

        def __getitem__(self, key):
            _self.keys_accessed.add(key)
            return self.store[key]

        def __setitem__(self, key, value):
            self.store[key] = value

        def __delitem__(self, key):
            del self.store[key]

        def __iter__(self):
            return iter(self.store)

        def __len__(self):
            return len(self.store)

        def copy(self):
            """Return copy of dict. Ansible fails if this not added."""
            return self.store.copy()

    def recursively_override(inp):
        """Iterate over input dictionary recursively to override its get behavior"""
        for k, v in inp.iteritems():
            if isinstance(v, dict):
                inp[k] = recursively_override(v)
        return TransformedDict(**inp)

    _self = arg[0]
    if _self._task.action == "setup":
        return
    # _self._job_vars = TransformedDict(**_self._job_vars)
    _self._job_vars = recursively_override(_self._job_vars)
    setattr(_self, "keys_accessed", set())


def queue_unused(*arg, **kw):  # pylint: disable=W0613
    """If unused variable for the task, enqueue it

    Before advice must have prepared set of method names that have been accessed in _job_vars.
    Use host's host_vars and group_vars to find the ones which haven't been accessed and add to
    the interceptor queue.
    """
    def find_unused(inp_dict):
        """Find if keys in dict are unused"""
        for key in inp_dict:
            if key not in used:
                unused.add(key)
            # TODO: Advanced search for unused var.
            # if isinstance(value, dict):
            #     find_unused(value)

    _self = arg[0]
    if _self._task.action == "setup":
        return
    unused, used = set(), deepcopy(_self.keys_accessed)
    host = _self._host
    host_vars, group_vars = host.vars, host.get_group_vars()
    group_vars.update(host_vars)
    find_unused(group_vars)
    if len(unused):
        _self._rslt_q.put({"unused_vars": unused}, interceptor=True)


class UnusedVariable(object):
    """Find host and group vars that aren't being used by the tasks."""
    def __init__(self, errors):
        """Initialise data store"""
        self.errors = errors

    aspects = {
        TaskExecutor: {
            r"run": dict(
                before=cache_key_gets,
                after_finally=queue_unused
            )}
    }
