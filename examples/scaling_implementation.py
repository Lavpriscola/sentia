"""
Scaling Implementation Examples
Demonstrates multi-threaded processing, batch processing, and data collection
"""

import asyncio
import threading
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import queue
import time
import json
import logging
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
import hashlib
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class AnalysisTask:
    """Represents a sentiment analysis task"""
    id: str
    text: str
    priority: int = 1
    submitted_at: float = None
    metadata: Dict = None
    
    def __post_init__(self):
        if self.submitted_at is None:
            self.submitted_at = time.time()
        if self.metadata is None:
            self.metadata = {}

@dataclass
class AnalysisResult:
    """Represents the result of sentiment analysis"""
    task_id: str
    text: str
    sentiment_label: str
    confidence: float
    processing_time: float
    worker_id: str
    language_detected: str = 'en'
    uncertainty_factors: List[str] = None
    
    def __post_init__(self):
        if self.uncertainty_factors is None:
            self.uncertainty_factors = []

class ThreadSafeAnalyzer:
    """Thread-safe sentiment analyzer for multi-threaded processing"""
    
    def __init__(self):
        self._lock = threading.Lock()
        self.analysis_count = 0
        self.total_processing_time = 0.0
        
        # Simulate sentiment analysis (replace with actual analyzer)
        self.sentiment_labels = [
            'ENTHUSIASTIC_SUPPORT', 'NOSTALGIC_APPRECIATION', 'ANTICIPATORY_EXCITEMENT',
            'PROTECTIVE_DEFENSIVE', 'CRITICAL_DISAPPOINTMENT', 'NEUTRAL_FACTUAL',
            'COMPETITIVE_RIVALRY', 'SARCASTIC_MOCKERY', 'MALICIOUS_COORDINATED', 'MIXED_CONFLICTED'
        ]
    
    def analyze(self, text: str, task_id: str = None) -> AnalysisResult:
        """Thread-safe sentiment analysis"""
        start_time = time.time()
        worker_id = threading.current_thread().name
        
        # Simulate processing time
        processing_delay = len(text) * 0.001  # 1ms per character
        time.sleep(processing_delay)
        
        # Simple sentiment classification (replace with actual logic)
        text_hash = hashlib.md5(text.encode()).hexdigest()
        sentiment_index = int(text_hash[:2], 16) % len(self.sentiment_labels)
        sentiment_label = self.sentiment_labels[sentiment_index]
        
        # Calculate confidence based on text length and content
        confidence = min(0.5 + (len(text.split()) * 0.05), 1.0)
        
        # Detect language (simplified)
        language = 'ko' if any(ord(char) >= 0xAC00 and ord(char) <= 0xD7AF for char in text) else 'en'
        
        processing_time = time.time() - start_time
        
        # Thread-safe statistics update
        with self._lock:
            self.analysis_count += 1
            self.total_processing_time += processing_time
        
        return AnalysisResult(
            task_id=task_id or str(uuid.uuid4()),
            text=text,
            sentiment_label=sentiment_label,
            confidence=confidence,
            processing_time=processing_time,
            worker_id=worker_id,
            language_detected=language
        )
    
    def get_stats(self) -> Dict:
        """Get thread-safe statistics"""
        with self._lock:
            avg_time = self.total_processing_time / self.analysis_count if self.analysis_count > 0 else 0
            return {
                'total_analyses': self.analysis_count,
                'total_processing_time': self.total_processing_time,
                'average_processing_time': avg_time
            }

