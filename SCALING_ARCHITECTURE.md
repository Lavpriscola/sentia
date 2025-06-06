# Scaling Architecture - Core Components for Future Growth

## 🚀 Multi-Threaded Processing for Better Responsiveness

### Current Bottlenecks
- Sequential text processing limits throughput
- Language detection blocks analysis pipeline
- Visualization generation causes UI freezes
- Database operations block request handling

### Threading Architecture

#### 1. Asynchronous Analysis Pipeline
```python
import asyncio
import concurrent.futures
from threading import ThreadPoolExecutor
from queue import Queue, PriorityQueue
import time

class AsyncSentimentAnalyzer:
    """Multi-threaded sentiment analyzer with async processing"""
    
    def __init__(self, max_workers=8):
        self.max_workers = max_workers
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.analysis_queue = PriorityQueue()
        self.result_cache = {}
        
        # Separate thread pools for different operations
        self.language_pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="lang")
        self.analysis_pool = ThreadPoolExecutor(max_workers=6, thread_name_prefix="analysis")
        self.viz_pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="viz")
        self.db_pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="db")
    
    async def analyze_async(self, text: str, priority: int = 1) -> dict:
        """Asynchronous analysis with priority queue"""
        # Create analysis task
        task_id = f"{hash(text)}_{time.time()}"
        
        # Check cache first
        if text in self.result_cache:
            return self.result_cache[text]
        
        # Submit to priority queue
        future = asyncio.get_event_loop().run_in_executor(
            self.analysis_pool, 
            self._analyze_threaded, 
            text, task_id
        )
        
        result = await future
        
        # Cache result
        self.result_cache[text] = result
        
        return result
    
    def _analyze_threaded(self, text: str, task_id: str) -> dict:
        """Thread-safe analysis method"""
        try:
            # Step 1: Language detection (parallel)
            lang_future = self.language_pool.submit(self._detect_language_safe, text)
            
            # Step 2: Basic preprocessing (can run in parallel)
            preprocess_future = self.analysis_pool.submit(self._preprocess_safe, text)
            
            # Wait for language detection
            language_info = lang_future.result(timeout=5)
            preprocessed = preprocess_future.result(timeout=3)
            
            # Step 3: Sentiment analysis
            sentiment_result = self._analyze_sentiment_safe(text, preprocessed, language_info)
            
            # Step 4: Uncertainty analysis (parallel)
            uncertainty_future = self.analysis_pool.submit(
                self._analyze_uncertainty_safe, text, sentiment_result, language_info
            )
            
            # Step 5: Confidence calculation (parallel)
            confidence_future = self.analysis_pool.submit(
                self._calculate_confidence_safe, text, sentiment_result, language_info
            )
            
            # Collect results
            uncertainty_factors = uncertainty_future.result(timeout=3)
            confidence_breakdown = confidence_future.result(timeout=3)
            
            # Compile final result
            result = {
                'task_id': task_id,
                'text': text,
                'language_info': language_info,
                'sentiment_result': sentiment_result,
                'uncertainty_factors': uncertainty_factors,
                'confidence_breakdown': confidence_breakdown,
                'processing_time': time.time(),
                'thread_info': {
                    'worker_id': threading.current_thread().name,
                    'queue_size': self.analysis_queue.qsize()
                }
            }
            
            # Async database storage
            self.db_pool.submit(self._store_result_safe, result)
            
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'task_id': task_id,
                'text': text,
                'processing_time': time.time()
            }
```

#### 2. Real-time Processing Queue
```python
class RealTimeProcessor:
    """Real-time processing with WebSocket support"""
    
    def __init__(self):
        self.processing_queue = asyncio.Queue(maxsize=1000)
        self.result_subscribers = set()
        self.processing_stats = {
            'total_processed': 0,
            'current_queue_size': 0,
            'average_processing_time': 0,
            'error_rate': 0
        }
    
    async def start_processing_loop(self):
        """Main processing loop"""
        while True:
            try:
                # Get next item from queue
                task = await self.processing_queue.get()
                
                # Process with timeout
                result = await asyncio.wait_for(
                    self._process_task(task), 
                    timeout=30.0
                )
                
                # Notify subscribers
                await self._notify_subscribers(result)
                
                # Update stats
                self._update_stats(result)
                
                # Mark task as done
                self.processing_queue.task_done()
                
            except asyncio.TimeoutError:
                await self._handle_timeout(task)
            except Exception as e:
                await self._handle_error(task, e)
    
    async def submit_analysis(self, text: str, priority: int = 1, user_id: str = None):
        """Submit text for analysis"""
        task = {
            'id': f"{hash(text)}_{time.time()}",
            'text': text,
            'priority': priority,
            'user_id': user_id,
            'submitted_at': time.time(),
            'retries': 0
        }
        
        try:
            await self.processing_queue.put(task)
            return {'task_id': task['id'], 'status': 'queued'}
        except asyncio.QueueFull:
            return {'error': 'Queue is full, please try again later'}
```

