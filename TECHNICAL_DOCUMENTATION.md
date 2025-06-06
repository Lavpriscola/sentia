# K-Pop Sentiment Analyzer - Technical Documentation

## 📋 Table of Contents
1. [System Architecture](#system-architecture)
2. [Analysis Engine Deep Dive](#analysis-engine-deep-dive)
3. [Customization Guide](#customization-guide)
4. [API Reference](#api-reference)
5. [Database Schema](#database-schema)
6. [Performance Optimization](#performance-optimization)
7. [Troubleshooting](#troubleshooting)

---

## 🏗️ System Architecture

### Overview
The K-Pop Sentiment Analyzer is built using a modular architecture that separates concerns and allows for easy customization and scaling.

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Interface (Flask)                    │
├─────────────────────────────────────────────────────────────┤
│                    Analysis Engine                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Text Processor  │  │ Sentiment       │  │ Risk        │ │
│  │                 │  │ Classifier      │  │ Assessor    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    Data Layer                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ SQLite Database │  │ Sentiment       │  │ Analysis    │ │
│  │                 │  │ Labels          │  │ Cache       │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. Text Preprocessor (`text_preprocessor.py`)
**Purpose:** Clean and normalize input text for analysis

**Key Functions:**
- URL removal and extraction
- @mention handling
- Hashtag processing
- Emoji detection
- Whitespace normalization

**Customization Points:**
```python
class TextPreprocessor:
    def __init__(self, preserve_emojis=True, extract_urls=True):
        self.preserve_emojis = preserve_emojis
        self.extract_urls = extract_urls
        # Add custom settings here
```

#### 2. Sentiment Labels (`sentiment_labels.py`)
**Purpose:** Define the 10 K-Pop specific sentiment categories

**Structure:**
```python
SENTIMENT_LABELS = {
    label_id: {
        'name': 'LABEL_NAME',
        'description': 'Human-readable description',
        'risk_level': 'Low|Medium|High|Very High',
        'keywords': ['list', 'of', 'keywords'],
        'patterns': ['regex', 'patterns'],
        'examples': ['example texts']
    }
}
```

#### 3. Sentiment Analyzer (`sentiment_analyzer.py`)
**Purpose:** Main analysis engine that classifies text

**Analysis Pipeline:**
1. Text preprocessing
2. Feature extraction
3. Pattern matching
4. Confidence calculation
5. Risk assessment
6. Result compilation

---

## 🔍 Analysis Engine Deep Dive

### How Classification Works

#### Step 1: Text Preprocessing
```python
def preprocess_text(self, text):
    """
    Clean and normalize input text
    
    Process:
    1. Extract metadata (URLs, mentions, hashtags)
    2. Normalize whitespace
    3. Handle emojis
    4. Remove noise
    """
    # Implementation details...
```

#### Step 2: Feature Extraction
The system extracts multiple types of features:

**Lexical Features:**
- Keyword presence and frequency
- Capitalization patterns
- Punctuation usage
- Text length

**Syntactic Features:**
- Exclamation marks (enthusiasm indicator)
- Question marks (uncertainty/curiosity)
- Quotation marks (sarcasm indicator)
- ALL CAPS usage (emphasis/anger)

**Semantic Features:**
- Positive/negative word ratios
- Emotional intensity markers
- Comparative language
- Temporal references

#### Step 3: Classification Logic

Each sentiment label has its own classification method:

```python
def classify_enthusiastic_support(self, text, preprocessed_text):
    """
    Detect enthusiastic support sentiment
    
    Indicators:
    - Positive keywords (love, amazing, perfect)
    - Enthusiasm markers (!!!, ALL CAPS)
    - Superlative language (best, greatest)
    - Fire/heart emojis
    """
    confidence = 0.0
    text_lower = preprocessed_text.lower()
    
    # Keyword matching (40% weight)
    keywords = ['love', 'amazing', 'perfect', 'incredible', 'best']
    keyword_score = sum(1 for kw in keywords if kw in text_lower)
    confidence += (keyword_score / len(keywords)) * 0.4
    
    # Pattern matching (30% weight)
    if re.search(r'[!]{2,}', text):  # Multiple exclamations
        confidence += 0.15
    if re.search(r'\b[A-Z]{3,}\b', text):  # ALL CAPS words
        confidence += 0.15
    
    # Emoji detection (20% weight)
    fire_emojis = len(re.findall(r'🔥|❤️|💖', text))
    confidence += min(fire_emojis * 0.1, 0.2)
    
    # Context analysis (10% weight)
    if any(word in text_lower for word in ['performance', 'song', 'album']):
        confidence += 0.1
    
    return min(confidence, 1.0)
```

#### Step 4: Confidence Calculation

The system uses a weighted approach to calculate confidence:

```python
def calculate_confidence(self, scores):
    """
    Calculate overall confidence based on multiple factors
    
    Factors:
    - Primary indicator strength (50%)
    - Secondary indicator presence (30%)
    - Text quality and length (20%)
    """
    primary_score = max(scores.values())
    secondary_indicators = len([s for s in scores.values() if s > 0.3])
    text_quality = self.assess_text_quality(text)
    
    confidence = (
        primary_score * 0.5 +
        min(secondary_indicators / 3, 1.0) * 0.3 +
        text_quality * 0.2
    )
    
    return confidence
```

#### Step 5: Risk Assessment

Risk levels are determined by sentiment type and confidence:

```python
def assess_risk_level(self, sentiment_label, confidence, text_features):
    """
    Assess risk level based on sentiment and context
    
    Risk Factors:
    - Base risk level of sentiment
    - Confidence score
    - Aggressive language
    - Coordinated attack patterns
    """
    base_risk = SENTIMENT_LABELS[sentiment_label]['risk_level']
    
    # Escalate risk based on confidence and features
    if confidence > 0.8 and text_features.get('aggressive_language'):
        return escalate_risk(base_risk)
    
    return base_risk
```

---

## ⚙️ Customization Guide

### Adding New Sentiment Labels

#### 1. Define the Label
Add to `sentiment_labels.py`:

```python
SENTIMENT_LABELS[11] = {
    'name': 'CUSTOM_SENTIMENT',
    'description': 'Description of when this sentiment applies',
    'risk_level': 'Medium',
    'keywords': ['custom', 'keywords', 'here'],
    'patterns': [r'regex.*patterns?', r'another.*pattern'],
    'examples': [
        'Example text that matches this sentiment',
        'Another example showing this emotion'
    ]
}
```

#### 2. Implement Classification Logic
Add to `sentiment_analyzer.py`:

```python
def classify_custom_sentiment(self, text, preprocessed_text):
    """
    Detect custom sentiment
    
    Args:
        text (str): Original text
        preprocessed_text (str): Cleaned text
        
    Returns:
        float: Confidence score (0-1)
    """
    confidence = 0.0
    text_lower = preprocessed_text.lower()
    
    # Implement your detection logic here
    # Example: keyword matching
    keywords = SENTIMENT_LABELS[11]['keywords']
    matches = sum(1 for kw in keywords if kw in text_lower)
    confidence += (matches / len(keywords)) * 0.6
    
    # Example: pattern matching
    patterns = SENTIMENT_LABELS[11]['patterns']
    for pattern in patterns:
        if re.search(pattern, text_lower):
            confidence += 0.2
            break
    
    # Example: contextual analysis
    if self.detect_specific_context(text):
        confidence += 0.2
    
    return min(confidence, 1.0)
```

#### 3. Register the Classifier
Add to the `analyze_sentiment` method:

```python
def analyze_sentiment(self, text):
    # ... existing code ...
    
    # Add your custom classifier
    scores[11] = self.classify_custom_sentiment(text, preprocessed_text)
    
    # ... rest of method ...
```

### Modifying Existing Labels

#### Adjusting Keywords
```python
# Add keywords
SENTIMENT_LABELS[1]['keywords'].extend(['new', 'keywords'])

# Replace keywords entirely
SENTIMENT_LABELS[1]['keywords'] = ['completely', 'new', 'list']

# Remove specific keywords
SENTIMENT_LABELS[1]['keywords'] = [
    kw for kw in SENTIMENT_LABELS[1]['keywords'] 
    if kw not in ['unwanted', 'keywords']
]
```

#### Changing Risk Levels
```python
# Make a label more conservative
SENTIMENT_LABELS[7]['risk_level'] = 'Very High'  # Was High

# Make a label less strict
SENTIMENT_LABELS[4]['risk_level'] = 'Low'  # Was Medium
```

#### Adding Pattern Detection
```python
# Add regex patterns for better detection
SENTIMENT_LABELS[8]['patterns'].extend([
    r'sure.*\b(jan|honey|sweetie)\b',  # Sarcastic patterns
    r'imagine.*thinking',               # Dismissive patterns
    r'not.*you.*saying'                # Confrontational patterns
])
```

### Customizing Analysis Parameters

#### Confidence Thresholds
```python
class SentimentAnalyzer:
    def __init__(self, confidence_threshold=0.5):
        self.confidence_threshold = confidence_threshold
        # Lower = more sensitive, Higher = more conservative
```

#### Text Length Handling
```python
def analyze_sentiment(self, text):
    # Skip very short texts
    if len(text.split()) < 3:
        return self.get_neutral_result(text, "Text too short")
    
    # Handle very long texts
    if len(text.split()) > 500:
        text = self.truncate_text(text, max_words=500)
```

#### Language-Specific Customization
```python
def detect_language(self, text):
    """Detect text language and adjust analysis"""
    if self.contains_korean(text):
        return self.analyze_korean_sentiment(text)
    elif self.contains_japanese(text):
        return self.analyze_japanese_sentiment(text)
    else:
        return self.analyze_english_sentiment(text)
```

### Performance Tuning

#### Caching Results
```python
from functools import lru_cache

class SentimentAnalyzer:
    @lru_cache(maxsize=1000)
    def analyze_sentiment_cached(self, text_hash):
        """Cache analysis results for identical texts"""
        return self.analyze_sentiment(text)
```

#### Batch Processing
```python
def analyze_batch(self, texts, batch_size=100):
    """Process multiple texts efficiently"""
    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        batch_results = [self.analyze_sentiment(text) for text in batch]
        results.extend(batch_results)
    return results
```

---

## 🔌 API Reference

### Core Analysis Methods

#### `analyze_sentiment(text)`
**Purpose:** Main analysis method

**Parameters:**
- `text` (str): Input text to analyze

**Returns:**
```python
{
    'text': str,                    # Original text
    'predicted_label': int,         # Label ID (1-10)
    'label_name': str,             # Human-readable label name
    'confidence': float,           # Confidence score (0-1)
    'risk_level': str,             # Low/Medium/High/Very High
    'reasoning': str,              # Explanation of classification
    'metadata': dict,              # Additional analysis data
    'preprocessing_info': dict     # Text preprocessing details
}
```

#### `preprocess_text(text)`
**Purpose:** Clean and normalize text

**Parameters:**
- `text` (str): Raw input text

**Returns:**
```python
{
    'cleaned_text': str,           # Processed text
    'extracted_urls': list,        # Found URLs
    'extracted_mentions': list,    # Found @mentions
    'extracted_hashtags': list,    # Found #hashtags
    'emoji_count': int,           # Number of emojis
    'original_length': int,       # Original text length
    'cleaned_length': int         # Processed text length
}
```

### Web API Endpoints

#### `POST /api/analyze`
**Purpose:** Analyze text via REST API

**Request Body:**
```json
{
    "text": "Text to analyze",
    "options": {
        "include_preprocessing": true,
        "include_metadata": true
    }
}
```

**Response:**
```json
{
    "success": true,
    "result": {
        "text": "Text to analyze",
        "predicted_label": 1,
        "label_name": "ENTHUSIASTIC_SUPPORT",
        "confidence": 0.85,
        "risk_level": "Low",
        "reasoning": "High enthusiasm indicators detected",
        "timestamp": "2024-01-01T12:00:00Z"
    }
}
```

#### `GET /api/labels`
**Purpose:** Get all sentiment labels

**Response:**
```json
{
    "labels": {
        "1": {
            "name": "ENTHUSIASTIC_SUPPORT",
            "description": "Highly positive, energetic support",
            "risk_level": "Low",
            "keywords": ["love", "amazing", "perfect"],
            "examples": ["OMG they absolutely SLAYED!"]
        }
    }
}
```

---

## 🗄️ Database Schema

### Main Tables

#### `sentiment_analysis`
```sql
CREATE TABLE sentiment_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,                    -- Original text
    predicted_label INTEGER NOT NULL,      -- Predicted label ID
    confidence REAL NOT NULL,              -- Confidence score
    label_name TEXT NOT NULL,              -- Label name
    risk_level TEXT NOT NULL,              -- Risk assessment
    reasoning TEXT,                        -- Classification reasoning
    metadata TEXT,                         -- JSON metadata
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_corrected_label INTEGER,          -- Manual correction
    is_verified BOOLEAN DEFAULT FALSE      -- Quality verification
);
```

#### `analysis_metadata`
```sql
CREATE TABLE analysis_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER,                   -- Foreign key
    preprocessing_info TEXT,               -- JSON preprocessing data
    feature_scores TEXT,                   -- JSON feature analysis
    alternative_labels TEXT,               -- JSON other possible labels
    processing_time REAL,                  -- Analysis duration
    FOREIGN KEY (analysis_id) REFERENCES sentiment_analysis (id)
);
```

### Indexes for Performance
```sql
CREATE INDEX idx_sentiment_label ON sentiment_analysis(predicted_label);
CREATE INDEX idx_sentiment_timestamp ON sentiment_analysis(timestamp);
CREATE INDEX idx_sentiment_confidence ON sentiment_analysis(confidence);
CREATE INDEX idx_sentiment_risk ON sentiment_analysis(risk_level);
```

---

## 🚀 Performance Optimization

### Analysis Speed Optimization

#### 1. Text Preprocessing Optimization
```python
class OptimizedTextPreprocessor:
    def __init__(self):
        # Compile regex patterns once
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.mention_pattern = re.compile(r'@\w+')
        self.hashtag_pattern = re.compile(r'#\w+')
    
    def preprocess(self, text):
        # Use compiled patterns for faster processing
        text = self.url_pattern.sub('', text)
        text = self.mention_pattern.sub('', text)
        return text
```

#### 2. Caching Strategy
```python
import redis
import json

class CachedSentimentAnalyzer:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.cache_ttl = 3600  # 1 hour
    
    def analyze_sentiment(self, text):
        # Check cache first
        cache_key = f"sentiment:{hash(text)}"
        cached_result = self.redis_client.get(cache_key)
        
        if cached_result:
            return json.loads(cached_result)
        
        # Perform analysis
        result = self._analyze_sentiment_uncached(text)
        
        # Cache result
        self.redis_client.setex(
            cache_key, 
            self.cache_ttl, 
            json.dumps(result)
        )
        
        return result
```

#### 3. Batch Processing
```python
def analyze_batch_optimized(self, texts):
    """Optimized batch processing"""
    # Group similar texts
    text_groups = self.group_similar_texts(texts)
    
    results = []
    for group in text_groups:
        # Process similar texts together
        group_results = self.process_text_group(group)
        results.extend(group_results)
    
    return results
```

### Memory Optimization

#### 1. Lazy Loading
```python
class LazyLoadedAnalyzer:
    def __init__(self):
        self._sentiment_labels = None
        self._preprocessor = None
    
    @property
    def sentiment_labels(self):
        if self._sentiment_labels is None:
            self._sentiment_labels = self.load_sentiment_labels()
        return self._sentiment_labels
```

#### 2. Memory-Efficient Data Structures
```python
# Use slots for memory efficiency
class AnalysisResult:
    __slots__ = ['text', 'label', 'confidence', 'risk_level']
    
    def __init__(self, text, label, confidence, risk_level):
        self.text = text
        self.label = label
        self.confidence = confidence
        self.risk_level = risk_level
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Issue: Low Accuracy for Specific Content
**Symptoms:** System consistently misclassifies certain types of content

**Diagnosis:**
1. Check if relevant keywords are missing
2. Verify pattern matching logic
3. Examine confidence thresholds

**Solutions:**
```python
# Add missing keywords
SENTIMENT_LABELS[label_id]['keywords'].extend(['missing', 'terms'])

# Adjust confidence thresholds
def classify_with_adjusted_threshold(self, text, preprocessed_text):
    confidence = self.base_classification(text, preprocessed_text)
    # Lower threshold for this specific case
    return max(confidence - 0.1, 0.0)

# Add specific pattern detection
def detect_specific_pattern(self, text):
    # Custom logic for problematic content
    if 'specific_indicator' in text.lower():
        return 0.8
    return 0.0
```

#### Issue: High False Positive Rate
**Symptoms:** System flags too much content as risky

**Diagnosis:**
1. Check if keywords are too broad
2. Verify risk level assignments
3. Examine confidence calculation

**Solutions:**
```python
# Make keywords more specific
old_keywords = ['bad', 'terrible']  # Too broad
new_keywords = ['absolutely terrible', 'completely bad']  # More specific

# Adjust risk levels
SENTIMENT_LABELS[label_id]['risk_level'] = 'Medium'  # Was High

# Increase confidence requirements
def classify_with_higher_threshold(self, text, preprocessed_text):
    confidence = self.base_classification(text, preprocessed_text)
    # Require higher confidence for risky classifications
    if SENTIMENT_LABELS[self.predicted_label]['risk_level'] in ['High', 'Very High']:
        return confidence * 0.8  # Reduce confidence
    return confidence
```

#### Issue: Slow Performance
**Symptoms:** Analysis takes too long for large volumes

**Diagnosis:**
1. Profile the analysis pipeline
2. Check database query performance
3. Examine memory usage

**Solutions:**
```python
# Add performance monitoring
import time
import cProfile

def analyze_with_profiling(self, text):
    start_time = time.time()
    
    result = self.analyze_sentiment(text)
    
    processing_time = time.time() - start_time
    if processing_time > 1.0:  # Log slow analyses
        self.log_slow_analysis(text, processing_time)
    
    return result

# Optimize database queries
def get_analyses_optimized(self, limit=100):
    # Use proper indexing and limit results
    query = """
    SELECT * FROM sentiment_analysis 
    WHERE timestamp > ? 
    ORDER BY timestamp DESC 
    LIMIT ?
    """
    return self.execute_query(query, [recent_date, limit])

# Implement connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'sqlite:///sentiment_data.db',
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

### Debugging Tools

#### 1. Analysis Debugging
```python
def debug_analysis(self, text):
    """Detailed analysis debugging"""
    print(f"Analyzing: {text}")
    
    # Step-by-step analysis
    preprocessed = self.preprocess_text(text)
    print(f"Preprocessed: {preprocessed['cleaned_text']}")
    
    # Show all label scores
    scores = {}
    for label_id in SENTIMENT_LABELS.keys():
        score = self.classify_label(label_id, text, preprocessed['cleaned_text'])
        scores[label_id] = score
        if score > 0:
            print(f"Label {label_id}: {score:.3f}")
    
    # Show final decision
    best_label = max(scores, key=scores.get)
    print(f"Final decision: {best_label} ({scores[best_label]:.3f})")
    
    return scores
```

#### 2. Performance Profiling
```python
def profile_analysis():
    """Profile analysis performance"""
    import cProfile
    import pstats
    
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run analysis
    analyzer = SentimentAnalyzer()
    test_texts = load_test_texts()
    for text in test_texts:
        analyzer.analyze_sentiment(text)
    
    profiler.disable()
    
    # Show results
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions
```

#### 3. Data Quality Monitoring
```python
def monitor_data_quality():
    """Monitor analysis quality metrics"""
    analyzer = SentimentAnalyzer()
    
    # Get recent analyses
    recent_analyses = analyzer.get_recent_analyses(days=7)
    
    # Calculate metrics
    avg_confidence = sum(a['confidence'] for a in recent_analyses) / len(recent_analyses)
    low_confidence_count = sum(1 for a in recent_analyses if a['confidence'] < 0.5)
    correction_rate = sum(1 for a in recent_analyses if a['user_corrected_label']) / len(recent_analyses)
    
    print(f"Average Confidence: {avg_confidence:.3f}")
    print(f"Low Confidence Analyses: {low_confidence_count}")
    print(f"User Correction Rate: {correction_rate:.3f}")
    
    # Alert if quality is degrading
    if avg_confidence < 0.6 or correction_rate > 0.2:
        print("⚠️ Data quality alert: Consider reviewing and updating labels")
```

This technical documentation provides comprehensive guidance for understanding, customizing, and optimizing the K-Pop Sentiment Analyzer system. Use it as a reference for both development and troubleshooting activities.