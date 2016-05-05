"""Composite queue to conditionally store ansible and interceptor data"""

from multiprocessing import Queue


class CompositeQueue(object):
    """Queue to store interceptor data without intervening ansible workflow"""
    def __init__(self, *args, **kwargs):
        """Initialise a queue referring to the ansible or the interceptor queue conditionally"""
        self.interceptor_q = Queue(*args, **kwargs)
        self.ansible_q = Queue(*args, **kwargs)

    def __getattr__(self, item):
        """Separate method calls for ansible and interceptor queues."""
        def meth(*args, **kw):
            """Get method corresponding to the right queue, based on the "interceptor" kwarg"""
            def get_instance_attr(obj):
                """common operation for either queue"""
                attr = getattr(obj, item)
                if callable(attr):
                    return attr(*args, **kw)
                return attr

            if kw.get('interceptor', False):
                # Remove the unknown kwarg for multiprocess
                del kw['interceptor']
                return get_instance_attr(self.interceptor_q)
            else:
                return get_instance_attr(self.ansible_q)
        return meth
