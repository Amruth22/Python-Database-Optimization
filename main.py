"""
Database Optimization - Main Demonstration
Shows examples of all database optimization features
"""

import time
import os
from connection.connection_pool import ConnectionPool
from query.query_analyzer import QueryAnalyzer
from caching.query_cache import QueryCache
from indexing.index_analyzer import IndexAnalyzer
from examples.database_setup import create_sample_database, populate_sample_data, get_table_stats


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_connection_pool():
    """Demonstrate connection pooling"""
    print_section("1. Connection Pooling - Reuse Connections")
    
    # Create database
    db_path = 'demo.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = create_sample_database(db_path)
    populate_sample_data(conn, num_users=100, num_orders=500, num_products=50)
    conn.close()
    
    # Create connection pool
    pool = ConnectionPool(db_path, min_connections=2, max_connections=5)
    
    print("\n📊 Connection Pool Stats:")
    stats = pool.get_stats()
    print(f"   Total connections: {stats['total_connections']}")
    print(f"   Available: {stats['available']}")
    print(f"   In use: {stats['in_use']}")
    
    # Use connections
    print("\n🔄 Getting connections from pool:")
    connections = []
    for i in range(3):
        conn = pool.get_connection()
        connections.append(conn)
        print(f"   Connection {i+1} acquired")
    
    stats = pool.get_stats()
    print(f"\n📊 After acquiring 3 connections:")
    print(f"   Available: {stats['available']}")
    print(f"   In use: {stats['in_use']}")
    
    # Release connections
    for conn in connections:
        pool.release_connection(conn)
    
    print("\n✅ Connections released back to pool")
    
    pool.close_all()


def demo_query_analysis():
    """Demonstrate query analysis"""
    print_section("2. Query Analysis - Performance Measurement")
    
    # Setup database
    db_path = 'demo.db'
    conn = create_sample_database(db_path)
    populate_sample_data(conn, num_users=1000, num_orders=5000, num_products=100)
    
    analyzer = QueryAnalyzer(slow_query_threshold=0.1)
    
    # Analyze a query
    print("\n🔍 Analyzing query performance:")
    query = "SELECT * FROM users WHERE city = 'New York'"
    
    result = analyzer.analyze_query(conn.connection, query)
    analysis = result['analysis']
    
    print(f"   Query: {query}")
    print(f"   Execution time: {analysis['execution_time']:.4f}s")
    print(f"   Rows returned: {analysis['rows_returned']}")
    print(f"   Slow query: {'Yes' if analysis['is_slow'] else 'No'}")
    
    # Get stats
    print("\n📊 Query Statistics:")
    stats = analyzer.get_query_stats()
    print(f"   Total queries: {stats['total_queries']}")
    print(f"   Slow queries: {stats['slow_queries']}")
    print(f"   Avg execution time: {stats['avg_execution_time']}")
    
    conn.close()


def demo_query_caching():
    """Demonstrate query caching"""
    print_section("3. Query Caching - Reduce Database Load")
    
    cache = QueryCache(ttl=60, max_size=100)
    
    # Setup database
    db_path = 'demo.db'
    conn = create_sample_database(db_path)
    populate_sample_data(conn, num_users=500, num_orders=2000, num_products=50)
    
    query = "SELECT * FROM users WHERE city = 'Chicago'"
    
    # First request (cache miss)
    print("\n🔍 First request (cache miss):")
    start = time.time()
    cached_result = cache.get(query)
    
    if cached_result is None:
        cursor = conn.execute(query)
        result = cursor.fetchall()
        cache.set(query, None, result)
        print(f"   ❌ Cache miss - Query executed in {time.time() - start:.4f}s")
    
    # Second request (cache hit)
    print("\n🔍 Second request (cache hit):")
    start = time.time()
    cached_result = cache.get(query)
    
    if cached_result is not None:
        print(f"   ✅ Cache hit - Retrieved in {time.time() - start:.6f}s")
    
    # Get cache stats
    print("\n📊 Cache Statistics:")
    stats = cache.get_stats()
    print(f"   Cache size: {stats['cache_size']}")
    print(f"   Hits: {stats['hits']}")
    print(f"   Misses: {stats['misses']}")
    print(f"   Hit rate: {stats['hit_rate']}")
    
    conn.close()


