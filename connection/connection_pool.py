"""
Connection Pool
Custom database connection pooling implementation
"""

import sqlite3
import time
import logging
from threading import Lock
from queue import Queue, Empty

logger = logging.getLogger(__name__)


class PooledConnection:
    """
    Wrapper for pooled database connection
    """
    
    def __init__(self, connection, pool):
        self.connection = connection
        self.pool = pool
        self.created_at = time.time()
        self.last_used = time.time()
        self.in_use = False
    
    def execute(self, query, params=None):
        """Execute query on connection"""
        self.last_used = time.time()
        cursor = self.connection.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        return cursor
    
    def commit(self):
        """Commit transaction"""
        self.connection.commit()
    
    def rollback(self):
        """Rollback transaction"""
        self.connection.rollback()
    
    def close(self):
        """Return connection to pool"""
        self.pool.release_connection(self)
    
    def is_expired(self, max_age):
        """Check if connection is too old"""
        age = time.time() - self.created_at
        return age > max_age


class ConnectionPool:
    """
    Custom database connection pool
    Manages a pool of reusable database connections
    """
    
    def __init__(self, database_path, min_connections=2, max_connections=10, 
                 timeout=30, max_age=300):
        """
        Initialize connection pool
        
        Args:
            database_path: Path to SQLite database
            min_connections: Minimum connections to maintain
            max_connections: Maximum connections allowed
            timeout: Timeout for getting connection
            max_age: Maximum age of connection before recreation
        """
        self.database_path = database_path
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.timeout = timeout
        self.max_age = max_age
        
        self.available = Queue(maxsize=max_connections)
        self.in_use = []
        self.lock = Lock()
        
        self.total_created = 0
        self.total_requests = 0
        self.total_hits = 0
        self.total_misses = 0
        
        # Create minimum connections
        self._initialize_pool()
        
        logger.info(f"Connection Pool initialized: min={min_connections}, max={max_connections}")
    
    def _initialize_pool(self):
        """Create initial connections"""
        for _ in range(self.min_connections):
            conn = self._create_connection()
            self.available.put(conn)
    
    def _create_connection(self):
        """Create a new database connection"""
        connection = sqlite3.connect(self.database_path, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        
        pooled_conn = PooledConnection(connection, self)
        self.total_created += 1
        
        logger.debug(f"Created new connection (total: {self.total_created})")
        return pooled_conn
    
    def get_connection(self):
        """
        Get a connection from the pool
        
        Returns:
            PooledConnection instance
            
        Raises:
            TimeoutError: If no connection available within timeout
        """
        self.total_requests += 1
        
        try:
            # Try to get available connection
            conn = self.available.get(timeout=self.timeout)
            
            # Check if connection is expired
            if conn.is_expired(self.max_age):
                logger.debug("Connection expired, creating new one")
                conn.connection.close()
                conn = self._create_connection()
                self.total_misses += 1
            else:
                self.total_hits += 1
            
            # Mark as in use
            with self.lock:
                conn.in_use = True
                self.in_use.append(conn)
            
            logger.debug(f"Connection acquired (in use: {len(self.in_use)})")
            return conn
            
        except Empty:
            # No available connection
            with self.lock:
                total_connections = self.available.qsize() + len(self.in_use)
                
                if total_connections < self.max_connections:
                    # Create new connection
                    conn = self._create_connection()
                    conn.in_use = True
                    self.in_use.append(conn)
                    self.total_misses += 1
                    
                    logger.debug(f"Created new connection (total: {total_connections + 1})")
                    return conn
                else:
                    # Pool exhausted
                    logger.error("Connection pool exhausted")
                    raise TimeoutError("No available connections in pool")
    
    def release_connection(self, conn):
        """
        Return connection to pool
        
        Args:
            conn: PooledConnection to release
        """
        with self.lock:
            if conn in self.in_use:
                self.in_use.remove(conn)
                conn.in_use = False
                
                # Return to available pool
                try:
                    self.available.put_nowait(conn)
                    logger.debug(f"Connection released (available: {self.available.qsize()})")
                except:
                    # Queue full, close connection
                    conn.connection.close()
                    logger.debug("Connection closed (pool full)")
    
    def close_all(self):
        """Close all connections in pool"""
        with self.lock:
            # Close in-use connections
            for conn in self.in_use:
                conn.connection.close()
            self.in_use.clear()
            
            # Close available connections
            while not self.available.empty():
                try:
                    conn = self.available.get_nowait()
                    conn.connection.close()
                except Empty:
                    break
        
        logger.info("All connections closed")
    
    def get_stats(self):
        """Get pool statistics"""
        with self.lock:
            return {
                'total_created': self.total_created,
                'total_requests': self.total_requests,
                'cache_hits': self.total_hits,
                'cache_misses': self.total_misses,
                'hit_rate': f"{(self.total_hits / self.total_requests * 100) if self.total_requests > 0 else 0:.2f}%",
                'available': self.available.qsize(),
                'in_use': len(self.in_use),
                'total_connections': self.available.qsize() + len(self.in_use)
            }
