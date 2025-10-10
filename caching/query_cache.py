"""
Query Cache
Caches query results to reduce database load
"""

import time
import logging
import hashlib
import json

logger = logging.getLogger(__name__)


class QueryCache:
    """
    Query result caching system
    Caches query results with TTL (Time To Live)
    """
    
    def __init__(self, ttl=300, max_size=1000):
        """
        Initialize query cache
        
        Args:
            ttl: Time to live in seconds
            max_size: Maximum cache entries
        """
        self.ttl = ttl
        self.max_size = max_size
        self.cache = {}
        
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        
        logger.info(f"Query Cache initialized: TTL={ttl}s, max_size={max_size}")
    
    def _generate_key(self, query, params=None):
        """
        Generate cache key from query and params
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Cache key string
        """
        # Combine query and params
        cache_data = {
            'query': query.strip().lower(),
            'params': params or []
        }
        
        # Generate hash
        cache_str = json.dumps(cache_data, sort_keys=True)
        cache_key = hashlib.md5(cache_str.encode()).hexdigest()
        
        return cache_key
    
    def get(self, query, params=None):
        """
        Get cached query result
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Cached result or None if not found/expired
        """
        cache_key = self._generate_key(query, params)
        
        if cache_key in self.cache:
            cached_time, result = self.cache[cache_key]
            
            # Check if expired
            if time.time() - cached_time < self.ttl:
                self.hits += 1
                logger.debug(f"Cache hit for query: {query[:50]}")
                return result
            else:
                # Expired, remove from cache
                del self.cache[cache_key]
                logger.debug(f"Cache expired for query: {query[:50]}")
        
        self.misses += 1
        logger.debug(f"Cache miss for query: {query[:50]}")
        return None
    
    def set(self, query, params, result):
        """
        Cache query result
        
        Args:
            query: SQL query string
            params: Query parameters
            result: Query result to cache
        """
        cache_key = self._generate_key(query, params)
        
        # Check cache size
        if len(self.cache) >= self.max_size:
            # Evict oldest entry
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][0])
            del self.cache[oldest_key]
            self.evictions += 1
            logger.debug("Cache eviction (max size reached)")
        
        # Store in cache
        self.cache[cache_key] = (time.time(), result)
        logger.debug(f"Cached query result: {query[:50]}")
    
    def invalidate(self, query=None, params=None):
        """
        Invalidate cache entry or entire cache
        
        Args:
            query: Specific query to invalidate (None for all)
            params: Query parameters
        """
        if query:
            cache_key = self._generate_key(query, params)
            if cache_key in self.cache:
                del self.cache[cache_key]
                logger.debug(f"Cache invalidated for query: {query[:50]}")
        else:
            # Clear entire cache
            self.cache.clear()
            logger.info("Entire cache invalidated")
    
    def get_stats(self):
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_size': len(self.cache),
            'max_size': self.max_size,
            'ttl_seconds': self.ttl,
            'hits': self.hits,
            'misses': self.misses,
            'evictions': self.evictions,
            'hit_rate': f"{hit_rate:.2f}%",
            'total_requests': total_requests
        }
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        logger.info("Cache cleared")