def demo_indexing():
    """Demonstrate database indexing"""
    print_section("4. Database Indexing - Speed Up Queries")
    
    # Setup database
    db_path = 'demo.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = create_sample_database(db_path)
    populate_sample_data(conn, num_users=5000, num_orders=10000, num_products=100)
    
    analyzer = IndexAnalyzer()
    
    # Test query without index
    print("\n🐌 Query WITHOUT index:")
    query = "SELECT * FROM users WHERE email = 'user500@example.com'"
    
    start = time.time()
    cursor = conn.execute(query)
    results = cursor.fetchall()
    time_without = time.time() - start
    
    print(f"   Query: {query}")
    print(f"   Time: {time_without:.4f}s")
    print(f"   Rows: {len(results)}")
    
    # Create index
    print("\n📊 Creating index on email column...")
    index_info = analyzer.create_index(conn, 'users', 'email')
    print(f"   Index created: {index_info['index_name']}")
    
    # Test query with index
    print("\n🚀 Query WITH index:")
    start = time.time()
    cursor = conn.execute(query)
    results = cursor.fetchall()
    time_with = time.time() - start
    
    print(f"   Query: {query}")
    print(f"   Time: {time_with:.4f}s")
    print(f"   Rows: {len(results)}")
    
    # Show improvement
    speedup = time_without / time_with if time_with > 0 else 0
    print(f"\n✅ Performance Improvement:")
    print(f"   Speedup: {speedup:.2f}x faster")
    print(f"   Time saved: {(time_without - time_with):.4f}s")
    
    conn.close()


def demo_query_optimization():
    """Demonstrate query optimization"""
    print_section("5. Query Optimization - Write Better Queries")
    
    # Setup database
    db_path = 'demo.db'
    conn = create_sample_database(db_path)
    populate_sample_data(conn, num_users=2000, num_orders=5000, num_products=100)
    
    analyzer = QueryAnalyzer()
    
    # Slow query (SELECT *)
    print("\n🐌 Slow Query (SELECT *):")
    slow_query = "SELECT * FROM users WHERE city = 'New York'"
    
    start = time.time()
    cursor = conn.execute(slow_query)
    results = cursor.fetchall()
    slow_time = time.time() - start
    
    print(f"   Query: {slow_query}")
    print(f"   Time: {slow_time:.4f}s")
    
    # Optimized query (SELECT specific columns)
    print("\n🚀 Optimized Query (SELECT specific columns):")
    fast_query = "SELECT id, username, email FROM users WHERE city = 'New York'"
    
    start = time.time()
    cursor = conn.execute(fast_query)
    results = cursor.fetchall()
    fast_time = time.time() - start
    
    print(f"   Query: {fast_query}")
    print(f"   Time: {fast_time:.4f}s")
    
    # Compare
    comparison = analyzer.compare_queries(conn, slow_query, fast_query)
    print(f"\n✅ Comparison:")
    print(f"   Speedup: {comparison['speedup']}")
    print(f"   Faster: {comparison['faster']}")
    
    conn.close()


def demo_explain_query():
    """Demonstrate EXPLAIN QUERY PLAN"""
    print_section("6. EXPLAIN QUERY PLAN - Understand Query Execution")
    
    # Setup database
    db_path = 'demo.db'
    conn = create_sample_database(db_path)
    populate_sample_data(conn, num_users=1000, num_orders=3000, num_products=50)
    
    analyzer = QueryAnalyzer()
    
    # Explain query without index
    print("\n🔍 Query Plan WITHOUT index:")
    query = "SELECT * FROM users WHERE email = 'user100@example.com'"
    
    plan = analyzer.explain_query(conn, query)
    print(f"   Query: {query}")
    print(f"   Plan: {plan['plan']}")
    
    # Create index
    index_analyzer = IndexAnalyzer()
    index_analyzer.create_index(conn, 'users', 'email')
    
    # Explain query with index
    print("\n🔍 Query Plan WITH index:")
    plan = analyzer.explain_query(conn, query)
    print(f"   Query: {query}")
    print(f"   Plan: {plan['plan']}")
    
    conn.close()


def main():
    """Run all demonstrations"""
    print("\n" + "=" * 70)
    print("  Database Optimization - Demonstration")
    print("=" * 70)
    
    try:
        demo_connection_pool()
        demo_query_analysis()
        demo_query_caching()
        demo_indexing()
        demo_query_optimization()
        demo_explain_query()
        
        print("\n" + "=" * 70)
        print("  All Demonstrations Completed!")
        print("=" * 70)
        print("\nKey Optimization Techniques Demonstrated:")
        print("  1. Connection Pooling - Reuse connections")
        print("  2. Query Analysis - Measure performance")
        print("  3. Query Caching - Cache results")
        print("  4. Database Indexing - Speed up queries")
        print("  5. Query Optimization - Write better queries")
        print("  6. EXPLAIN - Understand query plans")
        print("\nTo run tests:")
        print("  python tests.py")
        print()
        
        # Cleanup
        if os.path.exists('demo.db'):
            os.remove('demo.db')
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
