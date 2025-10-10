"""
Optimized Query Examples
Examples of efficient database queries
"""


def optimized_query_select_specific(connection):
    """
    Optimized: SELECT only needed columns
    """
    query = "SELECT id, username, email FROM users WHERE city = 'New York'"
    cursor = connection.execute(query)
    return cursor.fetchall()


def optimized_query_exact_match(connection):
    """
    Optimized: Use exact match instead of LIKE
    Assumes we extract domain and store it separately
    """
    query = "SELECT id, username, email FROM users WHERE email = ?"
    cursor = connection.execute(query, ('user@gmail.com',))
    return cursor.fetchall()


def optimized_query_with_index(connection):
    """
    Optimized: Query on indexed column
    """
    # Assumes index exists on status column
    query = "SELECT id, user_id, product, price FROM orders WHERE status = 'pending'"
    cursor = connection.execute(query)
    return cursor.fetchall()


def optimized_query_join(connection):
    """
    Optimized: Use JOIN instead of N+1 queries
    """
    query = """
        SELECT 
            users.id, users.username,
            orders.id as order_id, orders.product, orders.price
        FROM users
        LEFT JOIN orders ON users.id = orders.user_id
        LIMIT 10
    """
    cursor = connection.execute(query)
    return cursor.fetchall()


def optimized_query_exists(connection):
    """
    Optimized: Use EXISTS instead of IN with subquery
    """
    query = """
        SELECT * FROM users 
        WHERE EXISTS (
            SELECT 1 FROM orders 
            WHERE orders.user_id = users.id 
            AND orders.status = 'pending'
        )
    """
    cursor = connection.execute(query)
    return cursor.fetchall()


def optimized_query_limit(connection):
    """
    Optimized: Use LIMIT to reduce result set
    """
    query = "SELECT id, username, email FROM users WHERE city = 'New York' LIMIT 100"
    cursor = connection.execute(query)
    return cursor.fetchall()
