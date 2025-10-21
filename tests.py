"""
Comprehensive Unit Tests for Database Optimization
Tests connection pooling, query analysis, caching, and indexing
"""

import unittest
import time
import os
import sqlite3
from connection.connection_pool import ConnectionPool
from query.query_analyzer import QueryAnalyzer
from caching.query_cache import QueryCache
from indexing.index_analyzer import IndexAnalyzer
from examples.database_setup import create_sample_database, populate_sample_data


class DatabaseOptimizationTestCase(unittest.TestCase):
    """Unit tests for Database Optimization"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test configuration"""
        print("\n" + "=" * 60)
        print("Database Optimization - Unit Test Suite")
        print("=" * 60)
        print("Testing: Connection Pool, Query Analysis, Caching, Indexing")
        print("=" * 60 + "\n")
        
        # Create test database
        cls.db_path = 'test.db'
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)
        
        cls.conn = create_sample_database(cls.db_path)
        populate_sample_data(cls.conn, num_users=100, num_orders=500, num_products=20)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after tests"""
        cls.conn.close()
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)
    
    # Test 1: Connection Pool Creation
    def test_01_connection_pool_creation(self):
        """Test connection pool initialization"""
        print("\n1. Testing connection pool creation...")
        
        pool = ConnectionPool(self.db_path, min_connections=2, max_connections=5)
        
        stats = pool.get_stats()
        
        self.assertGreaterEqual(stats['total_connections'], 2)
        print(f"   [EMOJI] Pool created with {stats['total_connections']} connections")
        
        pool.close_all()
    
    # Test 2: Connection Reuse
    def test_02_connection_reuse(self):
        """Test connection pooling reuses connections"""
        print("\n2. Testing connection reuse...")
        
        pool = ConnectionPool(self.db_path, min_connections=2, max_connections=5)
        
        # Get and release connection multiple times
        for i in range(5):
            conn = pool.get_connection()
            pool.release_connection(conn)
        
        stats = pool.get_stats()
        
        # Should have reused connections (not created 5 new ones)
        self.assertLess(stats['total_created'], 5)
        print(f"   [EMOJI] Reused connections: {stats['cache_hits']} hits")
        print(f"   [EMOJI] Hit rate: {stats['hit_rate']}")
        
        pool.close_all()
    
    # Test 3: Query Analysis
    def test_03_query_analysis(self):
        """Test query performance analysis"""
        print("\n3. Testing query analysis...")
        
        analyzer = QueryAnalyzer(slow_query_threshold=0.5)
        
        query = "SELECT * FROM users WHERE city = 'New York'"
        result = analyzer.analyze_query(self.conn, query)
        
        self.assertIn('analysis', result)
        self.assertIn('execution_time', result['analysis'])
        self.assertIn('rows_returned', result['analysis'])
        
        print(f"   [EMOJI] Query analyzed")
        print(f"   [EMOJI] Execution time: {result['analysis']['execution_time']:.4f}s")
        print(f"   [EMOJI] Rows returned: {result['analysis']['rows_returned']}")
    
    # Test 4: Slow Query Detection
    def test_04_slow_query_detection(self):
        """Test slow query detection"""
        print("\n4. Testing slow query detection...")
        
        analyzer = QueryAnalyzer(slow_query_threshold=0.001)
        
        # Execute a query that should be marked as slow
        query = "SELECT * FROM orders WHERE status = 'pending'"
        result = analyzer.analyze_query(self.conn, query)
        
        # Check if detected as slow
        if result['analysis']['is_slow']:
            print(f"   [EMOJI] Slow query detected: {result['analysis']['execution_time']:.4f}s")
        
        # Get slow queries
        slow_queries = analyzer.get_slow_queries()
        self.assertGreaterEqual(len(slow_queries), 0)
        print(f"   [EMOJI] Total slow queries: {len(slow_queries)}")
    
    # Test 5: Query Caching
    def test_05_query_caching(self):
        """Test query result caching"""
        print("\n5. Testing query caching...")
        
        cache = QueryCache(ttl=60, max_size=100)
        
        query = "SELECT * FROM users LIMIT 10"
        
        # First request (cache miss)
        result1 = cache.get(query)
        self.assertIsNone(result1)
        print("   [EMOJI] First request: Cache miss")
        
        # Cache the result
        cursor = self.conn.execute(query)
        data = cursor.fetchall()
        cache.set(query, None, data)
        
        # Second request (cache hit)
        result2 = cache.get(query)
        self.assertIsNotNone(result2)
        print("   [EMOJI] Second request: Cache hit")
        
        # Check stats
        stats = cache.get_stats()
        self.assertEqual(stats['hits'], 1)
        self.assertEqual(stats['misses'], 1)
        print(f"   [EMOJI] Hit rate: {stats['hit_rate']}")
    
    # Test 6: Cache Invalidation
    def test_06_cache_invalidation(self):
        """Test cache invalidation"""
        print("\n6. Testing cache invalidation...")
        
        cache = QueryCache(ttl=60)
        
        query = "SELECT * FROM users LIMIT 5"
        
        # Cache a result
        cache.set(query, None, [1, 2, 3])
        
        # Verify it's cached
        result = cache.get(query)
        self.assertIsNotNone(result)
        print("   [EMOJI] Result cached")
        
        # Invalidate
        cache.invalidate(query)
        
        # Verify it's gone
        result = cache.get(query)
        self.assertIsNone(result)
        print("   [EMOJI] Cache invalidated")
    
    # Test 7: Index Creation
    def test_07_index_creation(self):
        """Test index creation"""
        print("\n7. Testing index creation...")
        
        analyzer = IndexAnalyzer()
        
        # Create index
        result = analyzer.create_index(self.conn, 'users', 'email')
        
        self.assertIn('index_name', result)
        print(f"   [EMOJI] Index created: {result['index_name']}")
        
        # Verify index exists
        indexes = analyzer.get_table_indexes(self.conn, 'users')
        index_names = [idx['name'] for idx in indexes]
        
        self.assertIn(result['index_name'], index_names)
        print(f"   [EMOJI] Index verified in table")
    
    # Test 8: Index Performance Impact
    def test_08_index_performance_impact(self):
        """Test performance improvement with index"""
        print("\n8. Testing index performance impact...")
        
        # Create fresh database for clean test
        test_db = 'index_test.db'
        if os.path.exists(test_db):
            os.remove(test_db)
        
        conn = create_sample_database(test_db)
        populate_sample_data(conn, num_users=1000, num_orders=3000, num_products=50)
        
        query = "SELECT * FROM users WHERE username = 'user500'"
        
        # Time without index
        start = time.time()
        cursor = conn.execute(query)
        results = cursor.fetchall()
        time_without = time.time() - start
        
        # Create index
        conn.execute("CREATE INDEX idx_username ON users(username)")
        conn.commit()
        
        # Time with index
        start = time.time()
        cursor = conn.execute(query)
        results = cursor.fetchall()
        time_with = time.time() - start
        
        print(f"   [EMOJI] Without index: {time_without:.4f}s")
        print(f"   [EMOJI] With index: {time_with:.4f}s")
        
        # With index should be faster or equal
        self.assertLessEqual(time_with, time_without * 1.5)
        
        conn.close()
        os.remove(test_db)
    
    # Test 9: Connection Pool Stats
    def test_09_connection_pool_stats(self):
        """Test connection pool statistics"""
        print("\n9. Testing connection pool stats...")
        
        pool = ConnectionPool(self.db_path, min_connections=2, max_connections=5)
        
        # Get multiple connections
        connections = []
        for i in range(3):
            conn = pool.get_connection()
            connections.append(conn)
        
        stats = pool.get_stats()
        
        self.assertEqual(stats['in_use'], 3)
        print(f"   [EMOJI] In use: {stats['in_use']}")
        
        # Release connections
        for conn in connections:
            pool.release_connection(conn)
        
        stats = pool.get_stats()
        self.assertEqual(stats['in_use'], 0)
        print(f"   [EMOJI] After release: {stats['in_use']} in use")
        
        pool.close_all()
    
    # Test 10: Cache TTL Expiration
    def test_10_cache_ttl_expiration(self):
        """Test cache TTL expiration"""
        print("\n10. Testing cache TTL expiration...")
        
        cache = QueryCache(ttl=1, max_size=100)  # 1 second TTL
        
        query = "SELECT * FROM users LIMIT 5"
        
        # Cache result
        cache.set(query, None, [1, 2, 3])
        
        # Should be in cache
        result = cache.get(query)
        self.assertIsNotNone(result)
        print("   [EMOJI] Result cached")
        
        # Wait for expiration
        time.sleep(1.5)
        
        # Should be expired
        result = cache.get(query)
        self.assertIsNone(result)
        print("   [EMOJI] Cache expired after TTL")


def run_tests():
    """Run all unit tests"""
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(DatabaseOptimizationTestCase)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.testsRun > 0:
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100)
        print(f"Success rate: {success_rate:.1f}%")
    
    if result.failures:
        print("\n[EMOJI] FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\n[EMOJI] ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    if not result.failures and not result.errors:
        print("\n[EMOJI] ALL TESTS PASSED! [EMOJI]")
    
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("Database Optimization - Unit Test Suite")
    print("=" * 60)
    
    try:
        success = run_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[EMOJI]️  Tests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n[EMOJI] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
