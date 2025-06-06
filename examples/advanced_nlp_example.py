"""
Advanced NLP with NLTK Integration Example
Demonstrates enhanced sentiment analysis using NLTK and other NLP libraries
"""

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.chunk import ne_chunk
from nltk.tag import pos_tag
from textblob import TextBlob
import re
from collections import Counter
import numpy as np

class AdvancedKPopNLPAnalyzer:
    def __init__(self):
        """Initialize the advanced NLP analyzer with required NLTK data"""
        # Download required NLTK data
        nltk_downloads = [
            'vader_lexicon', 'punkt', 'stopwords', 'averaged_perceptron_tagger',
            'maxent_ne_chunker', 'words', 'brown', 'wordnet'
        ]
        
        for item in nltk_downloads:
            try:
                nltk.data.find(f'tokenizers/{item}')
            except LookupError:
                print(f"Downloading {item}...")
                nltk.download(item, quiet=True)
        
        self.sia = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words('english'))
        
        # K-Pop specific entities and terms
        self.kpop_entities = {
            'groups': ['BTS', 'BLACKPINK', 'TWICE', 'Stray Kids', 'ITZY', 'aespa', 
                      'NewJeans', 'IVE', 'NMIXX', 'LE SSERAFIM', 'SEVENTEEN'],
            'members': ['RM', 'Jin', 'Suga', 'J-Hope', 'Jimin', 'V', 'Jungkook',
                       'Jisoo', 'Jennie', 'Rosé', 'Lisa', 'Nayeon', 'Jeongyeon'],
            'companies': ['HYBE', 'YG', 'SM', 'JYP', 'Starship', 'ADOR'],
            'terms': ['comeback', 'debut', 'bias', 'stan', 'fandom', 'choreography',
                     'visual', 'vocal', 'rapper', 'maknae', 'leader', 'center']
        }
        
        # Emotion lexicon for multi-dimensional analysis
        self.emotion_lexicon = {
            'joy': ['happy', 'excited', 'amazing', 'love', 'perfect', 'incredible'],
            'anger': ['hate', 'angry', 'furious', 'disgusting', 'terrible', 'awful'],
            'fear': ['scared', 'worried', 'anxious', 'nervous', 'concerned'],
            'sadness': ['sad', 'disappointed', 'heartbroken', 'depressed', 'upset'],
            'surprise': ['shocked', 'surprised', 'unexpected', 'wow', 'omg'],
            'disgust': ['disgusting', 'gross', 'revolting', 'sick', 'nasty']
        }

    def analyze_comprehensive_sentiment(self, text):
        """
        Perform comprehensive sentiment analysis
        
        Args:
            text (str): Input text to analyze
            
        Returns:
            dict: Comprehensive analysis results
        """
        # Basic preprocessing
        cleaned_text = self.preprocess_text(text)
        
        # VADER sentiment analysis
        vader_scores = self.sia.polarity_scores(text)
        
        # TextBlob sentiment analysis
        blob = TextBlob(text)
        textblob_sentiment = {
            'polarity': blob.sentiment.polarity,
            'subjectivity': blob.sentiment.subjectivity
        }
        
        # Multi-dimensional emotion analysis
        emotions = self.analyze_emotions(text)
        
        # K-Pop entity extraction
        entities = self.extract_kpop_entities(text)
        
        # Linguistic features
        linguistic_features = self.analyze_linguistic_features(text)
        
        # Advanced sarcasm detection
        sarcasm_score = self.detect_sarcasm_advanced(text)
        
        # Combine all analyses
        comprehensive_result = {
            'text': text,
            'cleaned_text': cleaned_text,
            'vader_sentiment': vader_scores,
            'textblob_sentiment': textblob_sentiment,
            'emotions': emotions,
            'kpop_entities': entities,
            'linguistic_features': linguistic_features,
            'sarcasm_score': sarcasm_score,
            'overall_sentiment': self.calculate_overall_sentiment(vader_scores, emotions),
            'confidence': self.calculate_confidence(vader_scores, emotions, linguistic_features)
        }
        
        return comprehensive_result

    def preprocess_text(self, text):
        """Clean and preprocess text"""
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove mentions and hashtags
        text = re.sub(r'@\w+|#\w+', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def analyze_emotions(self, text):
        """
        Analyze multiple emotions in text
        
        Args:
            text (str): Input text
            
        Returns:
            dict: Emotion scores
        """
        text_lower = text.lower()
        emotion_scores = {}
        
        for emotion, words in self.emotion_lexicon.items():
            score = sum(1 for word in words if word in text_lower)
            # Normalize by text length
            word_count = len(text.split())
            emotion_scores[emotion] = score / word_count if word_count > 0 else 0
        
        return emotion_scores

    def extract_kpop_entities(self, text):
        """
        Extract K-Pop related entities from text
        
        Args:
            text (str): Input text
            
        Returns:
            dict: Extracted entities by category
        """
        extracted_entities = {category: [] for category in self.kpop_entities.keys()}
        
        text_upper = text.upper()
        
        for category, entities in self.kpop_entities.items():
            for entity in entities:
                if entity.upper() in text_upper:
                    extracted_entities[category].append(entity)
        
        return extracted_entities

    def analyze_linguistic_features(self, text):
        """
        Analyze linguistic features of the text
        
        Args:
            text (str): Input text
            
        Returns:
            dict: Linguistic features
        """
        # Tokenize
        tokens = word_tokenize(text)
        sentences = sent_tokenize(text)
        
        # POS tagging
        pos_tags = pos_tag(tokens)
        
        # Count different POS types
        pos_counts = Counter(tag for word, tag in pos_tags)
        
        # Calculate features
        features = {
            'word_count': len(tokens),
            'sentence_count': len(sentences),
            'avg_sentence_length': len(tokens) / len(sentences) if sentences else 0,
            'exclamation_count': text.count('!'),
            'question_count': text.count('?'),
            'caps_ratio': sum(1 for c in text if c.isupper()) / len(text) if text else 0,
            'pos_distribution': dict(pos_counts),
            'unique_words': len(set(token.lower() for token in tokens if token.isalpha())),
            'lexical_diversity': len(set(tokens)) / len(tokens) if tokens else 0
        }
        
        return features

    def detect_sarcasm_advanced(self, text):
        """
        Advanced sarcasm detection using multiple indicators
        
        Args:
            text (str): Input text
            
        Returns:
            float: Sarcasm probability score (0-1)
        """
        sarcasm_indicators = {
            'quotation_marks': len(re.findall(r'["\'].*?["\']', text)) * 0.3,
            'sure_right_okay': len(re.findall(r'\b(sure|right|okay|yeah right)\b', text.lower())) * 0.4,
            'excessive_punctuation': len(re.findall(r'[!?]{2,}', text)) * 0.2,
            'contradictory_sentiment': 0,  # Would need more complex analysis
            'emoji_mismatch': 0  # Would need emoji sentiment analysis
        }
        
        # Check for contradictory patterns
        positive_words = ['great', 'amazing', 'wonderful', 'perfect']
        negative_context = ['not', "isn't", "wasn't", "doesn't"]
        
        for pos_word in positive_words:
            for neg_word in negative_context:
                if f"{neg_word} {pos_word}" in text.lower():
                    sarcasm_indicators['contradictory_sentiment'] += 0.5
        
        # Calculate overall sarcasm score
        sarcasm_score = min(sum(sarcasm_indicators.values()), 1.0)
        
        return sarcasm_score

    def calculate_overall_sentiment(self, vader_scores, emotions):
        """
        Calculate overall sentiment combining multiple sources
        
        Args:
            vader_scores (dict): VADER sentiment scores
            emotions (dict): Emotion analysis results
            
        Returns:
            dict: Overall sentiment classification
        """
        # Weight different sentiment sources
        vader_compound = vader_scores['compound']
        
        # Calculate emotion-based sentiment
        positive_emotions = emotions.get('joy', 0)
        negative_emotions = emotions.get('anger', 0) + emotions.get('sadness', 0) + emotions.get('disgust', 0)
        
        emotion_sentiment = positive_emotions - negative_emotions
        
        # Combine scores
        combined_score = (vader_compound * 0.7) + (emotion_sentiment * 0.3)
        
        # Classify sentiment
        if combined_score >= 0.1:
            sentiment_label = 'positive'
        elif combined_score <= -0.1:
            sentiment_label = 'negative'
        else:
            sentiment_label = 'neutral'
        
        return {
            'label': sentiment_label,
            'score': combined_score,
            'confidence': abs(combined_score)
        }

    def calculate_confidence(self, vader_scores, emotions, linguistic_features):
        """
        Calculate confidence score for the analysis
        
        Args:
            vader_scores (dict): VADER sentiment scores
            emotions (dict): Emotion analysis results
            linguistic_features (dict): Linguistic features
            
        Returns:
            float: Confidence score (0-1)
        """
        # Factors that increase confidence
        confidence_factors = []
        
        # Strong VADER compound score
        confidence_factors.append(abs(vader_scores['compound']))
        
        # Clear emotional indicators
        max_emotion = max(emotions.values()) if emotions.values() else 0
        confidence_factors.append(min(max_emotion * 2, 1.0))
        
        # Text length (longer texts generally more reliable)
        word_count = linguistic_features.get('word_count', 0)
        length_factor = min(word_count / 20, 1.0)  # Normalize to 20 words
        confidence_factors.append(length_factor)
        
        # Lexical diversity
        diversity = linguistic_features.get('lexical_diversity', 0)
        confidence_factors.append(diversity)
        
        # Calculate weighted average
        weights = [0.4, 0.3, 0.2, 0.1]
        confidence = sum(factor * weight for factor, weight in zip(confidence_factors, weights))
        
        return min(confidence, 1.0)

# Example usage and testing
if __name__ == "__main__":
    analyzer = AdvancedKPopNLPAnalyzer()
    
    # Test examples
    test_texts = [
        "OMG BTS absolutely SLAYED this performance! Jungkook's vocals were incredible! 🔥",
        "I miss BLACKPINK's old music style, their recent songs just don't hit the same...",
        "Sure, TWICE's new comeback is 'amazing' 🙄 Just another generic pop song",
        "Can't wait for Stray Kids' next album! Their music keeps getting better and better!",
        "The choreography in this ITZY video is so complex and well-executed. Professional work.",
        "Why do people even stan this group? They have no talent whatsoever 😤"
    ]
    
    print("Advanced K-Pop NLP Analysis Results:")
    print("=" * 60)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\nExample {i}: {text}")
        print("-" * 40)
        
        result = analyzer.analyze_comprehensive_sentiment(text)
        
        print(f"Overall Sentiment: {result['overall_sentiment']['label'].upper()} "
              f"(score: {result['overall_sentiment']['score']:.3f})")
        print(f"Confidence: {result['confidence']:.3f}")
        
        print(f"VADER Scores: {result['vader_sentiment']}")
        
        print("Emotions:", end=" ")
        for emotion, score in result['emotions'].items():
            if score > 0:
                print(f"{emotion}: {score:.3f}", end=" ")
        print()
        
        if any(result['kpop_entities'].values()):
            print("K-Pop Entities:", end=" ")
            for category, entities in result['kpop_entities'].items():
                if entities:
                    print(f"{category}: {entities}", end=" ")
            print()
        
        if result['sarcasm_score'] > 0.3:
            print(f"Sarcasm Detected: {result['sarcasm_score']:.3f}")
        
        print(f"Linguistic Features: {result['linguistic_features']['word_count']} words, "
              f"{result['linguistic_features']['exclamation_count']} exclamations, "
              f"{result['linguistic_features']['caps_ratio']:.2f} caps ratio")