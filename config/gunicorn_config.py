#!/usr/bin/env python3
"""
Production Gunicorn Configuration
================================
Optimized for high concurrency and performance
"""

import multiprocessing
import os

# Network configuration
bind = "0.0.0.0:5001"
backlog = 2048  # Maximum number of pending connections

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1  # Standard formula
worker_class = "gevent"  # Async worker for I/O bound operations
worker_connections = 1000  # Connections per worker
max_requests = 1000  # Restart workers after N requests (memory management)
max_requests_jitter = 50  # Add randomness to prevent thundering herd

# Performance tuning
keepalive = 10  # Keep connections alive for reuse
timeout = 30  # Worker timeout
graceful_timeout = 30  # Graceful shutdown time

# Memory management
preload_app = True  # Load app before forking workers
max_worker_memory = 300  # MB - restart if exceeded

# Logging
accesslog = "access.log"
errorlog = "error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Development vs Production
if os.getenv('FLASK_ENV') == 'development':
    reload = True
    workers = 2
else:
    # Production optimizations
    daemon = False  # Set to True for background
    pidfile = "/tmp/gunicorn.pid"
    worker_tmp_dir = "/dev/shm"  # Use RAM for temporary files 