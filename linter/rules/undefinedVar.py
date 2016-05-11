"""Undefined variable rule"""

import inspect

from ansible.errors import AnsibleUndefinedVariable
from ansible.plugins.strategy import StrategyBase  # pylint: disable=E0611,F0401
from ansible.executor.task_queue_manager import TaskQueueManager  # pylint: disable=E0611,F0401
from ansible.executor.process.worker import WorkerProcess  # pylint: disable=E0611,F0401

from Queue import Empty

# Interceptor internal method names to be skipped while backtracking through call stack.
INTERCEPTOR_INTERNAL_METHODS = {'run_advices', 'trivial'}
# Composite queue internal method names to be skipped for while backtracking through call stack.
COMPOSITE_QUEUE_INTERNAL_METHODS = {'meth', 'get_instance_attr'}
SKIP_METHODS = INTERCEPTOR_INTERNAL_METHODS.union(COMPOSITE_QUEUE_INTERNAL_METHODS)


def queue_exc(*arg, **kw):  # pylint: disable=W0613
    """Queue undefined variable exception"""
    _self = arg[0]
    if not isinstance(_self, AnsibleUndefinedVariable):
        # Run for AnsibleUndefinedVariable instance
        return
    _rslt_q = None
    for stack_trace in inspect.stack():
        # Check if method to be skipped
        if stack_trace[3] in SKIP_METHODS:
            continue
        _frame = stack_trace[0]
        _locals = inspect.getargvalues(_frame).locals
        if 'self' not in _locals:
            continue
        # Check if current frame instance of worker
        if isinstance(_locals['self'], WorkerProcess):
            # Get queue to add exception
            _rslt_q = getattr(_locals['self'], '_rslt_q')
    if not _rslt_q:
        raise ValueError("No Queue found.")
    _rslt_q.put(arg[3].message, interceptor=True)


def extract_worker_exc(errors):
    """Get the exceptions added by the workers"""
    def method(*arg, **kw):  # pylint: disable=W0613
        """Reference the advice and run with the data store"""
        _self = arg[0]
        if not isinstance(_self, StrategyBase):
            # Run for StrategyBase instance only
            return
        # Iterate over workers to get their task and queue
        for _worker in _self._workers:
            try:
                # Ansible 2.0.0
                _worker_prc, _main_q, _rslt_q = _worker
            except ValueError:
                # Ansible 2.0.2
                _worker_prc, _rslt_q = _worker
            try:
                _task = _worker_prc._task
            except AttributeError:
                # No worker. Probably the task encountered error.
                continue
            if _task.action == 'setup':
                # Ignore setup
                continue
            # Do till queue is empty for the worker
            while True:
                try:
                    _exc = _rslt_q.get(block=False, interceptor=True)
                    if "unused_vars" in _exc:
                        errors["unused_vars"] = errors["unused_vars"].union(_exc["unused_vars"])
                        continue
                    errors[_task.name].add(_exc)
                except Empty:
                    break
    return method


def extract_setup_failures(errors):
    """Extract failures that occur while setup"""
    def method(*arg, **kw):  # pylint: disable=W0613
        """Reference to advice"""
        try:
            result = arg[4]
        except IndexError:
            return
        try:
            _host, _task, _result = result._host, result._task, result._result
        except AttributeError:
            return
        if _task.action == "setup":
            for state in ("failed", "unreachable"):
                if state in _result:
                    errors["setup"].add("Host %s: %s: %s" % (_host.name, state, _result["msg"]))
    return method


class UndefinedVariable(object):
    """Undefined variable rule.

    Whenever the AnsibleUndefinedVariable exception is generated while playbook runs, the
    exception is queued in the composite queue pertaining to interceptor. And after all of the
    workers are run, they are extracted and stored in the data store.
    """
    def __init__(self, errors):
        """Initialise data store"""
        self.errors = errors

    @property
    def aspects(self):
        """Get aspects"""
        return {
            AnsibleUndefinedVariable: {
                r'__init__': dict(
                    around_after=queue_exc
                )},
            StrategyBase: {
                r'\brun\b': dict(
                    before=extract_worker_exc(self.errors)  # bind data store
                )},
            TaskQueueManager: {
                r'\bsend_callback\b': dict(before=extract_setup_failures(self.errors))
            }
        }
