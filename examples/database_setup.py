"""
Database Setup
Creates sample database with test data
"""

import sqlite3
import random
import logging

logger = logging.getLogger(__name__)


def create_sample_database(db_path='database.db'):
    """
    Create sample database with test data
    
    Args:
        db_path: Path to database file
        
    Returns:
        Database connection
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            age INTEGER,
            city TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product TEXT NOT NULL,
            quantity INTEGER,
            price REAL,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Create products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL,
            stock INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    logger.info("Database tables created")
    
    return conn


def populate_sample_data(conn, num_users=1000, num_orders=5000, num_products=100):
    """
    Populate database with sample data
    
    Args:
        conn: Database connection
        num_users: Number of users to create
        num_orders: Number of orders to create
        num_products: Number of products to create
    """
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("DELETE FROM orders")
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM products")
    
    # Insert users
    cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']
    
    for i in range(num_users):
        cursor.execute('''
            INSERT INTO users (username, email, age, city)
            VALUES (?, ?, ?, ?)
        ''', (
            f'user{i}',
            f'user{i}@example.com',
            random.randint(18, 80),
            random.choice(cities)
        ))
    
    # Insert products
    categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Sports']
    
    for i in range(num_products):
        cursor.execute('''
            INSERT INTO products (name, category, price, stock)
            VALUES (?, ?, ?, ?)
        ''', (
            f'Product {i}',
            random.choice(categories),
            round(random.uniform(10, 1000), 2),
            random.randint(0, 100)
        ))
    
    # Insert orders
    statuses = ['pending', 'confirmed', 'shipped', 'delivered']
    
    for i in range(num_orders):
        cursor.execute('''
            INSERT INTO orders (user_id, product, quantity, price, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            random.randint(1, num_users),
            f'Product {random.randint(1, num_products)}',
            random.randint(1, 5),
            round(random.uniform(10, 500), 2),
            random.choice(statuses)
        ))
    
    conn.commit()
    logger.info(f"Sample data created: {num_users} users, {num_orders} orders, {num_products} products")


def get_table_stats(conn, table_name):
    """
    Get statistics for a table
    
    Args:
        conn: Database connection
        table_name: Table name
        
    Returns:
        Table statistics
    """
    cursor = conn.cursor()
    
    # Get row count
    cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
    count = cursor.fetchone()['count']
    
    # Get table info
    cursor.execute(f"PRAGMA table_info('{table_name}')")
    columns = cursor.fetchall()
    
    return {
        'table': table_name,
        'row_count': count,
        'column_count': len(columns),
        'columns': [col['name'] for col in columns]
    }
