"""
YouTube Data API Integration Example
Demonstrates how to collect K-Pop content and comments for sentiment analysis
"""

import os
import googleapiclient.discovery
from googleapiclient.errors import HttpError
import pandas as pd
from datetime import datetime, timedelta
import time
import json

class YouTubeKPopCollector:
    def __init__(self, api_key):
        """
        Initialize YouTube Data API client
        
        Args:
            api_key (str): YouTube Data API key
        """
        self.api_key = api_key
        self.youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
        
        # K-Pop related channels (examples)
        self.kpop_channels = {
            'HYBE LABELS': 'UC3IZKseVpdzPSBaWxBxundA',
            'SMTOWN': 'UCEf_Bc-KVd7onSeifS3py9g',
            'YG Entertainment': 'UCOtgOJGLdLhKOKs-2_BbNzQ',
            'JYP Entertainment': 'UCaO6TYtlC8U5ttz62hTrZgg',
            'Stone Music Entertainment': 'UCOmHUn--16B90oW2L6FRR3A'
        }
        
        # K-Pop search terms
        self.kpop_keywords = [
            'BTS', 'BLACKPINK', 'TWICE', 'Stray Kids', 'ITZY', 'aespa',
            'NewJeans', 'IVE', 'NMIXX', 'LE SSERAFIM', 'SEVENTEEN',
            'ENHYPEN', 'TXT', 'ATEEZ', 'GIDLE', 'Red Velvet'
        ]

    def search_kpop_videos(self, query, max_results=50, published_after=None):
        """
        Search for K-Pop videos
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results
            published_after (datetime): Only videos published after this date
            
        Returns:
            list: Video data
        """
        try:
            search_params = {
                'part': 'snippet',
                'q': query + ' kpop',
                'type': 'video',
                'maxResults': max_results,
                'order': 'relevance',
                'regionCode': 'US',
                'relevanceLanguage': 'en'
            }
            
            if published_after:
                search_params['publishedAfter'] = published_after.isoformat() + 'Z'
            
            search_response = self.youtube.search().list(**search_params).execute()
            
            videos = []
            for item in search_response['items']:
                video_data = {
                    'video_id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'channel_id': item['snippet']['channelId'],
                    'channel_title': item['snippet']['channelTitle'],
                    'published_at': item['snippet']['publishedAt'],
                    'thumbnail_url': item['snippet']['thumbnails']['high']['url']
                }
                videos.append(video_data)
            
            return videos
            
        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
            return []

    def get_video_comments(self, video_id, max_results=100):
        """
        Get comments from a specific video
        
        Args:
            video_id (str): YouTube video ID
            max_results (int): Maximum number of comments to fetch
            
        Returns:
            list: Comment data
        """
        try:
            comments = []
            next_page_token = None
            
            while len(comments) < max_results:
                request_params = {
                    'part': 'snippet,replies',
                    'videoId': video_id,
                    'maxResults': min(100, max_results - len(comments)),
                    'order': 'relevance',
                    'textFormat': 'plainText'
                }
                
                if next_page_token:
                    request_params['pageToken'] = next_page_token
                
                response = self.youtube.commentThreads().list(**request_params).execute()
                
                for item in response['items']:
                    comment = item['snippet']['topLevelComment']['snippet']
                    comment_data = {
                        'comment_id': item['id'],
                        'video_id': video_id,
                        'author_name': comment['authorDisplayName'],
                        'text': comment['textDisplay'],
                        'like_count': comment['likeCount'],
                        'published_at': comment['publishedAt'],
                        'reply_count': item['snippet']['totalReplyCount']
                    }
                    comments.append(comment_data)
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                    
                time.sleep(0.1)  # Rate limiting
            
            return comments[:max_results]
            
        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
            return []

# Example usage
if __name__ == "__main__":
    API_KEY = "YOUR_YOUTUBE_API_KEY_HERE"
    
    if API_KEY == "YOUR_YOUTUBE_API_KEY_HERE":
        print("Please set your YouTube Data API key!")
        exit(1)
    
    collector = YouTubeKPopCollector(API_KEY)
    
    # Search for BTS content
    videos = collector.search_kpop_videos("BTS", max_results=5)
    for video in videos:
        print(f"- {video['title']} ({video['channel_title']})")