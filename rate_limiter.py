"""
Real Rate Limiter Implementation
Provides comprehensive rate limiting with load testing and performance monitoring
"""

import time
import threading
import asyncio
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque, defaultdict
import sqlite3
import json
import logging
from functools import wraps
import redis
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RateLimitConfig:
    """Rate limit configuration"""
    max_requests: int
    time_window: int  # seconds
    burst_limit: Optional[int] = None
    cooldown_period: int = 0
    
@dataclass
class RequestMetrics:
    """Metrics for a single request"""
    timestamp: datetime
    response_time: float
    success: bool
    error_message: Optional[str] = None
    endpoint: Optional[str] = None

@dataclass
class LoadTestResult:
    """Result of load testing"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    median_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    error_rate: float
    rate_limit_hits: int
    test_duration: float

class RealRateLimiter:
    """Real implementation of rate limiting with Redis backend"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0", 
                 fallback_to_memory: bool = True):
        self.fallback_to_memory = fallback_to_memory
        self.redis_client = self._init_redis(redis_url)
        
        # Memory-based fallback
        self.memory_store = defaultdict(deque)
        self.memory_lock = threading.Lock()
        
        # Rate limit configurations
        self.rate_limits = {}
        
        # Metrics storage
        self.metrics_db = "rate_limiter_metrics.db"
        self._setup_metrics_db()
        
        # Performance monitoring
        self.request_metrics = deque(maxlen=10000)  # Keep last 10k requests
        self.metrics_lock = threading.Lock()
    
    def _init_redis(self, redis_url: str) -> Optional[redis.Redis]:
        """Initialize Redis client"""
        try:
            client = redis.from_url(redis_url)
            client.ping()  # Test connection
            logger.info("Redis connection established")
            return client
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            if self.fallback_to_memory:
                logger.info("Falling back to memory-based rate limiting")
            return None
    
    def _setup_metrics_db(self):
        """Setup SQLite database for metrics storage"""
        conn = sqlite3.connect(self.metrics_db)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS request_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            endpoint TEXT,
            response_time REAL NOT NULL,
            success BOOLEAN NOT NULL,
            error_message TEXT,
            rate_limited BOOLEAN DEFAULT FALSE
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS load_test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            total_requests INTEGER NOT NULL,
            successful_requests INTEGER NOT NULL,
            failed_requests INTEGER NOT NULL,
            average_response_time REAL NOT NULL,
            median_response_time REAL NOT NULL,
            p95_response_time REAL NOT NULL,
            p99_response_time REAL NOT NULL,
            requests_per_second REAL NOT NULL,
            error_rate REAL NOT NULL,
            rate_limit_hits INTEGER NOT NULL,
            test_duration REAL NOT NULL,
            config TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def configure_rate_limit(self, key: str, config: RateLimitConfig):
        """Configure rate limit for a specific key"""
        self.rate_limits[key] = config
        logger.info(f"Configured rate limit for '{key}': {config.max_requests} requests per {config.time_window}s")
    
    def is_allowed(self, key: str, identifier: str = "default") -> bool:
        """Check if request is allowed under rate limit"""
        if key not in self.rate_limits:
            return True  # No rate limit configured
        
        config = self.rate_limits[key]
        rate_key = f"{key}:{identifier}"
        
        if self.redis_client:
            return self._check_rate_limit_redis(rate_key, config)
        else:
            return self._check_rate_limit_memory(rate_key, config)
    
    def _check_rate_limit_redis(self, rate_key: str, config: RateLimitConfig) -> bool:
        """Check rate limit using Redis"""
        try:
            current_time = time.time()
            window_start = current_time - config.time_window
            
            # Use Redis pipeline for atomic operations
            pipe = self.redis_client.pipeline()
            
            # Remove old entries
            pipe.zremrangebyscore(rate_key, 0, window_start)
            
            # Count current requests
            pipe.zcard(rate_key)
            
            # Add current request
            pipe.zadd(rate_key, {str(current_time): current_time})
            
            # Set expiration
            pipe.expire(rate_key, config.time_window + 1)
            
            results = pipe.execute()
            current_count = results[1]
            
            # Check burst limit if configured
            if config.burst_limit and current_count > config.burst_limit:
                return False
            
            return current_count < config.max_requests
            
        except Exception as e:
            logger.error(f"Redis rate limit check failed: {e}")
            # Fallback to memory-based checking
            return self._check_rate_limit_memory(rate_key, config)
    
    def _check_rate_limit_memory(self, rate_key: str, config: RateLimitConfig) -> bool:
        """Check rate limit using memory storage"""
        with self.memory_lock:
            current_time = time.time()
            window_start = current_time - config.time_window
            
            # Remove old entries
            requests = self.memory_store[rate_key]
            while requests and requests[0] < window_start:
                requests.popleft()
            
            # Check burst limit if configured
            if config.burst_limit and len(requests) >= config.burst_limit:
                return False
            
            # Check rate limit
            if len(requests) >= config.max_requests:
                return False
            
            # Add current request
            requests.append(current_time)
            return True
    
    def rate_limit_decorator(self, key: str, identifier_func: Optional[Callable] = None):
        """Decorator for rate limiting functions"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Determine identifier
                if identifier_func:
                    identifier = identifier_func(*args, **kwargs)
                else:
                    identifier = "default"
                
                # Check rate limit
                if not self.is_allowed(key, identifier):
                    raise RateLimitExceeded(f"Rate limit exceeded for {key}:{identifier}")
                
                # Execute function with metrics
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    response_time = time.time() - start_time
                    
                    # Record metrics
                    self._record_request_metrics(
                        endpoint=key,
                        response_time=response_time,
                        success=True
                    )
                    
                    return result
                    
                except Exception as e:
                    response_time = time.time() - start_time
                    
                    # Record metrics
                    self._record_request_metrics(
                        endpoint=key,
                        response_time=response_time,
                        success=False,
                        error_message=str(e)
                    )
                    
                    raise
            
            return wrapper
        return decorator
    
    def _record_request_metrics(self, endpoint: str, response_time: float, 
                               success: bool, error_message: Optional[str] = None):
        """Record request metrics"""
        metric = RequestMetrics(
            timestamp=datetime.now(),
            response_time=response_time,
            success=success,
            error_message=error_message,
            endpoint=endpoint
        )
        
        with self.metrics_lock:
            self.request_metrics.append(metric)
        
        # Store in database (async to avoid blocking)
        threading.Thread(
            target=self._store_metric_to_db,
            args=(metric,),
            daemon=True
        ).start()
    
    def _store_metric_to_db(self, metric: RequestMetrics):
        """Store metric to database"""
        try:
            conn = sqlite3.connect(self.metrics_db)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO request_metrics 
            (timestamp, endpoint, response_time, success, error_message)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                metric.timestamp,
                metric.endpoint,
                metric.response_time,
                metric.success,
                metric.error_message
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to store metric: {e}")
    
    def get_current_metrics(self) -> Dict:
        """Get current performance metrics"""
        with self.metrics_lock:
            if not self.request_metrics:
                return {}
            
            recent_metrics = [m for m in self.request_metrics 
                            if m.timestamp > datetime.now() - timedelta(minutes=5)]
            
            if not recent_metrics:
                return {}
            
            response_times = [m.response_time for m in recent_metrics]
            success_count = sum(1 for m in recent_metrics if m.success)
            
            return {
                'total_requests': len(recent_metrics),
                'successful_requests': success_count,
                'error_rate': (len(recent_metrics) - success_count) / len(recent_metrics),
                'average_response_time': statistics.mean(response_times),
                'median_response_time': statistics.median(response_times),
                'p95_response_time': statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else max(response_times),
                'requests_per_second': len(recent_metrics) / 300  # 5 minutes
            }
    
    def load_test(self, test_function: Callable, test_name: str, 
                  concurrent_users: int = 10, requests_per_user: int = 100,
                  ramp_up_time: int = 10) -> LoadTestResult:
        """Perform load testing on a function"""
        logger.info(f"Starting load test '{test_name}' with {concurrent_users} users, {requests_per_user} requests each")
        
        start_time = time.time()
        results = []
        rate_limit_hits = 0
        
        def user_simulation(user_id: int) -> List[RequestMetrics]:
            """Simulate a single user's requests"""
            user_results = []
            
            # Ramp up delay
            ramp_delay = (user_id / concurrent_users) * ramp_up_time
            time.sleep(ramp_delay)
            
            for request_id in range(requests_per_user):
                request_start = time.time()
                
                try:
                    # Execute test function
                    test_function()
                    response_time = time.time() - request_start
                    
                    user_results.append(RequestMetrics(
                        timestamp=datetime.now(),
                        response_time=response_time,
                        success=True,
                        endpoint=test_name
                    ))
                    
                except RateLimitExceeded:
                    response_time = time.time() - request_start
                    nonlocal rate_limit_hits
                    rate_limit_hits += 1
                    
                    user_results.append(RequestMetrics(
                        timestamp=datetime.now(),
                        response_time=response_time,
                        success=False,
                        error_message="Rate limit exceeded",
                        endpoint=test_name
                    ))
                    
                except Exception as e:
                    response_time = time.time() - request_start
                    
                    user_results.append(RequestMetrics(
                        timestamp=datetime.now(),
                        response_time=response_time,
                        success=False,
                        error_message=str(e),
                        endpoint=test_name
                    ))
                
                # Small delay between requests
                time.sleep(0.01)
            
            return user_results
        
        # Execute load test with thread pool
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(user_simulation, i) for i in range(concurrent_users)]
            
            for future in as_completed(futures):
                try:
                    user_results = future.result()
                    results.extend(user_results)
                except Exception as e:
                    logger.error(f"User simulation failed: {e}")
        
        # Calculate results
        test_duration = time.time() - start_time
        total_requests = len(results)
        successful_requests = sum(1 for r in results if r.success)
        failed_requests = total_requests - successful_requests
        
        if results:
            response_times = [r.response_time for r in results]
            average_response_time = statistics.mean(response_times)
            median_response_time = statistics.median(response_times)
            
            if len(response_times) >= 20:
                p95_response_time = statistics.quantiles(response_times, n=20)[18]
                p99_response_time = statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else max(response_times)
            else:
                p95_response_time = max(response_times)
                p99_response_time = max(response_times)
        else:
            average_response_time = 0
            median_response_time = 0
            p95_response_time = 0
            p99_response_time = 0
        
        requests_per_second = total_requests / test_duration if test_duration > 0 else 0
        error_rate = failed_requests / total_requests if total_requests > 0 else 0
        
        result = LoadTestResult(
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            average_response_time=average_response_time,
            median_response_time=median_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            requests_per_second=requests_per_second,
            error_rate=error_rate,
            rate_limit_hits=rate_limit_hits,
            test_duration=test_duration
        )
        
        # Store load test results
        self._store_load_test_result(test_name, result)
        
        logger.info(f"Load test '{test_name}' completed: {successful_requests}/{total_requests} successful, {requests_per_second:.2f} RPS")
        
        return result
    
    def _store_load_test_result(self, test_name: str, result: LoadTestResult):
        """Store load test result to database"""
        try:
            conn = sqlite3.connect(self.metrics_db)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO load_test_results 
            (test_name, timestamp, total_requests, successful_requests, failed_requests,
             average_response_time, median_response_time, p95_response_time, p99_response_time,
             requests_per_second, error_rate, rate_limit_hits, test_duration, config)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                test_name,
                datetime.now(),
                result.total_requests,
                result.successful_requests,
                result.failed_requests,
                result.average_response_time,
                result.median_response_time,
                result.p95_response_time,
                result.p99_response_time,
                result.requests_per_second,
                result.error_rate,
                result.rate_limit_hits,
                result.test_duration,
                json.dumps(self.rate_limits, default=str)
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to store load test result: {e}")
    
    def get_load_test_history(self, test_name: Optional[str] = None) -> List[Dict]:
        """Get load test history"""
        conn = sqlite3.connect(self.metrics_db)
        cursor = conn.cursor()
        
        if test_name:
            cursor.execute('''
            SELECT * FROM load_test_results 
            WHERE test_name = ? 
            ORDER BY timestamp DESC
            ''', (test_name,))
        else:
            cursor.execute('''
            SELECT * FROM load_test_results 
            ORDER BY timestamp DESC
            ''')
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results