class MultiThreadedProcessor:
    """Multi-threaded sentiment analysis processor"""
    
    def __init__(self, max_workers: int = 8):
        self.max_workers = max_workers
        self.analyzer = ThreadSafeAnalyzer()
        self.task_queue = queue.PriorityQueue()
        self.result_queue = queue.Queue()
        self.workers = []
        self.running = False
        
        # Statistics
        self.stats = {
            'tasks_submitted': 0,
            'tasks_completed': 0,
            'tasks_failed': 0,
            'total_processing_time': 0.0
        }
    
    def start_workers(self):
        """Start worker threads"""
        self.running = True
        
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"SentimentWorker-{i}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
        
        logger.info(f"Started {self.max_workers} worker threads")
    
    def stop_workers(self):
        """Stop worker threads"""
        self.running = False
        
        # Add sentinel values to wake up workers
        for _ in range(self.max_workers):
            self.task_queue.put((0, None))  # Priority 0, None task
        
        # Wait for workers to finish
        for worker in self.workers:
            worker.join(timeout=5.0)
        
        logger.info("All worker threads stopped")
    
    def submit_task(self, text: str, priority: int = 1, metadata: Dict = None) -> str:
        """Submit analysis task"""
        task = AnalysisTask(
            id=str(uuid.uuid4()),
            text=text,
            priority=priority,
            metadata=metadata or {}
        )
        
        # Add to priority queue (lower priority number = higher priority)
        self.task_queue.put((priority, task))
        self.stats['tasks_submitted'] += 1
        
        return task.id
    
    def submit_batch(self, texts: List[str], priority: int = 1) -> List[str]:
        """Submit batch of texts for analysis"""
        task_ids = []
        
        for text in texts:
            task_id = self.submit_task(text, priority)
            task_ids.append(task_id)
        
        return task_ids
    
    def get_result(self, timeout: float = None) -> Optional[AnalysisResult]:
        """Get analysis result"""
        try:
            return self.result_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_results_batch(self, count: int, timeout: float = 10.0) -> List[AnalysisResult]:
        """Get multiple results"""
        results = []
        end_time = time.time() + timeout
        
        while len(results) < count and time.time() < end_time:
            remaining_time = end_time - time.time()
            result = self.get_result(timeout=remaining_time)
            
            if result:
                results.append(result)
            else:
                break
        
        return results
    
    def _worker_loop(self):
        """Worker thread main loop"""
        worker_name = threading.current_thread().name
        logger.info(f"Worker {worker_name} started")
        
        while self.running:
            try:
                # Get task from queue
                priority, task = self.task_queue.get(timeout=1.0)
                
                # Check for sentinel value
                if task is None:
                    break
                
                # Process task
                try:
                    result = self.analyzer.analyze(task.text, task.id)
                    self.result_queue.put(result)
                    self.stats['tasks_completed'] += 1
                    
                except Exception as e:
                    logger.error(f"Worker {worker_name} error processing task {task.id}: {e}")
                    self.stats['tasks_failed'] += 1
                
                finally:
                    self.task_queue.task_done()
                    
            except queue.Empty:
                continue  # Timeout, check if still running
            except Exception as e:
                logger.error(f"Worker {worker_name} unexpected error: {e}")
        
        logger.info(f"Worker {worker_name} stopped")
    
    def get_queue_status(self) -> Dict:
        """Get current queue status"""
        return {
            'pending_tasks': self.task_queue.qsize(),
            'completed_results': self.result_queue.qsize(),
            'active_workers': sum(1 for w in self.workers if w.is_alive()),
            'stats': self.stats.copy(),
            'analyzer_stats': self.analyzer.get_stats()
        }

class AsyncBatchProcessor:
    """Asynchronous batch processor for high-throughput analysis"""
    
    def __init__(self, max_concurrent: int = 100):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.analyzer = ThreadSafeAnalyzer()
        
        # Batch statistics
        self.batch_stats = {
            'batches_processed': 0,
            'total_texts_processed': 0,
            'average_batch_time': 0.0,
            'total_batch_time': 0.0
        }
    
    async def process_batch_async(self, texts: List[str], batch_id: str = None) -> Dict:
        """Process batch of texts asynchronously"""
        if not batch_id:
            batch_id = f"batch_{int(time.time())}_{len(texts)}"
        
        start_time = time.time()
        logger.info(f"Starting async batch processing: {batch_id} ({len(texts)} texts)")
        
        # Create tasks for all texts
        tasks = []
        for i, text in enumerate(texts):
            task = asyncio.create_task(
                self._analyze_text_async(text, f"{batch_id}_{i}")
            )
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_results = []
        failed_results = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_results.append({
                    'text_index': i,
                    'text': texts[i],
                    'error': str(result)
                })
            else:
                successful_results.append(result)
        
        processing_time = time.time() - start_time
        
        # Update statistics
        self.batch_stats['batches_processed'] += 1
        self.batch_stats['total_texts_processed'] += len(texts)
        self.batch_stats['total_batch_time'] += processing_time
        self.batch_stats['average_batch_time'] = (
            self.batch_stats['total_batch_time'] / self.batch_stats['batches_processed']
        )
        
        batch_result = {
            'batch_id': batch_id,
            'processing_time': processing_time,
            'total_texts': len(texts),
            'successful_analyses': len(successful_results),
            'failed_analyses': len(failed_results),
            'success_rate': len(successful_results) / len(texts) * 100,
            'throughput': len(texts) / processing_time,  # texts per second
            'results': successful_results,
            'errors': failed_results
        }
        
        logger.info(f"Completed batch {batch_id}: {len(successful_results)}/{len(texts)} successful")
        return batch_result
    
    async def _analyze_text_async(self, text: str, task_id: str) -> AnalysisResult:
        """Analyze single text with concurrency control"""
        async with self.semaphore:
            # Run analysis in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self.analyzer.analyze, 
                text, 
                task_id
            )
            return result
    
    def get_batch_stats(self) -> Dict:
        """Get batch processing statistics"""
        return self.batch_stats.copy()

