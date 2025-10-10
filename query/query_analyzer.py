"""
Query Analyzer
Analyzes query performance and provides insights
"""

import time
import logging
import sqlite3

logger = logging.getLogger(__name__)


class QueryAnalyzer:
    """
    Query performance analyzer
    Tracks and analyzes query execution
    """
    
    def __init__(self, slow_query_threshold=1.0):
        """
        Initialize query analyzer
        
        Args:
            slow_query_threshold: Threshold in seconds for slow queries
        """
        self.slow_query_threshold = slow_query_threshold
        self.query_history = []
        self.slow_queries = []
        
        logger.info(f"Query Analyzer initialized (slow threshold: {slow_query_threshold}s)")
    
    def analyze_query(self, connection, query, params=None):
        """
        Analyze query execution
        
        Args:
            connection: Database connection
            query: SQL query string
            params: Query parameters
            
        Returns:
            Dictionary with query results and analysis
        """
        # Measure execution time
        start_time = time.time()
        
        cursor = connection.execute(query, params or [])
        results = cursor.fetchall()
        
        execution_time = time.time() - start_time
        
        # Get query plan
        explain_query = f"EXPLAIN QUERY PLAN {query}"
        try:
            explain_cursor = connection.execute(explain_query, params or [])
            query_plan = explain_cursor.fetchall()
        except:
            query_plan = []
        
        # Analyze results
        analysis = {
            'query': query,
            'params': params,
            'execution_time': execution_time,
            'rows_returned': len(results),
            'is_slow': execution_time > self.slow_query_threshold,
            'query_plan': [dict(row) for row in query_plan],
            'timestamp': time.time()
        }
        
        # Store in history
        self.query_history.append(analysis)
        
        # Track slow queries
        if analysis['is_slow']:
            self.slow_queries.append(analysis)
            logger.warning(f"Slow query detected: {execution_time:.4f}s - {query[:50]}")
        
        return {
            'results': results,
            'analysis': analysis
        }
    
    def get_slow_queries(self):
        """Get all slow queries"""
        return self.slow_queries
    
    def get_query_stats(self):
        """Get query statistics"""
        if not self.query_history:
            return {
                'total_queries': 0,
                'slow_queries': 0,
                'avg_execution_time': 0,
                'min_execution_time': 0,
                'max_execution_time': 0
            }
        
        execution_times = [q['execution_time'] for q in self.query_history]
        
        return {
            'total_queries': len(self.query_history),
            'slow_queries': len(self.slow_queries),
            'slow_query_percentage': f"{(len(self.slow_queries) / len(self.query_history) * 100):.2f}%",
            'avg_execution_time': f"{sum(execution_times) / len(execution_times):.4f}s",
            'min_execution_time': f"{min(execution_times):.4f}s",
            'max_execution_time': f"{max(execution_times):.4f}s"
        }
    
    def explain_query(self, connection, query, params=None):
        """
        Get query execution plan
        
        Args:
            connection: Database connection
            query: SQL query
            params: Query parameters
            
        Returns:
            Query execution plan
        """
        explain_query = f"EXPLAIN QUERY PLAN {query}"
        
        try:
            cursor = connection.execute(explain_query, params or [])
            plan = cursor.fetchall()
            
            return {
                'query': query,
                'plan': [dict(row) for row in plan]
            }
        except Exception as e:
            logger.error(f"Error explaining query: {e}")
            return {'error': str(e)}
    
    def compare_queries(self, connection, query1, query2, params1=None, params2=None):
        """
        Compare performance of two queries
        
        Args:
            connection: Database connection
            query1: First query
            query2: Second query
            params1: Parameters for query1
            params2: Parameters for query2
            
        Returns:
            Comparison results
        """
        # Analyze first query
        result1 = self.analyze_query(connection, query1, params1)
        
        # Analyze second query
        result2 = self.analyze_query(connection, query2, params2)
        
        # Compare
        time1 = result1['analysis']['execution_time']
        time2 = result2['analysis']['execution_time']
        
        speedup = time1 / time2 if time2 > 0 else 0
        
        return {
            'query1': {
                'query': query1,
                'time': f"{time1:.4f}s",
                'rows': result1['analysis']['rows_returned']
            },
            'query2': {
                'query': query2,
                'time': f"{time2:.4f}s",
                'rows': result2['analysis']['rows_returned']
            },
            'speedup': f"{speedup:.2f}x",
            'faster': 'query2' if time2 < time1 else 'query1'
        }
    
    def reset_stats(self):
        """Reset all statistics"""
        self.query_history.clear()
        self.slow_queries.clear()
        logger.info("Query analyzer stats reset")
