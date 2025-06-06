"""
Text Preprocessing Module for K-Pop Sentiment Analysis

Handles cleaning and normalization of user-provided text including:
- URL removal
- Mention removal (@username)
- Hashtag processing
- Whitespace normalization
- Emoji handling
- Special character cleaning
"""

import re
import string
from typing import List, Dict, Optional

class TextPreprocessor:
    def __init__(self):
        # Compile regex patterns for efficiency
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.mention_pattern = re.compile(r'@[A-Za-z0-9_]+')
        self.hashtag_pattern = re.compile(r'#[A-Za-z0-9_]+')
        self.whitespace_pattern = re.compile(r'\s+')
        self.emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE
        )
        
    def remove_urls(self, text: str) -> str:
        """Remove URLs from text"""
        return self.url_pattern.sub('', text)
    
    def remove_mentions(self, text: str) -> str:
        """Remove @mentions from text"""
        return self.mention_pattern.sub('', text)
    
    def process_hashtags(self, text: str, keep_hashtags: bool = False) -> str:
        """
        Process hashtags - either remove them or keep the text without #
        """
        if keep_hashtags:
            # Keep hashtag text but remove the # symbol
            return self.hashtag_pattern.sub(lambda m: m.group(0)[1:], text)
        else:
            # Remove hashtags entirely
            return self.hashtag_pattern.sub('', text)
    
    def handle_emojis(self, text: str, remove_emojis: bool = False) -> str:
        """
        Handle emojis - either remove them or keep them
        """
        if remove_emojis:
            return self.emoji_pattern.sub('', text)
        return text
    
    def normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace - collapse multiple spaces/newlines into single spaces"""
        return self.whitespace_pattern.sub(' ', text).strip()
    
    def clean_special_chars(self, text: str, keep_punctuation: bool = True) -> str:
        """
        Clean special characters while optionally preserving punctuation
        """
        if keep_punctuation:
            # Keep basic punctuation but remove other special chars
            allowed_chars = string.ascii_letters + string.digits + string.punctuation + ' '
            return ''.join(char for char in text if char in allowed_chars or ord(char) > 127)
        else:
            # Remove all punctuation except basic sentence endings
            keep_punct = '.!?'
            return ''.join(char for char in text if char.isalnum() or char.isspace() or char in keep_punct)
    
    def preprocess_text(self, 
                       text: str,
                       remove_urls: bool = True,
                       remove_mentions: bool = True,
                       keep_hashtags: bool = True,
                       remove_emojis: bool = False,
                       keep_punctuation: bool = True,
                       normalize_case: bool = False) -> str:
        """
        Main preprocessing function that applies all cleaning steps
        
        Args:
            text: Input text to preprocess
            remove_urls: Whether to remove URLs
            remove_mentions: Whether to remove @mentions
            keep_hashtags: Whether to keep hashtag text (without #)
            remove_emojis: Whether to remove emojis
            keep_punctuation: Whether to keep punctuation
            normalize_case: Whether to convert to lowercase
            
        Returns:
            Preprocessed text string
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Apply preprocessing steps in order
        processed_text = text
        
        if remove_urls:
            processed_text = self.remove_urls(processed_text)
            
        if remove_mentions:
            processed_text = self.remove_mentions(processed_text)
            
        processed_text = self.process_hashtags(processed_text, keep_hashtags)
        processed_text = self.handle_emojis(processed_text, remove_emojis)
        processed_text = self.clean_special_chars(processed_text, keep_punctuation)
        processed_text = self.normalize_whitespace(processed_text)
        
        if normalize_case:
            processed_text = processed_text.lower()
            
        return processed_text
    
    def extract_metadata(self, text: str) -> Dict[str, List[str]]:
        """
        Extract metadata from text (URLs, mentions, hashtags, emojis)
        
        Returns:
            Dictionary containing lists of extracted elements
        """
        metadata = {
            'urls': self.url_pattern.findall(text),
            'mentions': self.mention_pattern.findall(text),
            'hashtags': self.hashtag_pattern.findall(text),
            'emojis': self.emoji_pattern.findall(text)
        }
        return metadata
    
    def get_text_stats(self, text: str) -> Dict[str, int]:
        """
        Get basic statistics about the text
        
        Returns:
            Dictionary with text statistics
        """
        metadata = self.extract_metadata(text)
        words = text.split()
        
        stats = {
            'char_count': len(text),
            'word_count': len(words),
            'url_count': len(metadata['urls']),
            'mention_count': len(metadata['mentions']),
            'hashtag_count': len(metadata['hashtags']),
            'emoji_count': len(metadata['emojis'])
        }
        return stats

# Example usage and testing
if __name__ == "__main__":
    preprocessor = TextPreprocessor()
    
    # Test text with various elements
    test_text = """
    OMG @BTS_official just dropped the most AMAZING teaser!!! 🔥🔥🔥 
    Check it out: https://youtube.com/watch?v=example 
    #BTS #ARMY #NewEra    This is going to be ICONIC! 
    Can't wait for the full MV 😍
    """
    
    print("Original text:")
    print(test_text)
    print("\n" + "="*50 + "\n")
    
    print("Preprocessed text:")
    processed = preprocessor.preprocess_text(test_text)
    print(processed)
    print("\n" + "="*50 + "\n")
    
    print("Extracted metadata:")
    metadata = preprocessor.extract_metadata(test_text)
    for key, value in metadata.items():
        print(f"{key}: {value}")
    print("\n" + "="*50 + "\n")
    
    print("Text statistics:")
    stats = preprocessor.get_text_stats(test_text)
    for key, value in stats.items():
        print(f"{key}: {value}")