class DataCollectionSimulator:
    """Simulates data collection from multiple sources"""
    
    def __init__(self):
        self.sources = {
            'youtube': self._simulate_youtube_data,
            'twitter': self._simulate_twitter_data,
            'reddit': self._simulate_reddit_data,
            'instagram': self._simulate_instagram_data
        }
        
        self.collection_stats = {
            source: {'collected': 0, 'errors': 0, 'last_collection': None}
            for source in self.sources
        }
    
    async def collect_from_source(self, source: str, query: str, limit: int = 100) -> List[Dict]:
        """Collect data from a specific source"""
        if source not in self.sources:
            raise ValueError(f"Unknown source: {source}")
        
        logger.info(f"Collecting from {source}: query='{query}', limit={limit}")
        
        try:
            data = await self.sources[source](query, limit)
            self.collection_stats[source]['collected'] += len(data)
            self.collection_stats[source]['last_collection'] = time.time()
            
            logger.info(f"Collected {len(data)} items from {source}")
            return data
            
        except Exception as e:
            self.collection_stats[source]['errors'] += 1
            logger.error(f"Error collecting from {source}: {e}")
            raise
    
    async def collect_from_all_sources(self, query: str, limit_per_source: int = 50) -> Dict:
        """Collect data from all sources concurrently"""
        logger.info(f"Starting multi-source collection: query='{query}'")
        
        # Create tasks for all sources
        tasks = []
        for source in self.sources:
            task = asyncio.create_task(
                self.collect_from_source(source, query, limit_per_source)
            )
            tasks.append((source, task))
        
        # Wait for all collections to complete
        results = {}
        total_collected = 0
        
        for source, task in tasks:
            try:
                data = await task
                results[source] = {
                    'data': data,
                    'count': len(data),
                    'status': 'success'
                }
                total_collected += len(data)
                
            except Exception as e:
                results[source] = {
                    'data': [],
                    'count': 0,
                    'status': 'error',
                    'error': str(e)
                }
        
        logger.info(f"Multi-source collection completed: {total_collected} total items")
        
        return {
            'query': query,
            'total_collected': total_collected,
            'sources': results,
            'collection_time': time.time()
        }
    
    async def _simulate_youtube_data(self, query: str, limit: int) -> List[Dict]:
        """Simulate YouTube data collection"""
        await asyncio.sleep(0.5)  # Simulate API delay
        
        data = []
        for i in range(min(limit, 100)):  # YouTube API limits
            data.append({
                'source': 'youtube',
                'type': 'comment',
                'id': f"yt_{query}_{i}",
                'text': f"YouTube comment about {query} - sample {i}",
                'author': f"user_{i}",
                'timestamp': time.time() - (i * 3600),  # Spread over hours
                'likes': max(0, 50 - i),
                'video_id': f"video_{query}"
            })
        
        return data
    
    async def _simulate_twitter_data(self, query: str, limit: int) -> List[Dict]:
        """Simulate Twitter data collection"""
        await asyncio.sleep(0.3)  # Simulate API delay
        
        data = []
        for i in range(min(limit, 200)):  # Twitter API limits
            data.append({
                'source': 'twitter',
                'type': 'tweet',
                'id': f"tw_{query}_{i}",
                'text': f"Tweet about {query} - sample {i} #kpop",
                'author': f"@user_{i}",
                'timestamp': time.time() - (i * 1800),  # Spread over 30 min intervals
                'retweets': max(0, 30 - i),
                'likes': max(0, 100 - i * 2),
                'hashtags': ['kpop', query.lower()]
            })
        
        return data
    
    async def _simulate_reddit_data(self, query: str, limit: int) -> List[Dict]:
        """Simulate Reddit data collection"""
        await asyncio.sleep(0.7)  # Simulate API delay
        
        data = []
        for i in range(min(limit, 75)):  # Reddit API limits
            data.append({
                'source': 'reddit',
                'type': 'post' if i % 5 == 0 else 'comment',
                'id': f"rd_{query}_{i}",
                'text': f"Reddit discussion about {query} - sample {i}",
                'author': f"u/user_{i}",
                'timestamp': time.time() - (i * 7200),  # Spread over 2 hour intervals
                'upvotes': max(0, 75 - i),
                'subreddit': 'kpop' if i % 2 == 0 else 'bangtan'
            })
        
        return data
    
    async def _simulate_instagram_data(self, query: str, limit: int) -> List[Dict]:
        """Simulate Instagram data collection"""
        await asyncio.sleep(0.4)  # Simulate API delay
        
        data = []
        for i in range(min(limit, 60)):  # Instagram API limits
            data.append({
                'source': 'instagram',
                'type': 'comment',
                'id': f"ig_{query}_{i}",
                'text': f"Instagram comment about {query} - sample {i} 💜",
                'author': f"user_{i}",
                'timestamp': time.time() - (i * 5400),  # Spread over 90 min intervals
                'likes': max(0, 40 - i),
                'post_id': f"post_{query}_{i//10}"
            })
        
        return data
    
    def get_collection_stats(self) -> Dict:
        """Get data collection statistics"""
        return self.collection_stats.copy()

