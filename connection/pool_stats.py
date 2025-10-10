"""
Pool Statistics
Tracks and reports connection pool statistics
"""

import time
import logging

logger = logging.getLogger(__name__)


class PoolStats:
    """
    Connection pool statistics tracker
    """
    
    def __init__(self):
        self.start_time = time.time()
        self.total_connections_created = 0
        self.total_connections_closed = 0
        self.total_requests = 0
        self.total_waits = 0
        self.total_wait_time = 0.0
        
        logger.info("Pool Stats initialized")
    
    def record_connection_created(self):
        """Record a new connection creation"""
        self.total_connections_created += 1
    
    def record_connection_closed(self):
        """Record a connection closure"""
        self.total_connections_closed += 1
    
    def record_request(self):
        """Record a connection request"""
        self.total_requests += 1
    
    def record_wait(self, wait_time):
        """Record a wait for connection"""
        self.total_waits += 1
        self.total_wait_time += wait_time
    
    def get_stats(self):
        """Get all statistics"""
        uptime = time.time() - self.start_time
        
        return {
            'uptime_seconds': uptime,
            'total_connections_created': self.total_connections_created,
            'total_connections_closed': self.total_connections_closed,
            'active_connections': self.total_connections_created - self.total_connections_closed,
            'total_requests': self.total_requests,
            'total_waits': self.total_waits,
            'avg_wait_time': f"{(self.total_wait_time / self.total_waits) if self.total_waits > 0 else 0:.4f}s",
            'requests_per_second': self.total_requests / uptime if uptime > 0 else 0
        }
    
    def reset(self):
        """Reset all statistics"""
        self.start_time = time.time()
        self.total_connections_created = 0
        self.total_connections_closed = 0
        self.total_requests = 0
        self.total_waits = 0
        self.total_wait_time = 0.0
        logger.info("Pool stats reset")
