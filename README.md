# Database Optimization

Educational Python application demonstrating **database connection optimization**, **query analysis**, **custom connection pooling**, **query performance analysis**, **database indexing strategies**, and **query caching mechanisms**.

## Features

### 🔌 Connection Optimization
- **Custom Connection Pool** - Reuse database connections
- **Min/Max Connections** - Configurable pool size
- **Connection Timeout** - Handle connection limits
- **Connection Health** - Validate before use
- **Pool Statistics** - Track usage and efficiency

### 📊 Query Analysis
- **Execution Time Tracking** - Measure query performance
- **Slow Query Detection** - Identify bottlenecks
- **Query Statistics** - Aggregate performance metrics
- **EXPLAIN Analysis** - Understand query execution plans
- **Query Comparison** - Compare different approaches

### 💾 Query Caching
- **Result Caching** - Cache query results
- **TTL (Time To Live)** - Automatic expiration
- **Cache Invalidation** - Clear stale data
- **Hit/Miss Tracking** - Monitor cache efficiency
- **Size Management** - Limit cache size

### 📑 Database Indexing
- **Index Creation** - Create indexes on columns
- **Index Analysis** - Check index usage
- **Performance Comparison** - Before/after indexing
- **Index Recommendations** - Suggest improvements
- **Index Management** - Create/drop indexes

### 🚀 Query Optimization
- **Query Profiling** - Detailed performance analysis
- **Optimization Techniques** - Best practices
- **Before/After Examples** - Show improvements
- **N+1 Query Prevention** - Avoid common pitfalls

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Amruth22/Python-Database-Optimization.git
cd Python-Database-Optimization
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Demonstrations
```bash
python main.py
```

### 5. Run Tests
```bash
python tests.py
```

## Project Structure

```
Python-Database-Optimization/
│
├── connection/
│   └── connection_pool.py       # Connection pooling
│
├── query/
│   └── query_analyzer.py        # Query analysis
│
├── caching/
│   └── query_cache.py           # Query caching
│
├── indexing/
│   └── index_analyzer.py        # Index management
│
├── examples/
│   └── database_setup.py        # Sample database
│
├── main.py                      # Demonstration script
├── tests.py                     # 10 unit tests
├── requirements.txt             # Dependencies
├── .env                         # Configuration
└── README.md                    # This file
```

## Usage Examples

### Connection Pooling

```python
from connection.connection_pool import ConnectionPool

# Create connection pool
pool = ConnectionPool(
    database_path='database.db',
    min_connections=2,
    max_connections=10
)

# Get connection from pool
conn = pool.get_connection()

# Use connection
cursor = conn.execute("SELECT * FROM users")
results = cursor.fetchall()

# Return to pool (don't close!)
pool.release_connection(conn)

# Get pool statistics
stats = pool.get_stats()
print(f"Hit rate: {stats['hit_rate']}")
```

### Query Analysis

```python
from query.query_analyzer import QueryAnalyzer

# Create analyzer
analyzer = QueryAnalyzer(slow_query_threshold=1.0)

# Analyze query
result = analyzer.analyze_query(
    connection,
    "SELECT * FROM users WHERE email = ?",
    params=['user@example.com']
)

print(f"Execution time: {result['analysis']['execution_time']}s")
print(f"Rows returned: {result['analysis']['rows_returned']}")
print(f"Is slow: {result['analysis']['is_slow']}")

# Get statistics
stats = analyzer.get_query_stats()
print(f"Total queries: {stats['total_queries']}")
print(f"Slow queries: {stats['slow_queries']}")
```

### Query Caching

```python
from caching.query_cache import QueryCache

# Create cache
cache = QueryCache(ttl=300, max_size=1000)

query = "SELECT * FROM users WHERE city = 'New York'"

# Try to get from cache
result = cache.get(query)

if result is None:
    # Cache miss - execute query
    cursor = connection.execute(query)
    result = cursor.fetchall()
    
    # Cache the result
    cache.set(query, None, result)
else:
    # Cache hit - use cached result
    print("Using cached result!")

# Get cache stats
stats = cache.get_stats()
print(f"Hit rate: {stats['hit_rate']}")
```

### Database Indexing

```python
from indexing.index_analyzer import IndexAnalyzer

# Create analyzer
analyzer = IndexAnalyzer()

# Create index
result = analyzer.create_index(
    connection,
    table_name='users',
    column_name='email'
)

print(f"Index created: {result['index_name']}")

# Get table indexes
indexes = analyzer.get_table_indexes(connection, 'users')
print(f"Total indexes: {len(indexes)}")

# Compare performance
comparison = analyzer.compare_with_without_index(
    connection,
    'users',
    'email',
    "SELECT * FROM users WHERE email = 'user@example.com'"
)

print(f"Speedup: {comparison['speedup']}")
```

## Optimization Techniques

### 1. Connection Pooling