#### 3. WebSocket Real-time Updates
```python
from flask_socketio import SocketIO, emit
import json

class RealTimeAnalysisServer:
    """WebSocket server for real-time analysis updates"""
    
    def __init__(self, app):
        self.socketio = SocketIO(app, cors_allowed_origins="*")
        self.active_connections = {}
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.socketio.on('connect')
        def handle_connect():
            session_id = request.sid
            self.active_connections[session_id] = {
                'connected_at': time.time(),
                'analyses_requested': 0
            }
            emit('connected', {'session_id': session_id})
        
        @self.socketio.on('analyze_text')
        def handle_analysis_request(data):
            session_id = request.sid
            text = data.get('text', '')
            
            if not text:
                emit('error', {'message': 'No text provided'})
                return
            
            # Submit for async processing
            task_id = self._submit_async_analysis(text, session_id)
            
            # Send immediate response
            emit('analysis_started', {
                'task_id': task_id,
                'estimated_time': self._estimate_processing_time(text)
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            session_id = request.sid
            if session_id in self.active_connections:
                del self.active_connections[session_id]
    
    def broadcast_result(self, result, session_id):
        """Broadcast analysis result to specific session"""
        self.socketio.emit('analysis_complete', result, room=session_id)
    
    def broadcast_progress(self, progress_data, session_id):
        """Send progress updates"""
        self.socketio.emit('analysis_progress', progress_data, room=session_id)
```

## 📊 Comprehensive Data Collection from Multiple Sources

### Data Source Architecture

