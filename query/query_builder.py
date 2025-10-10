"""
Query Builder
Simple query builder for constructing SQL queries
"""

import logging

logger = logging.getLogger(__name__)


class QueryBuilder:
    """
    Simple SQL query builder
    Helps construct queries programmatically
    """
    
    def __init__(self, table_name):
        """
        Initialize query builder
        
        Args:
            table_name: Name of table to query
        """
        self.table_name = table_name
        self.select_columns = []
        self.where_conditions = []
        self.order_by_columns = []
        self.limit_value = None
        self.params = []
    
    def select(self, *columns):
        """
        Add columns to SELECT
        
        Args:
            *columns: Column names to select
        """
        self.select_columns.extend(columns)
        return self
    
    def where(self, condition, *params):
        """
        Add WHERE condition
        
        Args:
            condition: WHERE condition string
            *params: Parameters for condition
        """
        self.where_conditions.append(condition)
        self.params.extend(params)
        return self
    
    def order_by(self, column, direction='ASC'):
        """
        Add ORDER BY clause
        
        Args:
            column: Column to order by
            direction: ASC or DESC
        """
        self.order_by_columns.append(f"{column} {direction}")
        return self
    
    def limit(self, limit):
        """
        Add LIMIT clause
        
        Args:
            limit: Number of rows to limit
        """
        self.limit_value = limit
        return self
    
    def build(self):
        """
        Build the SQL query
        
        Returns:
            Tuple of (query_string, params)
        """
        # SELECT clause
        if self.select_columns:
            columns = ', '.join(self.select_columns)
        else:
            columns = '*'
        
        query = f"SELECT {columns} FROM {self.table_name}"
        
        # WHERE clause
        if self.where_conditions:
            where_clause = ' AND '.join(self.where_conditions)
            query += f" WHERE {where_clause}"
        
        # ORDER BY clause
        if self.order_by_columns:
            order_clause = ', '.join(self.order_by_columns)
            query += f" ORDER BY {order_clause}"
        
        # LIMIT clause
        if self.limit_value:
            query += f" LIMIT {self.limit_value}"
        
        return query, tuple(self.params)
    
    def execute(self, connection):
        """
        Build and execute query
        
        Args:
            connection: Database connection
            
        Returns:
            Query results
        """
        query, params = self.build()
        cursor = connection.execute(query, params)
        return cursor.fetchall()


# Example usage functions
def build_user_query(city=None, limit=None):
    """Build a user query"""
    builder = QueryBuilder('users')
    builder.select('id', 'username', 'email', 'city')
    
    if city:
        builder.where('city = ?', city)
    
    if limit:
        builder.limit(limit)
    
    return builder.build()


def build_order_query(user_id=None, status=None):
    """Build an order query"""
    builder = QueryBuilder('orders')
    builder.select('id', 'user_id', 'product', 'quantity', 'price', 'status')
    
    if user_id:
        builder.where('user_id = ?', user_id)
    
    if status:
        builder.where('status = ?', status)
    
    builder.order_by('created_at', 'DESC')
    
    return builder.build()
