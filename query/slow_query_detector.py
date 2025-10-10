"""
Slow Query Detector
Detects and logs slow database queries
"""

import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)


class SlowQueryDetector:
    """
    Slow query detection and logging
    """
    
    def __init__(self, threshold=1.0):
        """
        Initialize slow query detector
        
        Args:
            threshold: Threshold in seconds for slow queries
        """
        self.threshold = threshold
        self.slow_queries = []
        
        logger.info(f"Slow Query Detector initialized (threshold: {threshold}s)")
    
    def detect(self, query, execution_time, params=None):
        """
        Check if query is slow and log it
        
        Args:
            query: SQL query string
            execution_time: Query execution time
            params: Query parameters
            
        Returns:
            True if slow, False otherwise
        """
        if execution_time > self.threshold:
            slow_query = {
                'query': query,
                'params': params,
                'execution_time': execution_time,
                'timestamp': time.time()
            }
            
            self.slow_queries.append(slow_query)
            
            logger.warning(
                f"SLOW QUERY ({execution_time:.4f}s): {query[:100]}"
            )
            
            return True
        
        return False
    
    def get_slow_queries(self, limit=None):
        """
        Get slow queries
        
        Args:
            limit: Maximum number of queries to return
            
        Returns:
            List of slow queries
        """
        if limit:
            return self.slow_queries[-limit:]
        return self.slow_queries
    
    def clear(self):
        """Clear slow query log"""
        self.slow_queries.clear()
        logger.info("Slow query log cleared")


def detect_slow_query(threshold=1.0):
    """
    Decorator to detect slow queries
    
    Usage:
        @detect_slow_query(threshold=0.5)
        def get_users(conn):
            return conn.execute("SELECT * FROM users").fetchall()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            if execution_time > threshold:
                logger.warning(
                    f"SLOW QUERY in {func.__name__}: {execution_time:.4f}s"
                )
            
            return result
        
        return wrapper
    
    return decorator
