"""
Multi-Language Processor for K-Pop Sentiment Analysis
Supports multiple languages commonly used by K-Pop fans worldwide
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Language detection libraries
try:
    from langdetect import detect, detect_langs
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

try:
    import fasttext
    FASTTEXT_AVAILABLE = True
except ImportError:
    FASTTEXT_AVAILABLE = False

@dataclass
class LanguageDetectionResult:
    """Result of language detection"""
    detected_language: str
    confidence: float
    supported: bool
    fallback_used: bool = False
    detection_methods: Dict[str, Dict] = None

@dataclass
class ProcessingResult:
    """Result of text processing"""
    tokens: List[str]
    cleaned_text: str
    sentiment_indicators: Dict[str, float]
    cultural_markers: List[str]
    language_specific_features: Dict[str, any]
    confidence_factors: Dict[str, float]

class LanguageProcessor(ABC):
    """Abstract base class for language processors"""
    
    @abstractmethod
    def process(self, text: str, language_info: LanguageDetectionResult) -> ProcessingResult:
        """Process text in specific language"""
        pass
    
    @abstractmethod
    def get_sentiment_lexicon(self) -> Dict[str, List[str]]:
        """Get language-specific sentiment lexicon"""
        pass

class EnglishProcessor(LanguageProcessor):
    """English language processor"""
    
    def __init__(self):
        self.sentiment_lexicon = self.get_sentiment_lexicon()
        self.kpop_terms = self.get_kpop_terms()
    
    def process(self, text: str, language_info: LanguageDetectionResult) -> ProcessingResult:
        """Process English text"""
        # Basic tokenization
        tokens = self.tokenize(text)
        cleaned_text = self.clean_text(text)
        
        # Sentiment analysis
        sentiment_indicators = self.analyze_sentiment_indicators(tokens)
        
        # K-Pop cultural markers
        cultural_markers = self.detect_cultural_markers(text)
        
        # Language-specific features
        features = self.extract_english_features(text, tokens)
        
        # Confidence factors
        confidence_factors = self.calculate_confidence_factors(text, tokens, language_info)
        
        return ProcessingResult(
            tokens=tokens,
            cleaned_text=cleaned_text,
            sentiment_indicators=sentiment_indicators,
            cultural_markers=cultural_markers,
            language_specific_features=features,
            confidence_factors=confidence_factors
        )
    
    def get_sentiment_lexicon(self) -> Dict[str, List[str]]:
        """English sentiment lexicon for K-Pop context"""
        return {
            'positive': [
                'love', 'amazing', 'perfect', 'incredible', 'best', 'beautiful', 
                'talented', 'awesome', 'fantastic', 'wonderful', 'brilliant',
                'slay', 'iconic', 'legendary', 'queen', 'king', 'goddess', 'god'
            ],
            'negative': [
                'hate', 'terrible', 'worst', 'awful', 'disappointing', 'bad',
                'ugly', 'boring', 'overrated', 'trash', 'flop', 'cringe'
            ],
            'enthusiasm': [
                'omg', 'wow', 'yasss', 'periodt', 'facts', 'tea', 'mood',
                'literally', 'actually', 'honestly', 'seriously'
            ],
            'sarcasm': [
                'sure', 'right', 'okay', 'totally', 'obviously', 'clearly',
                'imagine', 'not', 'literally', 'actually'
            ],
            'competitive': [
                'better', 'superior', 'outsold', 'outperformed', 'dominated',
                'crushed', 'destroyed', 'owned', 'slayed'
            ]
        }
    
    def get_kpop_terms(self) -> List[str]:
        """K-Pop specific terms in English"""
        return [
            'bias', 'stan', 'ult', 'comeback', 'debut', 'mv', 'choreography',
            'visual', 'vocal', 'rapper', 'dancer', 'leader', 'maknae',
            'fandom', 'army', 'blink', 'once', 'stay', 'midzy', 'my'
        ]
    
    def tokenize(self, text: str) -> List[str]:
        """Simple tokenization for English"""
        # Remove URLs, mentions, hashtags for tokenization
        clean_text = re.sub(r'http\S+|www\S+|@\w+|#\w+', '', text)
        # Split on whitespace and punctuation
        tokens = re.findall(r'\b\w+\b', clean_text.lower())
        return tokens
    
    def clean_text(self, text: str) -> str:
        """Clean English text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def analyze_sentiment_indicators(self, tokens: List[str]) -> Dict[str, float]:
        """Analyze sentiment indicators in tokens"""
        indicators = {}
        
        for category, words in self.sentiment_lexicon.items():
            count = sum(1 for token in tokens if token in words)
            indicators[category] = count / len(tokens) if tokens else 0
        
        return indicators
    
    def detect_cultural_markers(self, text: str) -> List[str]:
        """Detect K-Pop cultural markers"""
        markers = []
        text_lower = text.lower()
        
        for term in self.kpop_terms:
            if term in text_lower:
                markers.append(term)
        
        return markers
    
    def extract_english_features(self, text: str, tokens: List[str]) -> Dict[str, any]:
        """Extract English-specific features"""
        return {
            'exclamation_count': text.count('!'),
            'question_count': text.count('?'),
            'caps_ratio': sum(1 for c in text if c.isupper()) / len(text) if text else 0,
            'avg_word_length': sum(len(token) for token in tokens) / len(tokens) if tokens else 0,
            'repeated_letters': len(re.findall(r'(.)\1{2,}', text.lower())),
            'emoji_count': len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', text))
        }
    
    def calculate_confidence_factors(self, text: str, tokens: List[str], language_info: LanguageDetectionResult) -> Dict[str, float]:
        """Calculate confidence factors for English processing"""
        factors = {}
        
        # Language detection confidence
        factors['language_detection'] = language_info.confidence
        
        # Text length factor
        word_count = len(tokens)
        if word_count < 3:
            factors['text_length'] = 0.3
        elif word_count > 100:
            factors['text_length'] = 0.7
        else:
            factors['text_length'] = 0.9
        
        # Vocabulary coverage
        known_words = sum(1 for token in tokens if self.is_known_word(token))
        factors['vocabulary_coverage'] = known_words / len(tokens) if tokens else 0
        
        # Cultural context
        kpop_terms_found = len(self.detect_cultural_markers(text))
        factors['cultural_context'] = min(kpop_terms_found / 3, 1.0)
        
        return factors
    
    def is_known_word(self, word: str) -> bool:
        """Check if word is in known vocabulary"""
        all_words = []
        for word_list in self.sentiment_lexicon.values():
            all_words.extend(word_list)
        all_words.extend(self.kpop_terms)
        
        return word in all_words

