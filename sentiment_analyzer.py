"""
K-Pop Sentiment Analyzer

Main sentiment analysis engine that classifies text into K-Pop specific sentiment categories.
Uses keyword matching, pattern recognition, and machine learning approaches.
"""

import re
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import Counter

from text_preprocessor import TextPreprocessor
from sentiment_labels import SENTIMENT_LABELS, get_sentiment_label_info

@dataclass
class SentimentResult:
    """Data class for sentiment analysis results"""
    text: str
    predicted_label: int
    confidence: float
    label_name: str
    risk_level: str
    reasoning: str
    metadata: Dict
    timestamp: datetime

class KPopSentimentAnalyzer:
    def __init__(self, db_path: str = "sentiment_data.db"):
        self.preprocessor = TextPreprocessor()
        self.db_path = db_path
        self.init_database()
        
        # Compile keyword patterns for efficiency
        self.keyword_patterns = self._compile_keyword_patterns()
        
        # Sentiment indicators
        self.positive_indicators = [
            'love', 'amazing', 'perfect', 'best', 'incredible', 'talented', 'beautiful',
            'stunning', 'iconic', 'legendary', 'queen', 'king', 'slay', 'serve'
        ]
        
        self.negative_indicators = [
            'hate', 'terrible', 'worst', 'awful', 'disappointing', 'overrated',
            'flop', 'cringe', 'annoying', 'fake', 'problematic'
        ]
        
        self.competitive_indicators = [
            'outsold', 'better than', 'superior', 'charts', 'numbers', 'sales',
            'views', 'streams', 'your faves', 'could never'
        ]
        
        self.sarcasm_indicators = [
            'sure', 'right', 'okay', 'imagine', 'literally', 'totally',
            'obviously', 'definitely'
        ]
        
    def init_database(self):
        """Initialize SQLite database for storing sentiment data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sentiment_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                predicted_label INTEGER NOT NULL,
                confidence REAL NOT NULL,
                label_name TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                reasoning TEXT,
                metadata TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_corrected_label INTEGER,
                is_verified BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def _compile_keyword_patterns(self) -> Dict[int, List[re.Pattern]]:
        """Compile regex patterns for each sentiment label's keywords"""
        patterns = {}
        for label_id, label_info in SENTIMENT_LABELS.items():
            patterns[label_id] = [
                re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
                for keyword in label_info['keywords']
            ]
        return patterns
        
    def _calculate_keyword_scores(self, text: str) -> Dict[int, float]:
        """Calculate keyword matching scores for each sentiment label"""
        scores = {}
        text_lower = text.lower()
        
        for label_id, patterns in self.keyword_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(pattern.findall(text))
                score += matches
            
            # Normalize by text length
            word_count = len(text.split())
            if word_count > 0:
                scores[label_id] = score / word_count
            else:
                scores[label_id] = 0
                
        return scores
        
    def _detect_patterns(self, text: str) -> Dict[str, float]:
        """Detect various linguistic patterns in the text"""
        text_lower = text.lower()
        patterns = {}
        
        # Exclamation and caps usage (enthusiasm)
        exclamation_count = text.count('!')
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        patterns['enthusiasm'] = min((exclamation_count * 0.2 + caps_ratio * 2), 1.0)
        
        # Question marks (uncertainty/confusion)
        question_count = text.count('?')
        patterns['questioning'] = min(question_count * 0.3, 1.0)
        
        # Emoji usage
        emoji_count = len(self.preprocessor.emoji_pattern.findall(text))
        patterns['emoji_usage'] = min(emoji_count * 0.1, 1.0)
        
        # Competitive language
        competitive_score = sum(1 for indicator in self.competitive_indicators 
                              if indicator in text_lower)
        patterns['competitive'] = min(competitive_score * 0.2, 1.0)
        
        # Sarcasm indicators
        sarcasm_score = sum(1 for indicator in self.sarcasm_indicators 
                           if indicator in text_lower)
        patterns['sarcasm'] = min(sarcasm_score * 0.3, 1.0)
        
        # Defensive language
        defensive_words = ['protect', 'defend', 'leave alone', 'stop', 'enough']
        defensive_score = sum(1 for word in defensive_words if word in text_lower)
        patterns['defensive'] = min(defensive_score * 0.3, 1.0)
        
        # Temporal references
        temporal_words = ['remember', 'miss', 'throwback', 'back then', 'used to']
        temporal_score = sum(1 for word in temporal_words if word in text_lower)
        patterns['nostalgic'] = min(temporal_score * 0.4, 1.0)
        
        # Future references
        future_words = ['comeback', 'soon', 'next', 'upcoming', 'can\'t wait']
        future_score = sum(1 for word in future_words if word in text_lower)
        patterns['anticipatory'] = min(future_score * 0.4, 1.0)
        
        return patterns
        
    def _rule_based_classification(self, text: str, keyword_scores: Dict[int, float], 
                                 patterns: Dict[str, float]) -> Tuple[int, float, str]:
        """Apply rule-based classification logic"""
        text_lower = text.lower()
        
        # Check for malicious coordinated content (highest priority)
        malicious_keywords = ['expose', 'thread', 'receipts', 'cancel', 'boycott', 'problematic']
        if any(keyword in text_lower for keyword in malicious_keywords):
            return 9, 0.9, "Detected malicious/coordinated attack keywords"
            
        # Check for competitive rivalry
        if patterns['competitive'] > 0.3 or keyword_scores.get(7, 0) > 0.1:
            return 7, 0.8, "High competitive/rivalry language detected"
            
        # Check for sarcasm
        if patterns['sarcasm'] > 0.4:
            return 8, 0.7, "Sarcastic tone indicators detected"
            
        # Check for defensive protection
        if patterns['defensive'] > 0.3:
            return 4, 0.7, "Protective/defensive language detected"
            
        # Check for nostalgia
        if patterns['nostalgic'] > 0.3:
            return 2, 0.7, "Nostalgic temporal references detected"
            
        # Check for anticipation
        if patterns['anticipatory'] > 0.3:
            return 3, 0.7, "Anticipatory future references detected"
            
        # Check for enthusiasm
        if patterns['enthusiasm'] > 0.4 and keyword_scores.get(1, 0) > 0.05:
            return 1, 0.8, "High enthusiasm and positive keywords detected"
            
        # Check for mixed feelings
        if 'but' in text_lower or 'however' in text_lower:
            return 10, 0.6, "Conflicting sentiment indicators detected"
            
        # Check for critical disappointment
        negative_score = sum(1 for word in self.negative_indicators if word in text_lower)
        if negative_score > 0 and patterns['enthusiasm'] < 0.2:
            return 5, 0.6, "Critical/disappointed tone detected"
            
        # Default to neutral if no strong patterns
        if max(keyword_scores.values()) < 0.05 and max(patterns.values()) < 0.3:
            return 6, 0.5, "No strong sentiment indicators, defaulting to neutral"
            
        # Use highest keyword score
        best_label = max(keyword_scores.items(), key=lambda x: x[1])
        return best_label[0], min(best_label[1] * 2, 0.9), f"Highest keyword match for label {best_label[0]}"
        
    def analyze_sentiment(self, text: str, save_to_db: bool = True) -> SentimentResult:
        """
        Analyze sentiment of input text
        
        Args:
            text: Input text to analyze
            save_to_db: Whether to save results to database
            
        Returns:
            SentimentResult object with analysis results
        """
        # Preprocess text
        processed_text = self.preprocessor.preprocess_text(text)
        metadata = self.preprocessor.extract_metadata(text)
        
        # Calculate scores and patterns
        keyword_scores = self._calculate_keyword_scores(processed_text)
        patterns = self._detect_patterns(text)
        
        # Apply classification
        predicted_label, confidence, reasoning = self._rule_based_classification(
            processed_text, keyword_scores, patterns
        )
        
        # Get label information
        label_info = get_sentiment_label_info(predicted_label)
        label_name = label_info['name']
        risk_level = label_info['risk_level']
        
        # Create result
        result = SentimentResult(
            text=text,
            predicted_label=predicted_label,
            confidence=confidence,
            label_name=label_name,
            risk_level=risk_level,
            reasoning=reasoning,
            metadata={
                'keyword_scores': keyword_scores,
                'patterns': patterns,
                'extracted_elements': metadata,
                'processed_text': processed_text
            },
            timestamp=datetime.now()
        )
        
        # Save to database
        if save_to_db:
            self._save_to_database(result)
            
        return result
        
    def _save_to_database(self, result: SentimentResult):
        """Save sentiment analysis result to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sentiment_analysis 
            (text, predicted_label, confidence, label_name, risk_level, reasoning, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            result.text,
            result.predicted_label,
            result.confidence,
            result.label_name,
            result.risk_level,
            result.reasoning,
            json.dumps(result.metadata)
        ))
        
        conn.commit()
        conn.close()
        
    def get_analysis_history(self, limit: int = 100) -> List[Dict]:
        """Get recent analysis history from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM sentiment_analysis 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
        
    def update_label(self, analysis_id: int, corrected_label: int):
        """Update a sentiment analysis with user correction"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE sentiment_analysis 
            SET user_corrected_label = ?, is_verified = TRUE
            WHERE id = ?
        ''', (corrected_label, analysis_id))
        
        conn.commit()
        conn.close()
        
    def delete_analysis(self, analysis_id: int):
        """Delete a sentiment analysis record"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM sentiment_analysis WHERE id = ?', (analysis_id,))
        
        conn.commit()
        conn.close()
        
    def get_statistics(self) -> Dict:
        """Get analysis statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total analyses
        cursor.execute('SELECT COUNT(*) FROM sentiment_analysis')
        total_analyses = cursor.fetchone()[0]
        
        # Label distribution
        cursor.execute('''
            SELECT predicted_label, label_name, COUNT(*) as count
            FROM sentiment_analysis 
            GROUP BY predicted_label, label_name
            ORDER BY count DESC
        ''')
        label_distribution = cursor.fetchall()
        
        # Risk level distribution
        cursor.execute('''
            SELECT risk_level, COUNT(*) as count
            FROM sentiment_analysis 
            GROUP BY risk_level
        ''')
        risk_distribution = cursor.fetchall()
        
        # Average confidence
        cursor.execute('SELECT AVG(confidence) FROM sentiment_analysis')
        avg_confidence = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_analyses': total_analyses,
            'label_distribution': label_distribution,
            'risk_distribution': risk_distribution,
            'average_confidence': round(avg_confidence, 3)
        }

# Example usage
if __name__ == "__main__":
    analyzer = KPopSentimentAnalyzer()
    
    # Test examples
    test_texts = [
        "OMG they absolutely SLAYED this performance! 🔥 Best group ever!",
        "I miss their debut era so much, those were simpler times",
        "They outsold your faves again, stay pressed 💅",
        "Sure, that performance was 'amazing' 🙄",
        "THREAD: Why this group is problematic and needs to be cancelled",
        "The album will be released on March 15th according to the company",
        "I love the song but the music video was disappointing"
    ]
    
    print("K-Pop Sentiment Analysis Results:")
    print("=" * 60)
    
    for text in test_texts:
        result = analyzer.analyze_sentiment(text)
        print(f"\nText: {text}")
        print(f"Label: {result.label_name} (ID: {result.predicted_label})")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Risk Level: {result.risk_level}")
        print(f"Reasoning: {result.reasoning}")
        print("-" * 40)