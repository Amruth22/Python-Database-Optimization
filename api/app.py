"""
Flask API with Database Optimization
Demonstrates connection pooling, caching, and query optimization
"""

from flask import Flask, request, jsonify
import os
import logging

from connection.connection_pool import ConnectionPool
from query.query_analyzer import QueryAnalyzer
from caching.query_cache import QueryCache
from indexing.index_analyzer import IndexAnalyzer
from examples.database_setup import create_sample_database, populate_sample_data, get_table_stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize database
db_path = os.getenv('DATABASE_PATH', 'database.db')
if not os.path.exists(db_path):
    conn = create_sample_database(db_path)
    populate_sample_data(conn, num_users=1000, num_orders=5000, num_products=100)
    conn.close()

# Initialize components
pool = ConnectionPool(db_path, min_connections=2, max_connections=10)
analyzer = QueryAnalyzer(slow_query_threshold=1.0)
cache = QueryCache(ttl=300, max_size=1000)
index_analyzer = IndexAnalyzer()


@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        'message': 'Database Optimization API',
        'version': '1.0.0',
        'features': [
            'Connection Pooling',
            'Query Analysis',
            'Query Caching',
            'Database Indexing'
        ],
        'endpoints': {
            'users': '/api/users',
            'orders': '/api/orders',
            'stats': '/api/stats',
            'pool_stats': '/api/pool/stats',
            'cache_stats': '/api/cache/stats'
        }
    })


@app.route('/health')
def health():
    """Health check"""
    return jsonify({'status': 'healthy'})


@app.route('/api/users', methods=['GET'])
def get_users():
    """Get users with caching"""
    city = request.args.get('city')
    
    # Build query
    if city:
        query = "SELECT id, username, email, city FROM users WHERE city = ?"
        params = (city,)
    else:
        query = "SELECT id, username, email, city FROM users LIMIT 100"
        params = None
    
    # Check cache
    cached_result = cache.get(query, params)
    
    if cached_result is not None:
        return jsonify({
            'status': 'success',
            'users': [dict(row) for row in cached_result],
            'count': len(cached_result),
            'cached': True
        })
    
    # Cache miss - execute query
    conn = pool.get_connection()
    
    try:
        result = analyzer.analyze_query(conn.connection, query, params)
        users = result['results']
        
        # Cache result
        cache.set(query, params, users)
        
        return jsonify({
            'status': 'success',
            'users': [dict(row) for row in users],
            'count': len(users),
            'cached': False,
            'execution_time': f"{result['analysis']['execution_time']:.4f}s"
        })
    finally:
        pool.release_connection(conn)


@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Get orders with query optimization"""
    user_id = request.args.get('user_id', type=int)
    
    conn = pool.get_connection()
    
    try:
        if user_id:
            query = "SELECT id, user_id, product, quantity, price, status FROM orders WHERE user_id = ?"
            params = (user_id,)
        else:
            query = "SELECT id, user_id, product, quantity, price, status FROM orders LIMIT 100"
            params = None
        
        result = analyzer.analyze_query(conn.connection, query, params)
        
        return jsonify({
            'status': 'success',
            'orders': [dict(row) for row in result['results']],
            'count': len(result['results']),
            'execution_time': f"{result['analysis']['execution_time']:.4f}s"
        })
    finally:
        pool.release_connection(conn)


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    conn = pool.get_connection()
    
    try:
        users_stats = get_table_stats(conn.connection, 'users')
        orders_stats = get_table_stats(conn.connection, 'orders')
        products_stats = get_table_stats(conn.connection, 'products')
        
        return jsonify({
            'status': 'success',
            'tables': {
                'users': users_stats,
                'orders': orders_stats,
                'products': products_stats
            }
        })
    finally:
        pool.release_connection(conn)


@app.route('/api/pool/stats', methods=['GET'])
def get_pool_stats():
    """Get connection pool statistics"""
    stats = pool.get_stats()
    
    return jsonify({
        'status': 'success',
        'pool_stats': stats
    })


@app.route('/api/cache/stats', methods=['GET'])
def get_cache_stats():
    """Get cache statistics"""
    stats = cache.get_stats()
    
    return jsonify({
        'status': 'success',
        'cache_stats': stats
    })


@app.route('/api/query/stats', methods=['GET'])
def get_query_stats():
    """Get query analyzer statistics"""
    stats = analyzer.get_query_stats()
    
    return jsonify({
        'status': 'success',
        'query_stats': stats
    })


@app.route('/api/query/slow', methods=['GET'])
def get_slow_queries():
    """Get slow queries"""
    slow_queries = analyzer.get_slow_queries()
    
    return jsonify({
        'status': 'success',
        'slow_queries': [
            {
                'query': q['query'],
                'execution_time': f"{q['execution_time']:.4f}s",
                'rows_returned': q['rows_returned']
            }
            for q in slow_queries
        ],
        'count': len(slow_queries)
    })


@app.route('/api/indexes/<table_name>', methods=['GET'])
def get_table_indexes(table_name):
    """Get indexes for a table"""
    conn = pool.get_connection()
    
    try:
        indexes = index_analyzer.get_table_indexes(conn.connection, table_name)
        
        return jsonify({
            'status': 'success',
            'table': table_name,
            'indexes': indexes,
            'count': len(indexes)
        })
    finally:
        pool.release_connection(conn)


@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Clear query cache"""
    cache.clear()
    
    return jsonify({
        'status': 'success',
        'message': 'Cache cleared'
    })


if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    print("=" * 60)
    print("Database Optimization - Flask API")
    print("=" * 60)
    print(f"Starting on port {port}")
    print("Optimization features enabled:")
    print("  - Connection Pooling")
    print("  - Query Analysis")
    print("  - Query Caching")
    print("  - Database Indexing")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