class KoreanProcessor(LanguageProcessor):
    """Korean language processor"""
    
    def __init__(self):
        self.sentiment_lexicon = self.get_sentiment_lexicon()
        self.kpop_terms = self.get_kpop_terms()
        
        # Try to import Korean NLP library
        try:
            from konlpy.tag import Okt
            self.tokenizer = Okt()
            self.konlpy_available = True
        except ImportError:
            self.tokenizer = None
            self.konlpy_available = False
    
    def process(self, text: str, language_info: LanguageDetectionResult) -> ProcessingResult:
        """Process Korean text"""
        if self.konlpy_available:
            tokens = self.tokenizer.morphs(text)
        else:
            # Fallback tokenization
            tokens = self.simple_korean_tokenize(text)
        
        cleaned_text = self.clean_korean_text(text)
        sentiment_indicators = self.analyze_korean_sentiment(tokens)
        cultural_markers = self.detect_korean_cultural_markers(text)
        features = self.extract_korean_features(text, tokens)
        confidence_factors = self.calculate_korean_confidence(text, tokens, language_info)
        
        return ProcessingResult(
            tokens=tokens,
            cleaned_text=cleaned_text,
            sentiment_indicators=sentiment_indicators,
            cultural_markers=cultural_markers,
            language_specific_features=features,
            confidence_factors=confidence_factors
        )
    
    def get_sentiment_lexicon(self) -> Dict[str, List[str]]:
        """Korean sentiment lexicon"""
        return {
            'positive': [
                '좋다', '사랑', '최고', '대박', '예쁘다', '멋있다', '완벽',
                '훌륭하다', '놀랍다', '감동', '행복', '기쁘다', '즐겁다'
            ],
            'negative': [
                '싫다', '나쁘다', '최악', '별로', '실망', '화나다', '짜증',
                '슬프다', '우울하다', '답답하다'
            ],
            'enthusiasm': [
                '와', '우와', '헐', '진짜', '레전드', '미쳤다', '개좋아',
                '존좋', '갓', '킹', '퀸'
            ],
            'honorifics': [
                '님', '씨', '선생님', '오빠', '언니', '형', '누나'
            ]
        }
    
    def get_kpop_terms(self) -> List[str]:
        """Korean K-Pop terms"""
        return [
            '아이돌', '가수', '댄스', '노래', '음악', '콘서트', '팬',
            '컴백', '데뷔', '뮤비', '안무', '보컬', '랩퍼'
        ]
    
    def simple_korean_tokenize(self, text: str) -> List[str]:
        """Simple Korean tokenization fallback"""
        # Basic space-based tokenization for Korean
        return text.split()
    
    def clean_korean_text(self, text: str) -> str:
        """Clean Korean text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def analyze_korean_sentiment(self, tokens: List[str]) -> Dict[str, float]:
        """Analyze Korean sentiment indicators"""
        indicators = {}
        
        for category, words in self.sentiment_lexicon.items():
            count = 0
            for token in tokens:
                for word in words:
                    if word in token:  # Partial matching for Korean
                        count += 1
                        break
            indicators[category] = count / len(tokens) if tokens else 0
        
        return indicators
    
    def detect_korean_cultural_markers(self, text: str) -> List[str]:
        """Detect Korean cultural markers"""
        markers = []
        
        for term in self.kpop_terms:
            if term in text:
                markers.append(term)
        
        # Detect honorifics usage
        for honorific in self.sentiment_lexicon['honorifics']:
            if honorific in text:
                markers.append(f"honorific_{honorific}")
        
        return markers
    
    def extract_korean_features(self, text: str, tokens: List[str]) -> Dict[str, any]:
        """Extract Korean-specific features"""
        return {
            'honorific_usage': sum(1 for h in self.sentiment_lexicon['honorifics'] if h in text),
            'exclamation_count': text.count('!'),
            'korean_exclamations': text.count('ㅋ') + text.count('ㅎ'),
            'emoticons': len(re.findall(r'[ㅠㅜㅡㅗㅓㅏ]{2,}', text)),
            'token_count': len(tokens)
        }
    
    def calculate_korean_confidence(self, text: str, tokens: List[str], language_info: LanguageDetectionResult) -> Dict[str, float]:
        """Calculate confidence factors for Korean processing"""
        factors = {}
        
        factors['language_detection'] = language_info.confidence
        factors['konlpy_available'] = 1.0 if self.konlpy_available else 0.5
        
        # Korean character ratio
        korean_chars = len(re.findall(r'[가-힣]', text))
        factors['korean_character_ratio'] = korean_chars / len(text) if text else 0
        
        # Vocabulary coverage
        known_terms = len(self.detect_korean_cultural_markers(text))
        factors['vocabulary_coverage'] = min(known_terms / 3, 1.0)
        
        return factors

class SpanishProcessor(LanguageProcessor):
    """Spanish language processor"""
    
    def __init__(self):
        self.sentiment_lexicon = self.get_sentiment_lexicon()
        self.kpop_terms = self.get_kpop_terms()
    
    def process(self, text: str, language_info: LanguageDetectionResult) -> ProcessingResult:
        """Process Spanish text"""
        tokens = self.tokenize_spanish(text)
        cleaned_text = self.clean_spanish_text(text)
        sentiment_indicators = self.analyze_spanish_sentiment(tokens)
        cultural_markers = self.detect_spanish_cultural_markers(text)
        features = self.extract_spanish_features(text, tokens)
        confidence_factors = self.calculate_spanish_confidence(text, tokens, language_info)
        
        return ProcessingResult(
            tokens=tokens,
            cleaned_text=cleaned_text,
            sentiment_indicators=sentiment_indicators,
            cultural_markers=cultural_markers,
            language_specific_features=features,
            confidence_factors=confidence_factors
        )
    
    def get_sentiment_lexicon(self) -> Dict[str, List[str]]:
        """Spanish sentiment lexicon"""
        return {
            'positive': [
                'amor', 'increíble', 'perfecto', 'hermoso', 'talentoso', 'genial',
                'fantástico', 'maravilloso', 'excelente', 'divino', 'precioso'
            ],
            'negative': [
                'odio', 'terrible', 'horrible', 'malo', 'feo', 'aburrido',
                'decepcionante', 'basura', 'fracaso'
            ],
            'enthusiasm': [
                'dios', 'madre', 'increíble', 'brutal', 'bestial', 'épico',
                'literalmente', 'totalmente'
            ],
            'sarcasm': [
                'claro', 'obvio', 'seguro', 'imagínate', 'por favor'
            ]
        }
    
    def get_kpop_terms(self) -> List[str]:
        """Spanish K-Pop terms"""
        return [
            'idol', 'comeback', 'debut', 'bias', 'stan', 'fandom',
            'coreografía', 'vocal', 'rapero', 'visual'
        ]
    
    def tokenize_spanish(self, text: str) -> List[str]:
        """Tokenize Spanish text"""
        clean_text = re.sub(r'http\S+|www\S+|@\w+|#\w+', '', text)
        tokens = re.findall(r'\b\w+\b', clean_text.lower())
        return tokens
    
    def clean_spanish_text(self, text: str) -> str:
        """Clean Spanish text"""
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def analyze_spanish_sentiment(self, tokens: List[str]) -> Dict[str, float]:
        """Analyze Spanish sentiment indicators"""
        indicators = {}
        
        for category, words in self.sentiment_lexicon.items():
            count = sum(1 for token in tokens if token in words)
            indicators[category] = count / len(tokens) if tokens else 0
        
        return indicators
    
    def detect_spanish_cultural_markers(self, text: str) -> List[str]:
        """Detect Spanish cultural markers"""
        markers = []
        text_lower = text.lower()
        
        for term in self.kpop_terms:
            if term in text_lower:
                markers.append(term)
        
        return markers
    
    def extract_spanish_features(self, text: str, tokens: List[str]) -> Dict[str, any]:
        """Extract Spanish-specific features"""
        return {
            'exclamation_count': text.count('!') + text.count('¡'),
            'question_count': text.count('?') + text.count('¿'),
            'accent_marks': len(re.findall(r'[áéíóúñü]', text.lower())),
            'avg_word_length': sum(len(token) for token in tokens) / len(tokens) if tokens else 0
        }
    
    def calculate_spanish_confidence(self, text: str, tokens: List[str], language_info: LanguageDetectionResult) -> Dict[str, float]:
        """Calculate confidence factors for Spanish processing"""
        factors = {}
        
        factors['language_detection'] = language_info.confidence
        
        # Spanish character indicators
        spanish_chars = len(re.findall(r'[áéíóúñü¿¡]', text.lower()))
        factors['spanish_indicators'] = min(spanish_chars / 10, 1.0)
        
        # Vocabulary coverage
        known_words = sum(1 for token in tokens if self.is_spanish_word(token))
        factors['vocabulary_coverage'] = known_words / len(tokens) if tokens else 0
        
        return factors
    
    def is_spanish_word(self, word: str) -> bool:
        """Check if word is in Spanish vocabulary"""
        all_words = []
        for word_list in self.sentiment_lexicon.values():
            all_words.extend(word_list)
        all_words.extend(self.kpop_terms)
        
        return word in all_words

class MultiLanguageProcessor:
    """Main multi-language processor"""
    
    def __init__(self):
        self.supported_languages = {
            'en': EnglishProcessor(),
            'ko': KoreanProcessor(),
            'es': SpanishProcessor(),
            # Add more processors as implemented
        }
        
        self.language_names = {
            'en': 'English',
            'ko': 'Korean',
            'es': 'Spanish',
            'ja': 'Japanese',
            'pt': 'Portuguese',
            'fr': 'French',
            'de': 'German',
            'zh': 'Chinese',
            'th': 'Thai'
        }
    
    def detect_language(self, text: str) -> LanguageDetectionResult:
        """Detect language of input text"""
        detections = {}
        
        # Try langdetect
        if LANGDETECT_AVAILABLE:
            try:
                lang_probs = detect_langs(text)
                best_detection = lang_probs[0]
                detections['langdetect'] = {
                    'language': best_detection.lang,
                    'confidence': best_detection.prob
                }
            except Exception as e:
                detections['langdetect'] = {
                    'language': 'unknown',
                    'confidence': 0.0,
                    'error': str(e)
                }
        
        # Simple heuristic detection
        detections['heuristic'] = self.heuristic_language_detection(text)
        
        # Determine final language
        final_language = self.get_consensus_language(detections)
        confidence = self.calculate_detection_confidence(detections, final_language)
        
        return LanguageDetectionResult(
            detected_language=final_language,
            confidence=confidence,
            supported=final_language in self.supported_languages,
            detection_methods=detections
        )
    
    def heuristic_language_detection(self, text: str) -> Dict[str, any]:
        """Simple heuristic language detection"""
        scores = {}
        
        # Korean detection
        korean_chars = len(re.findall(r'[가-힣]', text))
        scores['ko'] = korean_chars / len(text) if text else 0
        
        # English detection (basic)
        english_words = len(re.findall(r'\b[a-zA-Z]+\b', text))
        scores['en'] = english_words / len(text.split()) if text.split() else 0
        
        # Spanish detection (accent marks)
        spanish_chars = len(re.findall(r'[áéíóúñü¿¡]', text.lower()))
        scores['es'] = spanish_chars / len(text) if text else 0
        
        # Get best guess
        best_lang = max(scores, key=scores.get) if scores else 'en'
        best_score = scores.get(best_lang, 0)
        
        return {
            'language': best_lang,
            'confidence': best_score,
            'all_scores': scores
        }
    
    def get_consensus_language(self, detections: Dict[str, Dict]) -> str:
        """Get consensus language from multiple detection methods"""
        language_votes = {}
        
        for method, result in detections.items():
            if 'error' not in result:
                lang = result['language']
                confidence = result['confidence']
                
                if lang not in language_votes:
                    language_votes[lang] = 0
                language_votes[lang] += confidence
        
        if language_votes:
            return max(language_votes, key=language_votes.get)
        else:
            return 'en'  # Default to English
    
    def calculate_detection_confidence(self, detections: Dict[str, Dict], final_language: str) -> float:
        """Calculate overall detection confidence"""
        confidences = []
        
        for method, result in detections.items():
            if 'error' not in result and result['language'] == final_language:
                confidences.append(result['confidence'])
        
        if confidences:
            return sum(confidences) / len(confidences)
        else:
            return 0.5  # Medium confidence for fallback
    
    def process_text(self, text: str) -> Tuple[LanguageDetectionResult, ProcessingResult]:
        """Process text with language detection"""
        # Detect language
        language_info = self.detect_language(text)
        
        # Process with appropriate processor
        if language_info.supported:
            processor = self.supported_languages[language_info.detected_language]
            result = processor.process(text, language_info)
        else:
            # Fallback to English processor
            processor = self.supported_languages['en']
            result = processor.process(text, language_info)
            language_info.fallback_used = True
        
        return language_info, result
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return {
            code: self.language_names.get(code, code.upper()) 
            for code in self.supported_languages.keys()
        }

# Example usage
if __name__ == "__main__":
    processor = MultiLanguageProcessor()
    
    # Test texts in different languages
    test_texts = [
        "OMG BTS absolutely slayed this performance! 🔥",
        "방탄소년단 정말 대박이야! 사랑해 💜",
        "¡Dios mío, esta canción es increíble! Los amo tanto 💕"
    ]
    
    for text in test_texts:
        print(f"\nAnalyzing: {text}")
        language_info, processing_result = processor.process_text(text)
        
        print(f"Detected Language: {language_info.detected_language} (confidence: {language_info.confidence:.2%})")
        print(f"Supported: {language_info.supported}")
        print(f"Tokens: {processing_result.tokens[:5]}...")  # First 5 tokens
        print(f"Cultural Markers: {processing_result.cultural_markers}")
        print(f"Sentiment Indicators: {processing_result.sentiment_indicators}")