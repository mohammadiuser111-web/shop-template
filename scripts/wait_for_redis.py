#!/usr/bin/env python
"""
Wait for Redis to be ready
Shop Template - Django E-commerce Template
"""

import os
import sys
import time


def wait_for_redis(host='localhost', port=6379, timeout=60, interval=1):
    """
    Wait for Redis to be ready
    
    Args:
        host: Redis host
        port: Redis port
        timeout: Maximum time to wait in seconds
        interval: Time between checks in seconds
    """
    import redis
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            # Try to connect to Redis
            client = redis.Redis(host=host, port=port, socket_timeout=5)
            client.ping()
            print("Redis is ready!")
            return True
        except (redis.ConnectionError, redis.TimeoutError) as e:
            print(f"Redis not ready yet: {e}")
            print(f"Retrying in {interval} second(s)...")
            time.sleep(interval)
    
    print(f"Timeout waiting for Redis after {timeout} seconds")
    return False


if __name__ == '__main__':
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(description='Wait for Redis to be ready')
    parser.add_argument('--host', type=str, default='localhost', help='Redis host')
    parser.add_argument('--port', type=int, default=6379, help='Redis port')
    parser.add_argument('--timeout', type=int, default=60, help='Maximum time to wait in seconds')
    parser.add_argument('--interval', type=int, default=1, help='Time between checks in seconds')
    
    args = parser.parse_args()
    
    # Wait for Redis
    success = wait_for_redis(
        host=args.host,
        port=args.port,
        timeout=args.timeout,
        interval=args.interval
    )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
