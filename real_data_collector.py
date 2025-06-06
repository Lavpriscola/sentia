"""
Real Multi-Source Data Collector Implementation
Collects real data from YouTube, Twitter, Reddit, and other sources using actual APIs
"""

import os
import time
import json
import requests
import tweepy
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import praw
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import sqlite3
from ratelimit import limits, sleep_and_retry
import backoff
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CollectedData:
    """Represents collected data from any source"""
    source: str
    data_type: str  # 'comment', 'post', 'tweet', etc.
    id: str
    text: str
    author: str
    timestamp: datetime
    url: Optional[str] = None
    metadata: Optional[Dict] = None
    engagement_metrics: Optional[Dict] = None

@dataclass
class CollectionResult:
    """Result of a data collection operation"""
    source: str
    query: str
    collected_count: int
    success: bool
    error_message: Optional[str] = None
    data: List[CollectedData] = None
    collection_time: datetime = None
    
    def __post_init__(self):
        if self.collection_time is None:
            self.collection_time = datetime.now()
        if self.data is None:
            self.data = []

class RealDataCollector:
    """Real implementation of multi-source data collection"""
    
    def __init__(self, db_path: str = "collected_data.db"):
        self.db_path = db_path
        self.setup_database()
        
        # API configurations
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        self.twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
        self.reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        self.reddit_user_agent = os.getenv('REDDIT_USER_AGENT', 'KPopSentimentAnalyzer/1.0')
        
        # Initialize API clients
        self.youtube_client = self._init_youtube_client()
        self.twitter_client = self._init_twitter_client()
        self.reddit_client = self._init_reddit_client()
        
        # Rate limiting configurations
        self.rate_limits = {
            'youtube': {'calls': 100, 'period': 3600},  # 100 calls per hour
            'twitter': {'calls': 300, 'period': 900},   # 300 calls per 15 minutes
            'reddit': {'calls': 60, 'period': 60},      # 60 calls per minute
            'instagram': {'calls': 200, 'period': 3600} # 200 calls per hour
        }
    
    def setup_database(self):
        """Setup database for storing collected data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS collected_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            data_type TEXT NOT NULL,
            external_id TEXT NOT NULL,
            text TEXT NOT NULL,
            author TEXT,
            timestamp DATETIME NOT NULL,
            url TEXT,
            metadata TEXT,
            engagement_metrics TEXT,
            collected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            processed BOOLEAN DEFAULT FALSE,
            UNIQUE(source, external_id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS collection_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            query TEXT NOT NULL,
            collected_count INTEGER NOT NULL,
            success BOOLEAN NOT NULL,
            error_message TEXT,
            collection_time DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def _init_youtube_client(self):
        """Initialize YouTube Data API client"""
        if not self.youtube_api_key:
            logger.warning("YouTube API key not found. YouTube collection will be disabled.")
            return None
        
        try:
            return build('youtube', 'v3', developerKey=self.youtube_api_key)
        except Exception as e:
            logger.error(f"Failed to initialize YouTube client: {e}")
            return None
    
    def _init_twitter_client(self):
        """Initialize Twitter API client"""
        if not self.twitter_bearer_token:
            logger.warning("Twitter bearer token not found. Twitter collection will be disabled.")
            return None
        
        try:
            return tweepy.Client(bearer_token=self.twitter_bearer_token)
        except Exception as e:
            logger.error(f"Failed to initialize Twitter client: {e}")
            return None
    
    def _init_reddit_client(self):
        """Initialize Reddit API client"""
        if not self.reddit_client_id or not self.reddit_client_secret:
            logger.warning("Reddit credentials not found. Reddit collection will be disabled.")
            return None
        
        try:
            return praw.Reddit(
                client_id=self.reddit_client_id,
                client_secret=self.reddit_client_secret,
                user_agent=self.reddit_user_agent
            )
        except Exception as e:
            logger.error(f"Failed to initialize Reddit client: {e}")
            return None
    
    @sleep_and_retry
    @limits(calls=100, period=3600)  # YouTube rate limit
    def collect_youtube_data(self, query: str, max_results: int = 50) -> CollectionResult:
        """Collect data from YouTube comments and video descriptions"""
        if not self.youtube_client:
            return CollectionResult(
                source='youtube',
                query=query,
                collected_count=0,
                success=False,
                error_message="YouTube client not initialized"
            )
        
        collected_data = []
        
        try:
            # Search for videos
            search_response = self.youtube_client.search().list(
                q=query,
                part='id,snippet',
                type='video',
                maxResults=min(25, max_results // 2),  # Get videos first
                order='relevance',
                publishedAfter=(datetime.now() - timedelta(days=30)).isoformat() + 'Z'
            ).execute()
            
            for video in search_response.get('items', []):
                video_id = video['id']['videoId']
                video_snippet = video['snippet']
                
                # Collect video description as data point
                if video_snippet.get('description'):
                    collected_data.append(CollectedData(
                        source='youtube',
                        data_type='video_description',
                        id=f"video_{video_id}",
                        text=video_snippet['description'][:1000],  # Limit length
                        author=video_snippet['channelTitle'],
                        timestamp=datetime.fromisoformat(video_snippet['publishedAt'].replace('Z', '+00:00')),
                        url=f"https://www.youtube.com/watch?v={video_id}",
                        metadata={
                            'video_title': video_snippet['title'],
                            'channel_id': video_snippet['channelId']
                        }
                    ))
                
                # Collect comments for this video
                try:
                    comments_response = self.youtube_client.commentThreads().list(
                        part='snippet',
                        videoId=video_id,
                        maxResults=min(20, max_results // len(search_response['items'])),
                        order='relevance'
                    ).execute()
                    
                    for comment_thread in comments_response.get('items', []):
                        comment = comment_thread['snippet']['topLevelComment']['snippet']
                        
                        collected_data.append(CollectedData(
                            source='youtube',
                            data_type='comment',
                            id=comment_thread['id'],
                            text=comment['textDisplay'],
                            author=comment['authorDisplayName'],
                            timestamp=datetime.fromisoformat(comment['publishedAt'].replace('Z', '+00:00')),
                            url=f"https://www.youtube.com/watch?v={video_id}&lc={comment_thread['id']}",
                            engagement_metrics={
                                'likes': comment.get('likeCount', 0)
                            }
                        ))
                
                except HttpError as e:
                    if e.resp.status == 403:
                        logger.warning(f"Comments disabled for video {video_id}")
                    else:
                        logger.error(f"Error collecting comments for video {video_id}: {e}")
                
                # Respect rate limits
                time.sleep(0.1)
            
            # Store collected data
            self._store_collected_data(collected_data)
            
            return CollectionResult(
                source='youtube',
                query=query,
                collected_count=len(collected_data),
                success=True,
                data=collected_data
            )
            
        except Exception as e:
            logger.error(f"YouTube collection error: {e}")
            return CollectionResult(
                source='youtube',
                query=query,
                collected_count=0,
                success=False,
                error_message=str(e)
            )
    
    @sleep_and_retry
    @limits(calls=300, period=900)  # Twitter rate limit
    def collect_twitter_data(self, query: str, max_results: int = 100) -> CollectionResult:
        """Collect data from Twitter using the API v2"""
        if not self.twitter_client:
            return CollectionResult(
                source='twitter',
                query=query,
                collected_count=0,
                success=False,
                error_message="Twitter client not initialized"
            )
        
        collected_data = []
        
        try:
            # Search for recent tweets
            tweets = tweepy.Paginator(
                self.twitter_client.search_recent_tweets,
                query=f"{query} -is:retweet lang:en",
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'context_annotations'],
                user_fields=['username', 'name'],
                expansions=['author_id'],
                max_results=min(100, max_results)
            ).flatten(limit=max_results)
            
            # Get user information
            users = {}
            for tweet in tweets:
                if hasattr(tweet, 'author_id') and tweet.author_id not in users:
                    try:
                        user = self.twitter_client.get_user(id=tweet.author_id)
                        users[tweet.author_id] = user.data
                    except Exception as e:
                        logger.warning(f"Could not get user info for {tweet.author_id}: {e}")
                        users[tweet.author_id] = {'username': 'unknown', 'name': 'Unknown User'}
            
            # Process tweets
            for tweet in tweets:
                author_info = users.get(tweet.author_id, {'username': 'unknown', 'name': 'Unknown User'})
                
                collected_data.append(CollectedData(
                    source='twitter',
                    data_type='tweet',
                    id=tweet.id,
                    text=tweet.text,
                    author=author_info.get('username', 'unknown'),
                    timestamp=tweet.created_at,
                    url=f"https://twitter.com/{author_info.get('username', 'unknown')}/status/{tweet.id}",
                    metadata={
                        'author_name': author_info.get('name', 'Unknown User'),
                        'context_annotations': getattr(tweet, 'context_annotations', [])
                    },
                    engagement_metrics=getattr(tweet, 'public_metrics', {})
                ))
            
            # Store collected data
            self._store_collected_data(collected_data)
            
            return CollectionResult(
                source='twitter',
                query=query,
                collected_count=len(collected_data),
                success=True,
                data=collected_data
            )
            
        except Exception as e:
            logger.error(f"Twitter collection error: {e}")
            return CollectionResult(
                source='twitter',
                query=query,
                collected_count=0,
                success=False,
                error_message=str(e)
            )
    
    @sleep_and_retry
    @limits(calls=60, period=60)  # Reddit rate limit
    def collect_reddit_data(self, query: str, max_results: int = 100) -> CollectionResult:
        """Collect data from Reddit posts and comments"""
        if not self.reddit_client:
            return CollectionResult(
                source='reddit',
                query=query,
                collected_count=0,
                success=False,
                error_message="Reddit client not initialized"
            )
        
        collected_data = []
        
        try:
            # Search in relevant subreddits
            subreddits = ['kpop', 'bangtan', 'BlackPink', 'twice', 'straykids', 'ITZY', 'aespa']
            
            for subreddit_name in subreddits:
                try:
                    subreddit = self.reddit_client.subreddit(subreddit_name)
                    
                    # Search posts
                    posts = subreddit.search(query, limit=max_results // len(subreddits), time_filter='month')
                    
                    for post in posts:
                        # Collect post
                        collected_data.append(CollectedData(
                            source='reddit',
                            data_type='post',
                            id=f"post_{post.id}",
                            text=f"{post.title}\n{post.selftext}"[:1000],
                            author=str(post.author) if post.author else 'deleted',
                            timestamp=datetime.fromtimestamp(post.created_utc),
                            url=f"https://reddit.com{post.permalink}",
                            metadata={
                                'subreddit': subreddit_name,
                                'post_title': post.title,
                                'flair': post.link_flair_text
                            },
                            engagement_metrics={
                                'score': post.score,
                                'upvote_ratio': post.upvote_ratio,
                                'num_comments': post.num_comments
                            }
                        ))
                        
                        # Collect top comments
                        post.comments.replace_more(limit=0)  # Remove "more comments"
                        for comment in post.comments[:5]:  # Top 5 comments
                            if hasattr(comment, 'body') and len(comment.body) > 10:
                                collected_data.append(CollectedData(
                                    source='reddit',
                                    data_type='comment',
                                    id=f"comment_{comment.id}",
                                    text=comment.body,
                                    author=str(comment.author) if comment.author else 'deleted',
                                    timestamp=datetime.fromtimestamp(comment.created_utc),
                                    url=f"https://reddit.com{post.permalink}{comment.id}/",
                                    metadata={
                                        'subreddit': subreddit_name,
                                        'parent_post': post.id
                                    },
                                    engagement_metrics={
                                        'score': comment.score
                                    }
                                ))
                
                except Exception as e:
                    logger.warning(f"Error collecting from r/{subreddit_name}: {e}")
                    continue
                
                # Respect rate limits
                time.sleep(1)
            
            # Store collected data
            self._store_collected_data(collected_data)
            
            return CollectionResult(
                source='reddit',
                query=query,
                collected_count=len(collected_data),
                success=True,
                data=collected_data
            )
            
        except Exception as e:
            logger.error(f"Reddit collection error: {e}")
            return CollectionResult(
                source='reddit',
                query=query,
                collected_count=0,
                success=False,
                error_message=str(e)
            )
    
    def collect_instagram_data(self, query: str, max_results: int = 50) -> CollectionResult:
        """Collect data from Instagram (using web scraping as fallback)"""
        # Note: Instagram's official API has strict limitations
        # This is a placeholder for potential web scraping implementation
        # In production, you would need proper Instagram API access
        
        logger.warning("Instagram collection not implemented - requires Instagram Basic Display API or web scraping")
        
        return CollectionResult(
            source='instagram',
            query=query,
            collected_count=0,
            success=False,
            error_message="Instagram collection not implemented"
        )
    
    def collect_from_all_sources(self, query: str, max_results_per_source: int = 50) -> Dict[str, CollectionResult]:
        """Collect data from all available sources"""
        results = {}
        
        logger.info(f"Starting multi-source collection for query: '{query}'")
        
        # Collect from YouTube
        logger.info("Collecting from YouTube...")
        results['youtube'] = self.collect_youtube_data(query, max_results_per_source)
        
        # Collect from Twitter
        logger.info("Collecting from Twitter...")
        results['twitter'] = self.collect_twitter_data(query, max_results_per_source)
        
        # Collect from Reddit
        logger.info("Collecting from Reddit...")
        results['reddit'] = self.collect_reddit_data(query, max_results_per_source)
        
        # Collect from Instagram (placeholder)
        logger.info("Collecting from Instagram...")
        results['instagram'] = self.collect_instagram_data(query, max_results_per_source)
        
        # Log collection summary
        total_collected = sum(result.collected_count for result in results.values())
        successful_sources = sum(1 for result in results.values() if result.success)
        
        logger.info(f"Collection completed: {total_collected} items from {successful_sources}/{len(results)} sources")
        
        # Store collection logs
        self._store_collection_logs(results)
        
        return results
    
    def _store_collected_data(self, data_list: List[CollectedData]):
        """Store collected data in database"""
        if not data_list:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for data in data_list:
            try:
                cursor.execute('''
                INSERT OR IGNORE INTO collected_data 
                (source, data_type, external_id, text, author, timestamp, url, metadata, engagement_metrics)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data.source,
                    data.data_type,
                    data.id,
                    data.text,
                    data.author,
                    data.timestamp,
                    data.url,
                    json.dumps(data.metadata) if data.metadata else None,
                    json.dumps(data.engagement_metrics) if data.engagement_metrics else None
                ))
            except Exception as e:
                logger.error(f"Error storing data item {data.id}: {e}")
        
        conn.commit()
        conn.close()
    
    def _store_collection_logs(self, results: Dict[str, CollectionResult]):
        """Store collection logs in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for source, result in results.items():
            cursor.execute('''
            INSERT INTO collection_logs 
            (source, query, collected_count, success, error_message)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                result.source,
                result.query,
                result.collected_count,
                result.success,
                result.error_message
            ))
        
        conn.commit()
        conn.close()
    
    def get_collected_data(self, source: Optional[str] = None, limit: int = 100) -> List[CollectedData]:
        """Retrieve collected data from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if source:
            cursor.execute('''
            SELECT source, data_type, external_id, text, author, timestamp, url, metadata, engagement_metrics
            FROM collected_data 
            WHERE source = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
            ''', (source, limit))
        else:
            cursor.execute('''
            SELECT source, data_type, external_id, text, author, timestamp, url, metadata, engagement_metrics
            FROM collected_data 
            ORDER BY timestamp DESC 
            LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        data_list = []
        for row in rows:
            data_list.append(CollectedData(
                source=row[0],
                data_type=row[1],
                id=row[2],
                text=row[3],
                author=row[4],
                timestamp=datetime.fromisoformat(row[5]),
                url=row[6],
                metadata=json.loads(row[7]) if row[7] else None,
                engagement_metrics=json.loads(row[8]) if row[8] else None
            ))
        
        return data_list
    
    def get_collection_stats(self) -> Dict:
        """Get collection statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total counts by source
        cursor.execute('''
        SELECT source, COUNT(*) as count
        FROM collected_data 
        GROUP BY source
        ''')
        source_counts = dict(cursor.fetchall())
        
        # Recent collection activity
        cursor.execute('''
        SELECT source, SUM(collected_count) as total, COUNT(*) as collections
        FROM collection_logs 
        WHERE collection_time >= datetime('now', '-7 days')
        GROUP BY source
        ''')
        recent_activity = {row[0]: {'total_collected': row[1], 'collections': row[2]} 
                          for row in cursor.fetchall()}
        
        # Success rates
        cursor.execute('''
        SELECT source, 
               SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate
        FROM collection_logs 
        GROUP BY source
        ''')
        success_rates = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_data_points': sum(source_counts.values()),
            'source_counts': source_counts,
            'recent_activity': recent_activity,
            'success_rates': success_rates
        }

def test_data_collector():
    """Test the data collector with real APIs"""
    print("=== TESTING REAL DATA COLLECTOR ===")
    
    collector = RealDataCollector()
    
    # Test individual sources
    test_query = "BTS"
    
    print(f"\nTesting collection for query: '{test_query}'")
    
    # Test YouTube
    print("\n1. Testing YouTube collection...")
    youtube_result = collector.collect_youtube_data(test_query, max_results=10)
    print(f"YouTube: {youtube_result.collected_count} items, Success: {youtube_result.success}")
    if not youtube_result.success:
        print(f"Error: {youtube_result.error_message}")
    
    # Test Twitter
    print("\n2. Testing Twitter collection...")
    twitter_result = collector.collect_twitter_data(test_query, max_results=10)
    print(f"Twitter: {twitter_result.collected_count} items, Success: {twitter_result.success}")
    if not twitter_result.success:
        print(f"Error: {twitter_result.error_message}")
    
    # Test Reddit
    print("\n3. Testing Reddit collection...")
    reddit_result = collector.collect_reddit_data(test_query, max_results=10)
    print(f"Reddit: {reddit_result.collected_count} items, Success: {reddit_result.success}")
    if not reddit_result.success:
        print(f"Error: {reddit_result.error_message}")
    
    # Test multi-source collection
    print("\n4. Testing multi-source collection...")
    all_results = collector.collect_from_all_sources(test_query, max_results_per_source=5)
    
    total_collected = sum(result.collected_count for result in all_results.values())
    print(f"Total collected: {total_collected} items")
    
    for source, result in all_results.items():
        status = "✅" if result.success else "❌"
        print(f"  {source}: {status} {result.collected_count} items")
    
    # Show collection stats
    print("\n5. Collection statistics:")
    stats = collector.get_collection_stats()
    print(f"Total data points: {stats['total_data_points']}")
    print("By source:")
    for source, count in stats['source_counts'].items():
        print(f"  {source}: {count}")
    
    # Show sample collected data
    print("\n6. Sample collected data:")
    sample_data = collector.get_collected_data(limit=3)
    for i, data in enumerate(sample_data, 1):
        print(f"  {i}. [{data.source}] {data.text[:100]}...")

if __name__ == "__main__":
    test_data_collector()