class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded"""
    pass

def test_rate_limiter():
    """Test the rate limiter implementation"""
    print("=== TESTING RATE LIMITER ===")
    
    # Initialize rate limiter
    limiter = RealRateLimiter(fallback_to_memory=True)
    
    # Configure rate limits
    limiter.configure_rate_limit("api_calls", RateLimitConfig(
        max_requests=10,
        time_window=60,  # 10 requests per minute
        burst_limit=5
    ))
    
    limiter.configure_rate_limit("sentiment_analysis", RateLimitConfig(
        max_requests=100,
        time_window=60  # 100 requests per minute
    ))
    
    # Test basic rate limiting
    print("\n1. Testing basic rate limiting...")
    
    @limiter.rate_limit_decorator("api_calls")
    def test_api_call():
        time.sleep(0.01)  # Simulate API call
        return "API response"
    
    # Make requests within limit
    success_count = 0
    for i in range(15):
        try:
            result = test_api_call()
            success_count += 1
            print(f"Request {i+1}: Success")
        except RateLimitExceeded:
            print(f"Request {i+1}: Rate limited")
        except Exception as e:
            print(f"Request {i+1}: Error - {e}")
    
    print(f"Successful requests: {success_count}/15")
    
    # Test load testing
    print("\n2. Testing load testing functionality...")
    
    @limiter.rate_limit_decorator("sentiment_analysis")
    def sentiment_analysis_simulation():
        # Simulate sentiment analysis work
        time.sleep(0.005)  # 5ms processing time
        return {"sentiment": "positive", "confidence": 0.85}
    
    # Run load test
    load_result = limiter.load_test(
        test_function=sentiment_analysis_simulation,
        test_name="sentiment_analysis_load_test",
        concurrent_users=5,
        requests_per_user=20,
        ramp_up_time=2
    )
    
    print(f"Load test results:")
    print(f"  Total requests: {load_result.total_requests}")
    print(f"  Successful: {load_result.successful_requests}")
    print(f"  Failed: {load_result.failed_requests}")
    print(f"  Average response time: {load_result.average_response_time:.3f}s")
    print(f"  Requests per second: {load_result.requests_per_second:.2f}")
    print(f"  Error rate: {load_result.error_rate:.2%}")
    print(f"  Rate limit hits: {load_result.rate_limit_hits}")
    
    # Test current metrics
    print("\n3. Current performance metrics...")
    current_metrics = limiter.get_current_metrics()
    
    if current_metrics:
        print(f"  Recent requests: {current_metrics.get('total_requests', 0)}")
        print(f"  Success rate: {(1 - current_metrics.get('error_rate', 0)):.2%}")
        print(f"  Average response time: {current_metrics.get('average_response_time', 0):.3f}s")
        print(f"  Requests per second: {current_metrics.get('requests_per_second', 0):.2f}")
    else:
        print("  No recent metrics available")
    
    # Test different rate limit scenarios
    print("\n4. Testing different rate limit scenarios...")
    
    # High-frequency requests
    limiter.configure_rate_limit("high_frequency", RateLimitConfig(
        max_requests=1000,
        time_window=60
    ))
    
    @limiter.rate_limit_decorator("high_frequency")
    def high_frequency_task():
        return "processed"
    
    start_time = time.time()
    high_freq_success = 0
    
    for i in range(50):
        try:
            high_frequency_task()
            high_freq_success += 1
        except RateLimitExceeded:
            break
    
    duration = time.time() - start_time
    print(f"  High frequency test: {high_freq_success}/50 successful in {duration:.2f}s")
    print(f"  Throughput: {high_freq_success/duration:.2f} requests/second")

if __name__ == "__main__":
    test_rate_limiter()