#### 1. Multi-Source Data Collector
```python
import aiohttp
import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, AsyncGenerator
import logging

@dataclass
class DataSource:
    """Data source configuration"""
    name: str
    type: str  # 'api', 'scraper', 'stream', 'file'
    endpoint: str
    rate_limit: int  # requests per minute
    priority: int
    enabled: bool = True
    auth_config: Dict = None

class DataCollector(ABC):
    """Abstract base class for data collectors"""
    
    @abstractmethod
    async def collect(self, query: str, limit: int = 100) -> AsyncGenerator[Dict, None]:
        """Collect data from source"""
        pass
    
    @abstractmethod
    async def validate_data(self, data: Dict) -> bool:
        """Validate collected data"""
        pass

class YouTubeDataCollector(DataCollector):
    """YouTube comments and video data collector"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = None
        self.rate_limiter = AsyncRateLimiter(100, 60)  # 100 requests per minute
    
    async def collect(self, query: str, limit: int = 100) -> AsyncGenerator[Dict, None]:
        """Collect YouTube comments and video data"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        # Search for videos
        videos = await self._search_videos(query, limit // 10)
        
        for video in videos:
            # Get video details
            video_data = await self._get_video_details(video['id'])
            yield {
                'source': 'youtube_video',
                'type': 'video_metadata',
                'data': video_data,
                'collected_at': time.time()
            }
            
            # Get comments
            async for comment in self._get_video_comments(video['id'], limit // len(videos)):
                yield {
                    'source': 'youtube_comment',
                    'type': 'user_comment',
                    'data': comment,
                    'video_id': video['id'],
                    'collected_at': time.time()
                }
    
    async def _search_videos(self, query: str, max_results: int = 10):
        """Search for videos"""
        await self.rate_limiter.acquire()
        
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            'key': self.api_key,
            'q': query,
            'part': 'snippet',
            'type': 'video',
            'maxResults': max_results,
            'order': 'relevance'
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('items', [])
            else:
                logging.error(f"YouTube API error: {response.status}")
                return []

class TwitterDataCollector(DataCollector):
    """Twitter/X data collector"""
    
    def __init__(self, bearer_token: str):
        self.bearer_token = bearer_token
        self.session = None
        self.rate_limiter = AsyncRateLimiter(300, 900)  # 300 requests per 15 minutes
    
    async def collect(self, query: str, limit: int = 100) -> AsyncGenerator[Dict, None]:
        """Collect tweets"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={'Authorization': f'Bearer {self.bearer_token}'}
            )
        
        url = "https://api.twitter.com/2/tweets/search/recent"
        params = {
            'query': query,
            'max_results': min(limit, 100),
            'tweet.fields': 'created_at,author_id,public_metrics,lang,context_annotations',
            'user.fields': 'verified,public_metrics'
        }
        
        await self.rate_limiter.acquire()
        
        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                for tweet in data.get('data', []):
                    yield {
                        'source': 'twitter',
                        'type': 'tweet',
                        'data': tweet,
                        'collected_at': time.time()
                    }

class RedditDataCollector(DataCollector):
    """Reddit data collector"""
    
    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        self.session = None
        self.access_token = None
    
    async def collect(self, query: str, limit: int = 100) -> AsyncGenerator[Dict, None]:
        """Collect Reddit posts and comments"""
        if not self.access_token:
            await self._authenticate()
        
        # Search subreddits
        subreddits = ['kpop', 'bangtan', 'BlackPink', 'twice', 'kpopthoughts']
        
        for subreddit in subreddits:
            async for post in self._get_subreddit_posts(subreddit, query, limit // len(subreddits)):
                yield {
                    'source': 'reddit',
                    'type': 'post',
                    'data': post,
                    'subreddit': subreddit,
                    'collected_at': time.time()
                }
                
                # Get comments for each post
                async for comment in self._get_post_comments(post['id'], 10):
                    yield {
                        'source': 'reddit',
                        'type': 'comment',
                        'data': comment,
                        'post_id': post['id'],
                        'subreddit': subreddit,
                        'collected_at': time.time()
                    }

class MultiSourceDataManager:
    """Manages data collection from multiple sources"""
    
    def __init__(self):
        self.collectors = {}
        self.collection_stats = {}
        self.data_queue = asyncio.Queue(maxsize=10000)
        self.processing_queue = asyncio.Queue(maxsize=5000)
    
    def register_collector(self, name: str, collector: DataCollector):
        """Register a data collector"""
        self.collectors[name] = collector
        self.collection_stats[name] = {
            'total_collected': 0,
            'last_collection': None,
            'errors': 0,
            'rate_limit_hits': 0
        }
    
    async def collect_from_all_sources(self, query: str, limit_per_source: int = 100):
        """Collect data from all registered sources"""
        tasks = []
        
        for name, collector in self.collectors.items():
            if hasattr(collector, 'enabled') and not collector.enabled:
                continue
            
            task = asyncio.create_task(
                self._collect_from_source(name, collector, query, limit_per_source)
            )
            tasks.append(task)
        
        # Wait for all collections to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        total_collected = 0
        for i, result in enumerate(results):
            source_name = list(self.collectors.keys())[i]
            if isinstance(result, Exception):
                logging.error(f"Error collecting from {source_name}: {result}")
                self.collection_stats[source_name]['errors'] += 1
            else:
                total_collected += result
                self.collection_stats[source_name]['total_collected'] += result
                self.collection_stats[source_name]['last_collection'] = time.time()
        
        return total_collected
    
    async def _collect_from_source(self, name: str, collector: DataCollector, 
                                 query: str, limit: int) -> int:
        """Collect data from a single source"""
        collected_count = 0
        
        try:
            async for data_item in collector.collect(query, limit):
                # Validate data
                if await collector.validate_data(data_item['data']):
                    # Add to processing queue
                    await self.data_queue.put({
                        'source': name,
                        'item': data_item,
                        'priority': collector.priority if hasattr(collector, 'priority') else 1
                    })
                    collected_count += 1
                
                # Check if we've reached the limit
                if collected_count >= limit:
                    break
        
        except Exception as e:
            logging.error(f"Error in {name} collector: {e}")
            raise
        
        return collected_count
```