class ComprehensiveProcessor:
    """Comprehensive processor combining all scaling features"""
    
    def __init__(self, max_workers: int = 8, max_concurrent: int = 100):
        self.threaded_processor = MultiThreadedProcessor(max_workers)
        self.async_processor = AsyncBatchProcessor(max_concurrent)
        self.data_collector = DataCollectionSimulator()
        
        # Overall statistics
        self.overall_stats = {
            'total_texts_processed': 0,
            'total_batches_processed': 0,
            'total_data_collected': 0,
            'start_time': time.time()
        }
    
    def start(self):
        """Start all processors"""
        self.threaded_processor.start_workers()
        logger.info("Comprehensive processor started")
    
    def stop(self):
        """Stop all processors"""
        self.threaded_processor.stop_workers()
        logger.info("Comprehensive processor stopped")
    
    async def full_pipeline_demo(self, query: str = "BTS") -> Dict:
        """Demonstrate full processing pipeline"""
        logger.info(f"Starting full pipeline demo for query: {query}")
        
        # Step 1: Collect data from multiple sources
        logger.info("Step 1: Collecting data from multiple sources...")
        collection_result = await self.data_collector.collect_from_all_sources(query, 20)
        
        # Step 2: Extract texts for analysis
        all_texts = []
        for source, source_data in collection_result['sources'].items():
            if source_data['status'] == 'success':
                for item in source_data['data']:
                    all_texts.append(item['text'])
        
        logger.info(f"Step 2: Extracted {len(all_texts)} texts for analysis")
        
        # Step 3: Process with async batch processor
        logger.info("Step 3: Processing with async batch processor...")
        batch_result = await self.async_processor.process_batch_async(all_texts)
        
        # Step 4: Process some texts with threaded processor for comparison
        logger.info("Step 4: Processing sample with threaded processor...")
        sample_texts = all_texts[:10]  # Process first 10 texts
        
        # Submit to threaded processor
        task_ids = self.threaded_processor.submit_batch(sample_texts)
        
        # Get results
        threaded_results = self.threaded_processor.get_results_batch(len(task_ids))
        
        # Update overall statistics
        self.overall_stats['total_texts_processed'] += len(all_texts)
        self.overall_stats['total_batches_processed'] += 1
        self.overall_stats['total_data_collected'] += collection_result['total_collected']
        
        # Compile comprehensive result
        result = {
            'query': query,
            'pipeline_stages': {
                'data_collection': {
                    'total_collected': collection_result['total_collected'],
                    'sources': list(collection_result['sources'].keys()),
                    'collection_time': collection_result.get('collection_time')
                },
                'async_batch_processing': {
                    'total_texts': batch_result['total_texts'],
                    'success_rate': batch_result['success_rate'],
                    'throughput': batch_result['throughput'],
                    'processing_time': batch_result['processing_time']
                },
                'threaded_processing': {
                    'sample_size': len(threaded_results),
                    'completed': len(threaded_results),
                    'queue_status': self.threaded_processor.get_queue_status()
                }
            },
            'overall_stats': self.overall_stats.copy(),
            'performance_metrics': {
                'total_pipeline_time': time.time() - self.overall_stats['start_time'],
                'texts_per_second': (
                    self.overall_stats['total_texts_processed'] / 
                    (time.time() - self.overall_stats['start_time'])
                ),
                'data_collection_stats': self.data_collector.get_collection_stats(),
                'batch_processing_stats': self.async_processor.get_batch_stats()
            }
        }
        
        logger.info("Full pipeline demo completed successfully")
        return result

