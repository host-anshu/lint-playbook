"""Test composite queue and multiprocessing queue override"""

import multiprocessing
import unittest

from Queue import Empty

from linter.utils.composite_queue import CompositeQueue

multiprocessing.Queue = CompositeQueue


class CompositeQueueTest(unittest.TestCase):
    """Should test if composite queue refers to two queues based on kwarg interceptor"""
    def setUp(self):
        self.q_obj = CompositeQueue()

    def test_put_and_size(self):
        """Should test if put and size work on respective queues"""
        # qsize must be zero for both q.
        self.assertEqual(self.q_obj.ansible_q.qsize(), 0)
        self.assertEqual(self.q_obj.qsize(), 0)  # Abstract reference to ansible_q
        self.assertEqual(self.q_obj.interceptor_q.qsize(), 0)
        self.assertEqual(
            self.q_obj.qsize(interceptor=True), 0)  # Abstract reference to interceptor_q
        # Add to ansible_q
        self.q_obj.put(1)
        # qsize must be 1 for ansible_q
        self.assertEqual(self.q_obj.ansible_q.qsize(), 1)
        self.assertEqual(self.q_obj.qsize(), 1)  # Abstract reference to ansible_q
        # qsize must be 0 for interceptor_q
        self.assertEqual(self.q_obj.interceptor_q.qsize(), 0)
        self.assertEqual(
            self.q_obj.qsize(interceptor=True), 0)  # Abstract reference to interceptor_q
        # Add to interceptor_q
        self.q_obj.put(1, interceptor=True)
        # qsize must be 1 for ansible_q
        self.assertEqual(self.q_obj.ansible_q.qsize(), 1)
        self.assertEqual(self.q_obj.qsize(), 1)  # Abstract reference to ansible_q
        # qsize must be 1 for interceptor_q
        self.assertEqual(self.q_obj.interceptor_q.qsize(), 1)
        self.assertEqual(
            self.q_obj.qsize(interceptor=True), 1)  # Abstract reference to interceptor_q

    def test_get(self):
        """Should test if get works on respective queues"""
        # qsize must be zero for both q.
        self.assertEqual(self.q_obj.ansible_q.qsize(), 0)
        self.assertEqual(self.q_obj.qsize(), 0)  # Abstract reference to ansible_q
        self.assertEqual(self.q_obj.interceptor_q.qsize(), 0)
        self.assertEqual(
            self.q_obj.qsize(interceptor=True), 0)  # Abstract reference to interceptor_q
        # Get must raise exception on both q.
        self.assertRaises(Empty, self.q_obj.get, block=False)
        self.assertRaises(Empty, self.q_obj.get, block=False, interceptor=True)
        # Add to ansible_q
        self.q_obj.put(1)
        # Get from interceptor_q must raise exception
        self.assertRaises(Empty, self.q_obj.get, block=False, interceptor=True)
        # Get from ansible_q should work
        self.assertEqual(self.q_obj.get(), 1)
        # Add to interceptor_q
        self.q_obj.put(1, interceptor=True)
        # Get from ansible_q must raise exception
        self.assertRaises(Empty, self.q_obj.get, block=False)
        # Get from ansible_q should work
        self.assertEqual(self.q_obj.get(interceptor=True), 1)

    def test_close(self):
        """Should test if close works on respective queues"""
        # Both q open
        self.assertFalse(self.q_obj.ansible_q._closed)
        self.assertFalse(self.q_obj.interceptor_q._closed)
        # Close ansible_q
        self.q_obj.close()
        self.assertTrue(self.q_obj.ansible_q._closed)  # ansible_q closed
        self.assertFalse(self.q_obj.interceptor_q._closed)  # interceptor_q open
        # Close interceptor_q
        self.q_obj.close(interceptor=True)
        # Both q closed
        self.assertTrue(self.q_obj.ansible_q._closed)
        self.assertTrue(self.q_obj.interceptor_q._closed)


class MultiprocessingQueueOverrideTest(CompositeQueueTest):
    """Should test if multiprocessing.Queue gets replaced by CompositeQueue"""
    def setUp(self):
        self.q_obj = multiprocessing.Queue()


if __name__ == '__main__':
    unittest.main()
