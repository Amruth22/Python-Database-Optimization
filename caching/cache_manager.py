"""
Cache Manager
Manages multiple caches and cache strategies
"""

import logging
from caching.query_cache import QueryCache

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Manages multiple query caches
    """
    
    def __init__(self):
        self.caches = {}
        logger.info("Cache Manager initialized")
    
    def create_cache(self, name, ttl=300, max_size=1000):
        """
        Create a named cache
        
        Args:
            name: Cache name
            ttl: Time to live
            max_size: Maximum cache size
        """
        self.caches[name] = QueryCache(ttl, max_size)
        logger.info(f"Cache created: {name} (TTL={ttl}s, max_size={max_size})")
    
    def get_cache(self, name):
        """Get cache by name"""
        return self.caches.get(name)
    
    def clear_cache(self, name):
        """Clear specific cache"""
        if name in self.caches:
            self.caches[name].clear()
            logger.info(f"Cache cleared: {name}")
    
    def clear_all(self):
        """Clear all caches"""
        for cache in self.caches.values():
            cache.clear()
        logger.info("All caches cleared")
    
    def get_all_stats(self):
        """Get statistics for all caches"""
        stats = {}
        for name, cache in self.caches.items():
            stats[name] = cache.get_stats()
        return stats


class CacheStrategy:
    """
    Cache invalidation strategies
    """
    
    @staticmethod
    def invalidate_on_write(cache, table_name):
        """
        Invalidate all cache entries for a table when data is written
        
        Args:
            cache: QueryCache instance
            table_name: Table that was modified
        """
        # In simple implementation, clear entire cache
        cache.clear()
        logger.info(f"Cache invalidated for table: {table_name}")
    
    @staticmethod
    def invalidate_pattern(cache, pattern):
        """
        Invalidate cache entries matching a pattern
        
        Args:
            cache: QueryCache instance
            pattern: Pattern to match
        """
        # Simple implementation - would need more sophisticated matching
        cache.clear()
        logger.info(f"Cache invalidated for pattern: {pattern}")
