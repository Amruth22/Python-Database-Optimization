"""
Slow Query Examples
Examples of inefficient database queries
"""


def slow_query_select_all(connection):
    """
    Slow: SELECT * returns all columns
    """
    query = "SELECT * FROM users WHERE city = 'New York'"
    cursor = connection.execute(query)
    return cursor.fetchall()


def slow_query_like_wildcard(connection):
    """
    Slow: LIKE with leading wildcard prevents index usage
    """
    query = "SELECT * FROM users WHERE email LIKE '%@gmail.com'"
    cursor = connection.execute(query)
    return cursor.fetchall()


def slow_query_no_index(connection):
    """
    Slow: Query on non-indexed column
    """
    query = "SELECT * FROM orders WHERE status = 'pending'"
    cursor = connection.execute(query)
    return cursor.fetchall()


def slow_query_n_plus_one(connection):
    """
    Slow: N+1 query problem
    """
    # Get all users
    users_cursor = connection.execute("SELECT id, username FROM users LIMIT 10")
    users = users_cursor.fetchall()
    
    # For each user, get their orders (N queries)
    results = []
    for user in users:
        orders_cursor = connection.execute(
            "SELECT * FROM orders WHERE user_id = ?",
            (user['id'],)
        )
        orders = orders_cursor.fetchall()
        results.append({
            'user': dict(user),
            'orders': [dict(o) for o in orders]
        })
    
    return results


def slow_query_subquery(connection):
    """
    Slow: Inefficient subquery
    """
    query = """
        SELECT * FROM users 
        WHERE id IN (SELECT user_id FROM orders WHERE status = 'pending')
    """
    cursor = connection.execute(query)
    return cursor.fetchall()
