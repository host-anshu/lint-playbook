"""Rule to lint playbook for variables that are same if their cases and special characters in
them are ignored.
"""

import re

from ansible.executor.task_executor import TaskExecutor  # pylint: disable=E0611,F0401
# from ansible.plugins.strategy import StrategyBase  # pylint: disable=E0611,F0401
from collections import defaultdict


def queue_conflicting_vars(*arg, **kw):  # pylint: disable=W0613
    """If conflicting vars enqueue them.

    Advice to find vars that are same if their case and special characters in them are ignored.
    """
    def get_nested_keys(inp):
        """recursively get all keys for the dictionary"""
        for key, val in inp.iteritems():
            if isinstance(val, dict):
                for _key in get_nested_keys(val):
                    # TODO: Fully qualify the key?
                    yield _key
            yield key

    def normalize(var):
        """Normalize variable by changing it to lower case and removing its special characters"""
        return re.sub(r"[_-]", "", var).lower()

    _self = arg[0]
    if _self._task.action == "setup":
        return
    conflicting = defaultdict(set)
    host = _self._host
    var_collections = host.vars, host.get_group_vars()
    for _vars in var_collections:
        for var in get_nested_keys(_vars):
            conflicting[normalize(var)].add(var)
    conflicting = set([", ".join(_vars) for _vars in conflicting.itervalues() if len(_vars) > 1])
    if len(conflicting):
        _self._rslt_q.put({"conflicting_vars": conflicting}, interceptor=True)


# def hosts_conflicting_vars(errors):
#     """If conflicting vars enqueue them.
#
#     Advice to find vars that are same if their case and special characters in them are ignored.
#     """
#     def meth(*arg, **kw):  # pylint: disable=W0613
#         def get_nested_keys(inp):
#             """recursively get all keys for the dictionary"""
#             for k, v in inp.iteritems():
#                 if isinstance(v, dict):
#                     for _k in get_nested_keys(v):
#                         # TODO: Fully qualify the key?
#                         yield _k
#                 yield k
#
#         def normalize(var):
#             """Normalize variable by changing it to lower case and removing its special
#             characters
#             """
#             return re.sub(r"[_-]", "", var).lower()
#
#         _task = arg[4]
#         if _task.action == "setup":
#             return
#         _self, host = arg[0], arg[3]
#         try:
#             if host.name in _self.evaluated:
#                 return
#         except AttributeError:
#             pass
#         conflicting = defaultdict(set)
#         var_collections = host.vars, host.get_group_vars()
#         for vars in var_collections:
#             for var in get_nested_keys(vars):
#                 conflicting[normalize(var)].add(var)
#
#         for _vars in conflicting.itervalues():
#             if len(_vars) > 1:
#                 errors["conflicting_vars"].add(", ".join(_vars))
#         setattr(_self, "evaluated", set(host.name))
#     return meth


class ConflictingVar(object):
    """Find host and group vars that aren't being used by the tasks."""
    def __init__(self, errors):
        """Initialise data store"""
        self.errors = errors

    aspects = {
        TaskExecutor: {
            r"__init__": dict(
                after_finally=queue_conflicting_vars
            )},
    }

    # @property
    # def aspects(self):
    #     return {
    #         StrategyBase: {
    #             r"\b_queue_task\b": dict(
    #                 before=hosts_conflicting_vars(self.errors),
    #             )
    #         }
    #     }
