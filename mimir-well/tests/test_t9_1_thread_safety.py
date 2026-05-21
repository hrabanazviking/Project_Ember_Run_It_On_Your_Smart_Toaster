"""T9-1: Thread Safety Tests — WyrdGraph threading.local, _write() lock, close().

Tests that WyrdGraph uses thread-local connections and that concurrent
operations on both RunaMemory and WyrdGraph are thread-safe.
"""

import os
import tempfile
import threading
import time
import unittest
from mimir_well import RunaMemory
from mimir_well.wyrd_graph import WyrdGraph


def _fresh_db():
    """Create a temporary database path that auto-cleans."""
    f = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    f.close()
    return f.name


class TestWyrdGraphThreadSafety(unittest.TestCase):
    """WyrdGraph should use thread-local connections."""

    def setUp(self):
        self.db_path = _fresh_db()
        self.graph = WyrdGraph(self.db_path)

    def tearDown(self):
        self.graph.close()
        os.unlink(self.db_path)

    def test_thread_local_connections(self):
        """Each thread should get its own connection via threading.local()."""
        conn_ids = []
        barriers = threading.Barrier(3, timeout=5)

        def get_conn_id():
            conn = self.graph._get_conn()
            conn_ids.append(id(conn))
            barriers.wait()

        threads = [threading.Thread(target=get_conn_id) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)

        # Each thread should have a different connection object
        self.assertEqual(len(conn_ids), 3, "All threads should get a connection")
        # At least 2 should be different (main thread may match one)
        self.assertGreaterEqual(len(set(conn_ids)), 2,
                                "Threads should use different connections")

    def test_concurrent_add_edges(self):
        """5 threads each adding 20 edges should not corrupt data."""
        errors = []

        def add_edges(thread_id):
            try:
                for i in range(20):
                    self.graph.add_edge(
                        f"node_{thread_id}", f"target_{i}",
                        f"rel_{thread_id}_{i}", strength=float(i),
                        user_id=f"user_{thread_id}"
                    )
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=add_edges, args=(t,)) for t in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)

        self.assertEqual(len(errors), 0, f"Thread errors: {errors}")
        # Should have 100 edges total (5 threads × 20)
        count = self.graph.edge_count()
        self.assertEqual(count, 100,
                         f"Expected 100 edges, got {count}") 

    def test_concurrent_reads_and_writes(self):
        """Mixed concurrent reads and writes should not crash."""
        errors = []

        def writer():
            for i in range(50):
                try:
                    self.graph.add_edge("w_node", f"w_target_{i}", f"w_rel_{i}",
                                        strength=float(i), user_id="writer")
                except Exception as e:
                    errors.append(str(e))

        def reader():
            for i in range(50):
                try:
                    self.graph.get_edges_from("w_node", user_id="writer")
                    self.graph.get_edges_to("w_target_0", user_id="writer")
                except Exception as e:
                    errors.append(str(e))

        threads = [
            threading.Thread(target=writer),
            threading.Thread(target=writer),
            threading.Thread(target=reader),
            threading.Thread(target=reader),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)

        self.assertEqual(len(errors), 0, f"Thread errors: {errors}")

    def test_close_clears_thread_local(self):
        """After close(), _local.conn should be None."""
        self.graph._get_conn()  # Ensure connection exists
        self.graph.close()
        conn = getattr(self.graph._local, 'conn', None)
        self.assertIsNone(conn, "close() should clear the thread-local connection")

    def test_close_is_idempotent(self):
        """Calling close() twice should not raise."""
        self.graph.close()
        self.graph.close()  # Should not raise


class TestRunaMemoryThreadSafety(unittest.TestCase):
    """RunaMemory._commit() should be thread-safe."""

    def setUp(self):
        self.db_path = _fresh_db()
        self.mem = RunaMemory(db_path=self.db_path)

    def tearDown(self):
        self.mem.close()
        os.unlink(self.db_path)

    def test_concurrent_decay_and_recall(self):
        """decay() (which uses _commit) and recall should not crash under concurrency."""
        # Add some memories first
        for i in range(20):
            self.mem.add_memory(f"test memory {i}", category="general",
                                importance=5 + (i % 5), user_id="thread_test")

        errors = []

        def decay_worker():
            try:
                for _ in range(5):
                    result = self.mem.decay(half_life_days=30, min_importance=1,
                                            user_id="thread_test")
                    self.assertIsInstance(result, dict)
            except Exception as e:
                errors.append(str(e))

        def recall_worker():
            try:
                for _ in range(10):
                    results = self.mem.recall_by_importance(min_importance=3,
                                                            limit=10,
                                                            user_id="thread_test")
                    self.assertIsInstance(results, list)
            except Exception as e:
                errors.append(str(e))

        threads = [
            threading.Thread(target=decay_worker),
            threading.Thread(target=decay_worker),
            threading.Thread(target=recall_worker),
            threading.Thread(target=recall_worker),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=15)

        self.assertEqual(len(errors), 0, f"Thread errors: {errors}")

    def test_concurrent_consolidate_and_recall(self):
        """consolidate() and recall should not crash under concurrency."""
        # Add memories with some access logs
        for i in range(20):
            self.mem.add_memory(f"consolidate test {i}", category="general",
                                importance=5 + (i % 3), user_id="con_test")

        errors = []

        def consolidate_worker():
            try:
                result = self.mem.consolidate(user_id="con_test")
                self.assertIsInstance(result, dict)
            except Exception as e:
                errors.append(str(e))

        def recall_worker():
            try:
                for _ in range(5):
                    self.mem.recall_by_importance(min_importance=3, limit=10,
                                                  user_id="con_test")
            except Exception as e:
                errors.append(str(e))

        threads = [
            threading.Thread(target=consolidate_worker),
            threading.Thread(target=consolidate_worker),
            threading.Thread(target=recall_worker),
            threading.Thread(target=recall_worker),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=15)

        self.assertEqual(len(errors), 0, f"Thread errors: {errors}")

    def test_close_is_idempotent_memory(self):
        """Calling RunaMemory.close() twice should not raise."""
        self.mem.close()
        self.mem.close()  # Should not raise


if __name__ == "__main__":
    unittest.main()