#### 2. Data Processing Pipeline
```python
class DataProcessingPipeline:
    """Process collected data through analysis pipeline"""
    
    def __init__(self, sentiment_analyzer):
        self.sentiment_analyzer = sentiment_analyzer
        self.processed_data = []
        self.processing_stats = {
            'total_processed': 0,
            'successful_analyses': 0,
            'failed_analyses': 0,
            'average_processing_time': 0
        }
    
    async def start_processing_loop(self, data_queue: asyncio.Queue):
        """Main data processing loop"""
        while True:
            try:
                # Get data from queue
                data_item = await data_queue.get()
                
                # Process the data
                result = await self._process_data_item(data_item)
                
                # Store result
                if result:
                    await self._store_processed_data(result)
                    self.processing_stats['successful_analyses'] += 1
                else:
                    self.processing_stats['failed_analyses'] += 1
                
                self.processing_stats['total_processed'] += 1
                
                # Mark task as done
                data_queue.task_done()
                
            except Exception as e:
                logging.error(f"Error processing data: {e}")
                self.processing_stats['failed_analyses'] += 1
    
    async def _process_data_item(self, data_item: Dict) -> Dict:
        """Process individual data item"""
        start_time = time.time()
        
        try:
            # Extract text content
            text = self._extract_text(data_item)
            
            if not text or len(text.strip()) < 5:
                return None
            
            # Analyze sentiment
            analysis_result = await self.sentiment_analyzer.analyze_async(text)
            
            # Compile result
            result = {
                'source': data_item['source'],
                'original_data': data_item['item'],
                'extracted_text': text,
                'analysis_result': analysis_result,
                'processing_time': time.time() - start_time,
                'processed_at': time.time()
            }
            
            return result
            
        except Exception as e:
            logging.error(f"Error analyzing text: {e}")
            return None
    
    def _extract_text(self, data_item: Dict) -> str:
        """Extract text content from data item"""
        item_data = data_item['item']['data']
        source = data_item['source']
        
        if source == 'youtube_comment':
            return item_data.get('textDisplay', '')
        elif source == 'twitter':
            return item_data.get('text', '')
        elif source == 'reddit':
            if data_item['item']['type'] == 'post':
                title = item_data.get('title', '')
                selftext = item_data.get('selftext', '')
                return f"{title} {selftext}".strip()
            else:  # comment
                return item_data.get('body', '')
        
        return ''
```

## ⚡ Batch Processing Architecture

### High-Performance Batch Processing

