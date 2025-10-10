"""
Index Recommendations
Provides index recommendations based on query patterns
"""

import logging
import re

logger = logging.getLogger(__name__)


class IndexRecommendations:
    """
    Analyzes queries and recommends indexes
    """
    
    def __init__(self):
        self.query_patterns = []
        logger.info("Index Recommendations initialized")
    
    def analyze_query_for_indexes(self, query):
        """
        Analyze query and recommend indexes
        
        Args:
            query: SQL query string
            
        Returns:
            List of index recommendations
        """
        recommendations = []
        
        # Extract table name
        table_match = re.search(r'FROM\s+(\w+)', query, re.IGNORECASE)
        if not table_match:
            return recommendations
        
        table_name = table_match.group(1)
        
        # Extract WHERE columns
        where_match = re.search(r'WHERE\s+(.+?)(?:ORDER|GROUP|LIMIT|$)', query, re.IGNORECASE)
        if where_match:
            where_clause = where_match.group(1)
            
            # Find column names in WHERE clause
            column_pattern = r'(\w+)\s*[=<>]'
            columns = re.findall(column_pattern, where_clause)
            
            for column in columns:
                recommendations.append({
                    'table': table_name,
                    'column': column,
                    'reason': f'Column used in WHERE clause',
                    'priority': 'high'
                })
        
        # Extract JOIN columns
        join_matches = re.findall(r'JOIN\s+(\w+)\s+ON\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)', query, re.IGNORECASE)
        for match in join_matches:
            join_table = match[0]
            left_col = match[2]
            right_col = match[4]
            
            recommendations.append({
                'table': join_table,
                'column': right_col,
                'reason': 'Column used in JOIN condition',
                'priority': 'high'
            })
        
        # Extract ORDER BY columns
        order_match = re.search(r'ORDER\s+BY\s+(\w+)', query, re.IGNORECASE)
        if order_match:
            column = order_match.group(1)
            recommendations.append({
                'table': table_name,
                'column': column,
                'reason': 'Column used in ORDER BY',
                'priority': 'medium'
            })
        
        return recommendations
    
    def get_recommendations_summary(self, recommendations):
        """
        Get summary of recommendations
        
        Args:
            recommendations: List of recommendations
            
        Returns:
            Summary dictionary
        """
        high_priority = [r for r in recommendations if r['priority'] == 'high']
        medium_priority = [r for r in recommendations if r['priority'] == 'medium']
        
        return {
            'total_recommendations': len(recommendations),
            'high_priority': len(high_priority),
            'medium_priority': len(medium_priority),
            'recommendations': recommendations
        }