**Problem:**
```python
# Creating new connection for each request (SLOW)
for i in range(100):
    conn = sqlite3.connect('database.db')
    cursor = conn.execute("SELECT * FROM users")
    conn.close()
# Time: ~5 seconds
```

**Solution:**
```python
# Reusing connections from pool (FAST)
pool = ConnectionPool('database.db', max_connections=10)
for i in range(100):
    conn = pool.get_connection()
    cursor = conn.execute("SELECT * FROM users")
    pool.release_connection(conn)
# Time: ~0.5 seconds (10x faster!)
```

### 2. Query Optimization

**Slow Query:**
```sql
SELECT * FROM users WHERE email LIKE '%@gmail.com'
-- Time: 2.5s (full table scan)
```

**Optimized Query:**
```sql
-- Add index
CREATE INDEX idx_email ON users(email);

-- Use exact match instead of LIKE
SELECT id, username, email FROM users WHERE email = 'user@gmail.com'
-- Time: 0.001s (2500x faster!)
```

### 3. Query Caching

**Without Cache:**
```python
# Every request hits database
for i in range(100):
    result = execute_query("SELECT * FROM users WHERE city = 'NYC'")
# Time: 10 seconds
```

**With Cache:**
```python
# First request hits database, rest use cache
cache = QueryCache(ttl=300)
for i in range(100):
    result = cache.get(query) or execute_and_cache(query)
# Time: 0.1 seconds (100x faster!)
```

### 4. Index Selection

**Good Indexes:**
- Columns in WHERE clauses
- Columns in JOIN conditions
- Columns in ORDER BY
- Foreign keys

**Bad Indexes:**
- Small tables (< 1000 rows)
- Columns with low cardinality
- Frequently updated columns

## Performance Comparison

| Technique | Improvement | Use Case |
|-----------|-------------|----------|
| **Connection Pooling** | 5-10x | All applications |
| **Indexing** | 10-1000x | Large tables, WHERE/JOIN |
| **Query Caching** | 100-1000x | Repeated queries |
| **Query Optimization** | 2-100x | Complex queries |
| **SELECT Specific Columns** | 1.5-3x | Large tables |

## Testing

Run the comprehensive test suite:

```bash
python tests.py
```

### Test Coverage (10 Tests)

1. ✅ **Connection Pool Creation** - Test pool initialization
2. ✅ **Connection Reuse** - Test connection pooling
3. ✅ **Query Analysis** - Test performance measurement
4. ✅ **Slow Query Detection** - Test slow query identification
5. ✅ **Query Caching** - Test cache hit/miss
6. ✅ **Cache Invalidation** - Test cache clearing
7. ✅ **Index Creation** - Test index creation
8. ✅ **Index Performance** - Test performance improvement
9. ✅ **Pool Statistics** - Test pool metrics
10. ✅ **Cache TTL** - Test cache expiration

## Educational Notes

### 1. Why Connection Pooling?

**Without Pooling:**
- Create new connection: ~50ms
- 100 requests = 5 seconds overhead
- Resource intensive

**With Pooling:**
- Reuse connection: ~0.1ms
- 100 requests = 0.01 seconds overhead
- 500x faster!

### 2. When to Add Indexes

**Add Index When:**
- Table has > 1000 rows
- Column used in WHERE/JOIN
- Query is slow
- Column has high cardinality

**Don't Index When:**
- Small tables
- Frequently updated columns
- Low cardinality columns
- Already fast enough

### 3. Query Caching Strategy

**Cache:**
- Read-heavy queries
- Expensive queries
- Rarely changing data

**Don't Cache:**
- Real-time data
- User-specific data
- Frequently changing data

### 4. Common Query Problems

**N+1 Problem:**
```python
# Bad: N+1 queries
users = execute("SELECT * FROM users")
for user in users:
    orders = execute("SELECT * FROM orders WHERE user_id = ?", user.id)

# Good: 1 query with JOIN
result = execute("""
    SELECT users.*, orders.*
    FROM users
    LEFT JOIN orders ON users.id = orders.user_id
""")
```

## Production Considerations

For production use:

1. **Connection Pooling:**
   - Use SQLAlchemy or psycopg2 pools
   - Configure appropriate pool size
   - Monitor pool exhaustion

2. **Caching:**
   - Use Redis for distributed caching
   - Implement cache warming
   - Set appropriate TTLs

3. **Indexing:**
   - Analyze query patterns
   - Create composite indexes
   - Monitor index usage
   - Remove unused indexes

4. **Monitoring:**
   - Track slow queries
   - Monitor connection pool
   - Alert on performance degradation

5. **Database:**
   - Use PostgreSQL/MySQL for production
   - Implement read replicas
   - Use connection pooling at DB level

## Dependencies

- **Flask 3.0.0** - Web framework
- **python-dotenv 1.0.0** - Environment variables
- **pytest 7.4.3** - Testing framework
- **requests 2.31.0** - HTTP client
- **sqlite3** - Database (built-in)

## License

This project is for educational purposes. Feel free to use and modify as needed.

---

**Happy Optimizing! 🚀**