#### 1. Distributed Batch Processor
```python
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
import pickle
import redis
from typing import List, Callable, Any

class DistributedBatchProcessor:
    """Distributed batch processing with Redis coordination"""
    
    def __init__(self, redis_host='localhost', redis_port=6379, max_workers=None):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.max_workers = max_workers or mp.cpu_count()
        self.batch_queue_key = 'sentiment_batch_queue'
        self.result_queue_key = 'sentiment_result_queue'
        self.processing_stats_key = 'sentiment_processing_stats'
    
    async def submit_batch(self, texts: List[str], batch_id: str = None, 
                          priority: int = 1, chunk_size: int = 100) -> str:
        """Submit batch for processing"""
        if not batch_id:
            batch_id = f"batch_{int(time.time())}_{hash(str(texts[:10]))}"
        
        # Split into chunks
        chunks = [texts[i:i+chunk_size] for i in range(0, len(texts), chunk_size)]
        
        # Submit chunks to Redis queue
        for i, chunk in enumerate(chunks):
            chunk_data = {
                'batch_id': batch_id,
                'chunk_id': f"{batch_id}_chunk_{i}",
                'texts': chunk,
                'priority': priority,
                'submitted_at': time.time(),
                'chunk_index': i,
                'total_chunks': len(chunks)
            }
            
            # Serialize and queue
            serialized_chunk = pickle.dumps(chunk_data)
            self.redis_client.lpush(self.batch_queue_key, serialized_chunk)
        
        # Store batch metadata
        batch_metadata = {
            'batch_id': batch_id,
            'total_texts': len(texts),
            'total_chunks': len(chunks),
            'submitted_at': time.time(),
            'status': 'queued',
            'priority': priority
        }
        
        self.redis_client.hset(f"batch_metadata:{batch_id}", mapping=batch_metadata)
        
        return batch_id
    
    def start_worker_processes(self, num_processes: int = None):
        """Start worker processes for batch processing"""
        if not num_processes:
            num_processes = self.max_workers
        
        processes = []
        
        for i in range(num_processes):
            process = mp.Process(
                target=self._worker_process,
                args=(i,),
                name=f"SentimentWorker-{i}"
            )
            process.start()
            processes.append(process)
        
        return processes
    
    def _worker_process(self, worker_id: int):
        """Worker process for batch processing"""
        # Initialize sentiment analyzer in worker process
        from sentiment_analyzer import SentimentAnalyzer
        analyzer = SentimentAnalyzer()
        
        logging.info(f"Worker {worker_id} started")
        
        while True:
            try:
                # Get chunk from queue (blocking)
                serialized_chunk = self.redis_client.brpop(self.batch_queue_key, timeout=30)
                
                if not serialized_chunk:
                    continue  # Timeout, try again
                
                # Deserialize chunk
                chunk_data = pickle.loads(serialized_chunk[1])
                
                # Process chunk
                results = self._process_chunk(analyzer, chunk_data, worker_id)
                
                # Store results
                result_data = {
                    'batch_id': chunk_data['batch_id'],
                    'chunk_id': chunk_data['chunk_id'],
                    'results': results,
                    'processed_at': time.time(),
                    'worker_id': worker_id,
                    'processing_time': results.get('processing_time', 0)
                }
                
                serialized_result = pickle.dumps(result_data)
                self.redis_client.lpush(self.result_queue_key, serialized_result)
                
                # Update processing stats
                self._update_processing_stats(worker_id, len(chunk_data['texts']))
                
            except Exception as e:
                logging.error(f"Worker {worker_id} error: {e}")
                time.sleep(1)  # Brief pause before retrying
    
    def _process_chunk(self, analyzer, chunk_data: Dict, worker_id: int) -> Dict:
        """Process a chunk of texts"""
        start_time = time.time()
        texts = chunk_data['texts']
        results = []
        
        for text in texts:
            try:
                result = analyzer.analyze_sentiment(text)
                results.append({
                    'text': text,
                    'analysis': result,
                    'success': True
                })
            except Exception as e:
                results.append({
                    'text': text,
                    'error': str(e),
                    'success': False
                })
        
        processing_time = time.time() - start_time
        
        return {
            'chunk_id': chunk_data['chunk_id'],
            'batch_id': chunk_data['batch_id'],
            'results': results,
            'processing_time': processing_time,
            'texts_processed': len(texts),
            'successful_analyses': sum(1 for r in results if r['success']),
            'failed_analyses': sum(1 for r in results if not r['success'])
        }
    
    async def get_batch_status(self, batch_id: str) -> Dict:
        """Get status of a batch"""
        # Get batch metadata
        metadata = self.redis_client.hgetall(f"batch_metadata:{batch_id}")
        
        if not metadata:
            return {'error': 'Batch not found'}
        
        # Count completed chunks
        completed_chunks = 0
        total_results = []
        
        # Check result queue for this batch
        result_keys = self.redis_client.lrange(self.result_queue_key, 0, -1)
        
        for result_key in result_keys:
            try:
                result_data = pickle.loads(result_key)
                if result_data['batch_id'] == batch_id:
                    completed_chunks += 1
                    total_results.extend(result_data['results'])
            except:
                continue
        
        total_chunks = int(metadata.get('total_chunks', 0))
        progress = (completed_chunks / total_chunks * 100) if total_chunks > 0 else 0
        
        status = 'completed' if completed_chunks == total_chunks else 'processing'
        if completed_chunks == 0:
            status = 'queued'
        
        return {
            'batch_id': batch_id,
            'status': status,
            'progress': progress,
            'completed_chunks': completed_chunks,
            'total_chunks': total_chunks,
            'total_texts': int(metadata.get('total_texts', 0)),
            'results_available': len(total_results),
            'submitted_at': float(metadata.get('submitted_at', 0))
        }
    
    async def get_batch_results(self, batch_id: str) -> List[Dict]:
        """Get results for a completed batch"""
        results = []
        result_keys = self.redis_client.lrange(self.result_queue_key, 0, -1)
        
        for result_key in result_keys:
            try:
                result_data = pickle.loads(result_key)
                if result_data['batch_id'] == batch_id:
                    results.extend(result_data['results'])
            except:
                continue
        
        return results
```

