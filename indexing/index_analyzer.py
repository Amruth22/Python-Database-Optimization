"""
Index Analyzer
Analyzes database indexes and provides recommendations
"""

import logging
import time

logger = logging.getLogger(__name__)


class IndexAnalyzer:
    """
    Database index analyzer
    Analyzes index usage and provides recommendations
    """
    
    def __init__(self):
        logger.info("Index Analyzer initialized")
    
    def get_table_indexes(self, connection, table_name):
        """
        Get all indexes for a table
        
        Args:
            connection: Database connection
            table_name: Name of table
            
        Returns:
            List of indexes
        """
        query = f"PRAGMA index_list('{table_name}')"
        cursor = connection.execute(query)
        indexes = cursor.fetchall()
        
        index_details = []
        for index in indexes:
            index_name = index['name']
            
            # Get index info
            info_query = f"PRAGMA index_info('{index_name}')"
            info_cursor = connection.execute(info_query)
            columns = info_cursor.fetchall()
            
            index_details.append({
                'name': index_name,
                'unique': bool(index['unique']),
                'columns': [col['name'] for col in columns]
            })
        
        return index_details
    
    def create_index(self, connection, table_name, column_name, unique=False):
        """
        Create an index on a table column
        
        Args:
            connection: Database connection
            table_name: Table name
            column_name: Column name
            unique: Whether index should be unique
        """
        index_name = f"idx_{table_name}_{column_name}"
        unique_clause = "UNIQUE" if unique else ""
        
        query = f"CREATE {unique_clause} INDEX IF NOT EXISTS {index_name} ON {table_name}({column_name})"
        
        start_time = time.time()
        connection.execute(query)
        connection.commit()
        creation_time = time.time() - start_time
        
        logger.info(f"Index created: {index_name} in {creation_time:.4f}s")
        
        return {
            'index_name': index_name,
            'table': table_name,
            'column': column_name,
            'creation_time': f"{creation_time:.4f}s"
        }
    
    def drop_index(self, connection, index_name):
        """
        Drop an index
        
        Args:
            connection: Database connection
            index_name: Name of index to drop
        """
        query = f"DROP INDEX IF EXISTS {index_name}"
        connection.execute(query)
        connection.commit()
        
        logger.info(f"Index dropped: {index_name}")
    
    def analyze_query_with_index(self, connection, query, params=None):
        """
        Analyze if query uses indexes
        
        Args:
            connection: Database connection
            query: SQL query
            params: Query parameters
            
        Returns:
            Analysis results
        """
        explain_query = f"EXPLAIN QUERY PLAN {query}"
        
        try:
            cursor = connection.execute(explain_query, params or [])
            plan = cursor.fetchall()
            
            # Check if using index
            uses_index = any('USING INDEX' in str(row).upper() for row in plan)
            table_scan = any('SCAN TABLE' in str(row).upper() for row in plan)
            
            return {
                'query': query,
                'uses_index': uses_index,
                'table_scan': table_scan,
                'plan': [dict(row) for row in plan],
                'recommendation': 'Consider adding index' if table_scan else 'Query optimized'
            }
        except Exception as e:
            logger.error(f"Error analyzing query: {e}")
            return {'error': str(e)}
    
    def compare_with_without_index(self, connection, table_name, column_name, query, params=None):
        """
        Compare query performance with and without index
        
        Args:
            connection: Database connection
            table_name: Table name
            column_name: Column to index
            query: Query to test
            params: Query parameters
            
        Returns:
            Comparison results
        """
        # Test without index
        start = time.time()
        cursor = connection.execute(query, params or [])
        results = cursor.fetchall()
        time_without = time.time() - start
        
        # Create index
        self.create_index(connection, table_name, column_name)
        
        # Test with index
        start = time.time()
        cursor = connection.execute(query, params or [])
        results_with = cursor.fetchall()
        time_with = time.time() - start
        
        speedup = time_without / time_with if time_with > 0 else 0
        
        return {
            'without_index': f"{time_without:.4f}s",
            'with_index': f"{time_with:.4f}s",
            'speedup': f"{speedup:.2f}x",
            'improvement': f"{((time_without - time_with) / time_without * 100):.2f}%"
        }
    
    def get_index_recommendations(self, connection, table_name):
        """
        Get index recommendations for a table
        
        Args:
            connection: Database connection
            table_name: Table name
            
        Returns:
            List of recommendations
        """
        # Get table info
        cursor = connection.execute(f"PRAGMA table_info('{table_name}')")
        columns = cursor.fetchall()
        
        # Get existing indexes
        existing_indexes = self.get_table_indexes(connection, table_name)
        indexed_columns = set()
        for index in existing_indexes:
            indexed_columns.update(index['columns'])
        
        # Recommend indexes for non-indexed columns
        recommendations = []
        for column in columns:
            col_name = column['name']
            
            if col_name not in indexed_columns and col_name != 'id':
                recommendations.append({
                    'table': table_name,
                    'column': col_name,
                    'reason': 'Column not indexed, may benefit from index for WHERE/JOIN clauses'
                })
        
        return recommendations
