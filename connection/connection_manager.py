"""
Connection Manager
Manages database connections with context manager support
"""

import sqlite3
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Database connection manager
    Provides context manager for safe connection handling
    """
    
    def __init__(self, database_path):
        """
        Initialize connection manager
        
        Args:
            database_path: Path to database file
        """
        self.database_path = database_path
        logger.info(f"Connection Manager initialized for {database_path}")
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connection
        
        Usage:
            with manager.get_connection() as conn:
                cursor = conn.execute("SELECT * FROM users")
        """
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Error in connection: {e}")
            raise
        finally:
            conn.close()
    
    def execute_query(self, query, params=None):
        """
        Execute a query and return results
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            Query results
        """
        with self.get_connection() as conn:
            cursor = conn.execute(query, params or [])
            return cursor.fetchall()
    
    def execute_many(self, query, params_list):
        """
        Execute query with multiple parameter sets
        
        Args:
            query: SQL query
            params_list: List of parameter tuples
        """
        with self.get_connection() as conn:
            conn.executemany(query, params_list)