#### 2. Streaming Batch Processor
```python
class StreamingBatchProcessor:
    """Process data in streaming batches for real-time analysis"""
    
    def __init__(self, batch_size: int = 50, max_wait_time: float = 5.0):
        self.batch_size = batch_size
        self.max_wait_time = max_wait_time
        self.current_batch = []
        self.last_batch_time = time.time()
        self.processing_queue = asyncio.Queue()
        self.result_callbacks = []
    
    async def add_text(self, text: str, metadata: Dict = None):
        """Add text to streaming batch"""
        item = {
            'text': text,
            'metadata': metadata or {},
            'added_at': time.time()
        }
        
        self.current_batch.append(item)
        
        # Check if batch is ready
        if (len(self.current_batch) >= self.batch_size or 
            time.time() - self.last_batch_time >= self.max_wait_time):
            await self._process_current_batch()
    
    async def _process_current_batch(self):
        """Process current batch"""
        if not self.current_batch:
            return
        
        batch = self.current_batch.copy()
        self.current_batch = []
        self.last_batch_time = time.time()
        
        # Submit batch for processing
        await self.processing_queue.put({
            'batch_id': f"stream_batch_{int(time.time())}",
            'items': batch,
            'batch_size': len(batch)
        })
    
    async def start_processing_loop(self):
        """Start the batch processing loop"""
        while True:
            try:
                # Get batch from queue
                batch_data = await self.processing_queue.get()
                
                # Process batch
                results = await self._process_batch_async(batch_data)
                
                # Notify callbacks
                for callback in self.result_callbacks:
                    await callback(results)
                
                self.processing_queue.task_done()
                
            except Exception as e:
                logging.error(f"Error in streaming batch processor: {e}")
    
    async def _process_batch_async(self, batch_data: Dict) -> Dict:
        """Process batch asynchronously"""
        start_time = time.time()
        items = batch_data['items']
        
        # Process items in parallel
        tasks = []
        for item in items:
            task = asyncio.create_task(self._analyze_item(item))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Compile batch results
        successful_results = []
        failed_results = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_results.append({
                    'item': items[i],
                    'error': str(result)
                })
            else:
                successful_results.append(result)
        
        return {
            'batch_id': batch_data['batch_id'],
            'processing_time': time.time() - start_time,
            'total_items': len(items),
            'successful_analyses': len(successful_results),
            'failed_analyses': len(failed_results),
            'results': successful_results,
            'errors': failed_results
        }
    
    def add_result_callback(self, callback: Callable):
        """Add callback for batch results"""
        self.result_callbacks.append(callback)
```

## 🔧 Additional Crucial Core Components

### 1. Caching & Performance Layer
```python
class AdvancedCachingLayer:
    """Multi-level caching for performance optimization"""
    
    def __init__(self):
        # Memory cache (fastest)
        self.memory_cache = {}
        self.memory_cache_size = 10000
        
        # Redis cache (shared across instances)
        self.redis_cache = redis.Redis(host='localhost', port=6379)
        
        # Database cache (persistent)
        self.db_cache_table = 'analysis_cache'
        
        # Cache statistics
        self.cache_stats = {
            'memory_hits': 0,
            'redis_hits': 0,
            'db_hits': 0,
            'cache_misses': 0
        }
    
    async def get_cached_analysis(self, text_hash: str) -> Optional[Dict]:
        """Get cached analysis with multi-level lookup"""
        # Level 1: Memory cache
        if text_hash in self.memory_cache:
            self.cache_stats['memory_hits'] += 1
            return self.memory_cache[text_hash]
        
        # Level 2: Redis cache
        redis_result = self.redis_cache.get(f"analysis:{text_hash}")
        if redis_result:
            result = json.loads(redis_result)
            # Promote to memory cache
            self._add_to_memory_cache(text_hash, result)
            self.cache_stats['redis_hits'] += 1
            return result
        
        # Level 3: Database cache
        db_result = await self._get_from_db_cache(text_hash)
        if db_result:
            # Promote to higher levels
            self._add_to_memory_cache(text_hash, db_result)
            self.redis_cache.setex(f"analysis:{text_hash}", 3600, json.dumps(db_result))
            self.cache_stats['db_hits'] += 1
            return db_result
        
        # Cache miss
        self.cache_stats['cache_misses'] += 1
        return None
    
    async def cache_analysis(self, text_hash: str, result: Dict):
        """Cache analysis result at all levels"""
        # Add to memory cache
        self._add_to_memory_cache(text_hash, result)
        
        # Add to Redis cache (1 hour TTL)
        self.redis_cache.setex(f"analysis:{text_hash}", 3600, json.dumps(result))
        
        # Add to database cache (persistent)
        await self._add_to_db_cache(text_hash, result)
```