async def main():
    """Main demonstration function"""
    print("🚀 Scaling Implementation Demonstration")
    print("=" * 60)
    
    # Initialize comprehensive processor
    processor = ComprehensiveProcessor(max_workers=4, max_concurrent=50)
    
    try:
        # Start processors
        processor.start()
        
        # Run full pipeline demonstration
        print("\n📊 Running Full Pipeline Demo...")
        result = await processor.full_pipeline_demo("BLACKPINK")
        
        # Display results
        print("\n📈 Pipeline Results:")
        print(f"Query: {result['query']}")
        print(f"Total Data Collected: {result['pipeline_stages']['data_collection']['total_collected']}")
        print(f"Total Texts Processed: {result['pipeline_stages']['async_batch_processing']['total_texts']}")
        print(f"Success Rate: {result['pipeline_stages']['async_batch_processing']['success_rate']:.1f}%")
        print(f"Throughput: {result['pipeline_stages']['async_batch_processing']['throughput']:.1f} texts/second")
        
        print("\n🔧 Performance Metrics:")
        metrics = result['performance_metrics']
        print(f"Total Pipeline Time: {metrics['total_pipeline_time']:.2f} seconds")
        print(f"Overall Throughput: {metrics['texts_per_second']:.1f} texts/second")
        
        print("\n📊 Component Statistics:")
        for source, stats in metrics['data_collection_stats'].items():
            print(f"  {source.title()}: {stats['collected']} collected, {stats['errors']} errors")
        
        # Demonstrate individual components
        print("\n" + "=" * 60)
        print("🔧 Individual Component Demonstrations")
        
        # Multi-threaded processing demo
        print("\n1. Multi-threaded Processing Demo:")
        sample_texts = [
            "OMG BTS new song is amazing! 🔥",
            "BLACKPINK 블랙핑크 최고야!",
            "Not sure about this comeback...",
            "TWICE never disappoints! 💕",
            "This choreography is insane!"
        ]
        
        task_ids = processor.threaded_processor.submit_batch(sample_texts, priority=1)
        results = processor.threaded_processor.get_results_batch(len(task_ids), timeout=5.0)
        
        print(f"  Submitted: {len(task_ids)} tasks")
        print(f"  Completed: {len(results)} results")
        for result in results[:3]:  # Show first 3 results
            print(f"    {result.sentiment_label} ({result.confidence:.2f}) - {result.text[:50]}...")
        
        # Async batch processing demo
        print("\n2. Async Batch Processing Demo:")
        large_batch = [f"Sample K-Pop text {i} with various sentiments" for i in range(50)]
        batch_result = await processor.async_processor.process_batch_async(large_batch)
        
        print(f"  Batch Size: {batch_result['total_texts']}")
        print(f"  Processing Time: {batch_result['processing_time']:.2f} seconds")
        print(f"  Throughput: {batch_result['throughput']:.1f} texts/second")
        print(f"  Success Rate: {batch_result['success_rate']:.1f}%")
        
        # Data collection demo
        print("\n3. Data Collection Demo:")
        collection_result = await processor.data_collector.collect_from_all_sources("NewJeans", 15)
        
        print(f"  Query: NewJeans")
        print(f"  Total Collected: {collection_result['total_collected']}")
        for source, data in collection_result['sources'].items():
            status = "✅" if data['status'] == 'success' else "❌"
            print(f"    {source.title()}: {status} {data['count']} items")
        
    finally:
        # Clean up
        processor.stop()
    
    print("\n✅ Scaling implementation demonstration completed!")
    print("\nKey Features Demonstrated:")
    print("  ✓ Multi-threaded processing with priority queues")
    print("  ✓ Asynchronous batch processing with concurrency control")
    print("  ✓ Multi-source data collection with error handling")
    print("  ✓ Comprehensive statistics and monitoring")
    print("  ✓ Thread-safe operations and resource management")

if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(main())