# src/utils/metrics.py

"""
Metrics Tracking System
========================
Prometheus metrics for monitoring CodeSensei.

Metrics:
- Request counts
- Response times
- Error rates
- Cache hit rates
- LLM API usage
- Analysis performance

Author: Shobin Sebastian
Date: December 2025
"""

from prometheus_client import (
    Counter, Histogram, Gauge, Summary,
    generate_latest, CONTENT_TYPE_LATEST
)
from functools import wraps
from typing import Callable
import time


# ============================================================================
# REQUEST METRICS
# ============================================================================

# Total requests by endpoint and status
REQUEST_COUNT = Counter(
    'codesensei_requests_total',
    'Total number of requests',
    ['endpoint', 'method', 'status_code']
)

# Request duration histogram
REQUEST_DURATION = Histogram(
    'codesensei_request_duration_seconds',
    'Request duration in seconds',
    ['endpoint', 'method'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0)
)

# Active requests gauge
ACTIVE_REQUESTS = Gauge(
    'codesensei_active_requests',
    'Number of active requests',
    ['endpoint']
)


# ============================================================================
# ANALYSIS METRICS
# ============================================================================

# Code analysis requests
ANALYSIS_COUNT = Counter(
    'codesensei_analysis_total',
    'Total code analyses performed',
    ['analysis_type']  # 'static' or 'llm'
)

# Analysis duration
ANALYSIS_DURATION = Histogram(
    'codesensei_analysis_duration_seconds',
    'Time taken for analysis',
    ['analysis_type'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0)
)

# Issues found per analysis
ISSUES_FOUND = Histogram(
    'codesensei_issues_found',
    'Number of issues found per analysis',
    ['severity'],  # 'critical', 'medium', 'low'
    buckets=(0, 1, 2, 5, 10, 20, 50, 100)
)

# Code size analyzed
CODE_SIZE_ANALYZED = Histogram(
    'codesensei_code_size_bytes',
    'Size of code analyzed in bytes',
    buckets=(100, 500, 1000, 5000, 10000, 50000, 100000)
)


# ============================================================================
# LLM METRICS
# ============================================================================

# LLM API calls
LLM_API_CALLS = Counter(
    'codesensei_llm_calls_total',
    'Total LLM API calls',
    ['status']  # 'success' or 'error'
)

# LLM API duration
LLM_API_DURATION = Histogram(
    'codesensei_llm_duration_seconds',
    'LLM API call duration',
    buckets=(0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0)
)

# LLM tokens used
LLM_TOKENS_USED = Counter(
    'codesensei_llm_tokens_total',
    'Total LLM tokens consumed',
    ['token_type']  # 'input' or 'output'
)


# ============================================================================
# CACHE METRICS
# ============================================================================

# Cache hits/misses
CACHE_OPERATIONS = Counter(
    'codesensei_cache_operations_total',
    'Cache operations',
    ['operation', 'result']  # operation: get/set, result: hit/miss/error
)

# Cache size
CACHE_SIZE = Gauge(
    'codesensei_cache_size_entries',
    'Number of entries in cache'
)


# ============================================================================
# ERROR METRICS
# ============================================================================

# Error count by type
ERROR_COUNT = Counter(
    'codesensei_errors_total',
    'Total errors',
    ['error_type', 'endpoint']
)

# Error rate (errors per minute)
ERROR_RATE = Gauge(
    'codesensei_error_rate',
    'Errors per minute'
)


# ============================================================================
# SYSTEM METRICS
# ============================================================================

# Application info
APP_INFO = Gauge(
    'codesensei_app_info',
    'Application information',
    ['version', 'environment']
)

# Uptime
UPTIME_SECONDS = Gauge(
    'codesensei_uptime_seconds',
    'Application uptime in seconds'
)


# ============================================================================
# DECORATORS
# ============================================================================

def track_request(endpoint: str):
    """Decorator to track request metrics."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Track active requests
            ACTIVE_REQUESTS.labels(endpoint=endpoint).inc()
            
            # Track duration
            start_time = time.time()
            
            try:
                # Execute function
                result = await func(*args, **kwargs)
                status_code = getattr(result, 'status_code', 200)
                
                # Record success
                REQUEST_COUNT.labels(
                    endpoint=endpoint,
                    method='POST',
                    status_code=status_code
                ).inc()
                
                return result
                
            except Exception as e:
                # Record error
                REQUEST_COUNT.labels(
                    endpoint=endpoint,
                    method='POST',
                    status_code=500
                ).inc()
                
                ERROR_COUNT.labels(
                    error_type=type(e).__name__,
                    endpoint=endpoint
                ).inc()
                
                raise
                
            finally:
                # Record duration
                duration = time.time() - start_time
                REQUEST_DURATION.labels(
                    endpoint=endpoint,
                    method='POST'
                ).observe(duration)
                
                # Decrease active requests
                ACTIVE_REQUESTS.labels(endpoint=endpoint).dec()
        
        return wrapper
    return decorator


def track_analysis(analysis_type: str):
    """Decorator to track analysis metrics."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Track count
            ANALYSIS_COUNT.labels(analysis_type=analysis_type).inc()
            
            # Track duration
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                # Track code size if available
                if 'code' in kwargs:
                    code_size = len(kwargs['code'])
                    CODE_SIZE_ANALYZED.observe(code_size)
                
                # Track issues found
                if isinstance(result, dict) and 'issues' in result:
                    for issue in result['issues']:
                        ISSUES_FOUND.labels(
                            severity=issue.get('severity', 'unknown')
                        ).observe(1)
                
                return result
                
            finally:
                duration = time.time() - start_time
                ANALYSIS_DURATION.labels(
                    analysis_type=analysis_type
                ).observe(duration)
        
        return wrapper
    return decorator


def track_llm_call(func: Callable) -> Callable:
    """Decorator to track LLM API calls."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            
            # Record success
            LLM_API_CALLS.labels(status='success').inc()
            
            # Track tokens if available
            if hasattr(result, 'usage'):
                LLM_TOKENS_USED.labels(token_type='input').inc(
                    result.usage.prompt_tokens
                )
                LLM_TOKENS_USED.labels(token_type='output').inc(
                    result.usage.completion_tokens
                )
            
            return result
            
        except Exception:
            # Record error
            LLM_API_CALLS.labels(status='error').inc()
            raise
            
        finally:
            # Record duration
            duration = time.time() - start_time
            LLM_API_DURATION.observe(duration)
    
    return wrapper


def track_cache_operation(operation: str, result: str):
    """Track cache operation."""
    CACHE_OPERATIONS.labels(
        operation=operation,
        result=result
    ).inc()


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_metrics() -> bytes:
    """Get metrics in Prometheus format."""
    return generate_latest()


def init_metrics(version: str = "0.3.0", environment: str = "production"):
    """Initialize metrics with application info."""
    APP_INFO.labels(version=version, environment=environment).set(1)


# Example usage
if __name__ == "__main__":
    # Initialize metrics
    init_metrics(version="0.3.0", environment="development")
    
    # Simulate some metrics
    REQUEST_COUNT.labels(
        endpoint="/analyze",
        method="POST",
        status_code=200
    ).inc()
    
    REQUEST_DURATION.labels(
        endpoint="/analyze",
        method="POST"
    ).observe(1.5)
    
    ANALYSIS_COUNT.labels(analysis_type="static").inc()
    ISSUES_FOUND.labels(severity="critical").observe(3)
    
    LLM_API_CALLS.labels(status="success").inc()
    LLM_TOKENS_USED.labels(token_type="input").inc(150)
    
    # Print metrics
    print(get_metrics().decode('utf-8'))