### 2. Monitoring & Observability
```python
class SystemMonitor:
    """Comprehensive system monitoring and alerting"""
    
    def __init__(self):
        self.metrics = {
            'requests_per_second': 0,
            'average_response_time': 0,
            'error_rate': 0,
            'queue_sizes': {},
            'worker_utilization': 0,
            'memory_usage': 0,
            'cpu_usage': 0
        }
        
        self.alerts = []
        self.alert_thresholds = {
            'error_rate': 0.05,  # 5%
            'response_time': 5.0,  # 5 seconds
            'queue_size': 1000,
            'memory_usage': 0.85  # 85%
        }
    
    async def start_monitoring(self):
        """Start monitoring loop"""
        while True:
            await self._collect_metrics()
            await self._check_alerts()
            await asyncio.sleep(30)  # Monitor every 30 seconds
    
    async def _collect_metrics(self):
        """Collect system metrics"""
        import psutil
        
        # System metrics
        self.metrics['memory_usage'] = psutil.virtual_memory().percent / 100
        self.metrics['cpu_usage'] = psutil.cpu_percent() / 100
        
        # Application metrics
        self.metrics['queue_sizes'] = await self._get_queue_sizes()
        self.metrics['worker_utilization'] = await self._get_worker_utilization()
    
    async def _check_alerts(self):
        """Check for alert conditions"""
        for metric, threshold in self.alert_thresholds.items():
            current_value = self.metrics.get(metric, 0)
            
            if current_value > threshold:
                alert = {
                    'metric': metric,
                    'current_value': current_value,
                    'threshold': threshold,
                    'timestamp': time.time(),
                    'severity': 'high' if current_value > threshold * 1.5 else 'medium'
                }
                
                await self._send_alert(alert)
```

### 3. Auto-scaling & Load Balancing
```python
class AutoScaler:
    """Automatic scaling based on load"""
    
    def __init__(self, min_workers=2, max_workers=20):
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.current_workers = min_workers
        self.worker_processes = []
        
        self.scaling_metrics = {
            'queue_length_threshold': 100,
            'cpu_threshold': 0.8,
            'response_time_threshold': 3.0
        }
    
    async def monitor_and_scale(self):
        """Monitor system and auto-scale"""
        while True:
            metrics = await self._get_current_metrics()
            
            scale_decision = self._make_scaling_decision(metrics)
            
            if scale_decision == 'scale_up':
                await self._scale_up()
            elif scale_decision == 'scale_down':
                await self._scale_down()
            
            await asyncio.sleep(60)  # Check every minute
    
    def _make_scaling_decision(self, metrics: Dict) -> str:
        """Decide whether to scale up or down"""
        queue_length = metrics.get('queue_length', 0)
        cpu_usage = metrics.get('cpu_usage', 0)
        response_time = metrics.get('avg_response_time', 0)
        
        # Scale up conditions
        if (queue_length > self.scaling_metrics['queue_length_threshold'] or
            cpu_usage > self.scaling_metrics['cpu_threshold'] or
            response_time > self.scaling_metrics['response_time_threshold']):
            
            if self.current_workers < self.max_workers:
                return 'scale_up'
        
        # Scale down conditions
        elif (queue_length < self.scaling_metrics['queue_length_threshold'] * 0.3 and
              cpu_usage < self.scaling_metrics['cpu_threshold'] * 0.5 and
              response_time < self.scaling_metrics['response_time_threshold'] * 0.5):
            
            if self.current_workers > self.min_workers:
                return 'scale_down'
        
        return 'no_change'
```

This scaling architecture provides the foundation for handling massive K-Pop sentiment analysis workloads with enterprise-grade performance, reliability, and observability.