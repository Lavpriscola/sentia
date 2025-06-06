# K-Pop Sentiment Analyzer

A comprehensive text sentiment analysis tool specifically designed for K-Pop discourse with advanced preprocessing, machine learning capabilities, and a web-based GUI for data management and fine-tuning.

## Features

### 🎯 **10 K-Pop Specific Sentiment Labels**
1. **ENTHUSIASTIC_SUPPORT** - Highly positive, energetic support for idols/groups
2. **NOSTALGIC_APPRECIATION** - Warm, reflective sentiment about past eras or memories
3. **ANTICIPATORY_EXCITEMENT** - Forward-looking excitement about comebacks, releases, events
4. **PROTECTIVE_DEFENSIVE** - Defensive stance protecting idols from criticism or hate
5. **CRITICAL_DISAPPOINTMENT** - Constructive criticism or disappointment from fans
6. **NEUTRAL_FACTUAL** - Objective, informational content without emotional bias
7. **COMPETITIVE_RIVALRY** - Inter-fandom competition and comparison rhetoric
8. **SARCASTIC_MOCKERY** - Sarcastic or mocking tone, often passive-aggressive
9. **MALICIOUS_COORDINATED** - Coordinated attacks, smear campaigns, or malicious content
10. **MIXED_CONFLICTED** - Complex emotions showing internal conflict or mixed feelings

### 🔧 **Advanced Text Preprocessing**
- URL removal
- @mention handling
- Hashtag processing (keep text, remove #)
- Emoji handling (preserve or remove)
- Whitespace normalization
- Special character cleaning
- Metadata extraction

### 🤖 **Intelligent Classification**
- Keyword-based pattern matching
- Linguistic pattern detection (enthusiasm, sarcasm, competitiveness)
- Risk level assessment (low, medium, high, very high)
- Confidence scoring
- Rule-based classification with machine learning readiness

### 🌐 **Web Application Features**
- **Dashboard**: Overview of analysis statistics and recent activity
- **Text Analysis**: Real-time sentiment analysis with detailed results
- **Data Management**: Review, correct, edit, and delete analysis records
- **Statistics**: Comprehensive analytics with interactive charts
- **Label Guide**: Complete reference for all sentiment categories
- **Data Export**: JSON export for external processing

### 📊 **Machine Learning Integration**
- SQLite database for storing training data
- User correction tracking for model improvement
- Confidence scoring for quality assessment
- Risk level categorization for content moderation
- Export capabilities for external ML training

## Installation

1. **Clone or download the project**
```bash
git clone <repository-url>
cd kpop_sentiment_analyzer
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python app.py
```

4. **Access the web interface**
Open your browser and navigate to `http://localhost:12000`

## Usage

### Web Interface

1. **Analyze Text**: Enter K-Pop related text to get instant sentiment analysis
2. **Review Results**: View detailed analysis including confidence scores and reasoning
3. **Manage Data**: Correct predictions, delete records, and build training datasets
4. **View Statistics**: Monitor analysis trends and model performance
5. **Export Data**: Download analysis data for external processing

### API Usage

```python
from sentiment_analyzer import KPopSentimentAnalyzer

# Initialize analyzer
analyzer = KPopSentimentAnalyzer()

# Analyze text
result = analyzer.analyze_sentiment("OMG they absolutely SLAYED this performance! 🔥")

print(f"Label: {result.label_name}")
print(f"Confidence: {result.confidence}")
print(f"Risk Level: {result.risk_level}")
```

### Programmatic Usage

```python
from text_preprocessor import TextPreprocessor

# Initialize preprocessor
preprocessor = TextPreprocessor()

# Clean text
clean_text = preprocessor.preprocess_text(
    "OMG @BTS_official just dropped the most AMAZING teaser!!! 🔥🔥🔥 https://youtube.com/watch?v=example #BTS #ARMY"
)

# Extract metadata
metadata = preprocessor.extract_metadata(text)
```

## File Structure

```
kpop_sentiment_analyzer/
├── app.py                    # Flask web application
├── sentiment_analyzer.py     # Main sentiment analysis engine
├── sentiment_labels.py       # K-Pop specific sentiment label definitions
├── text_preprocessor.py      # Text cleaning and preprocessing
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── templates/               # HTML templates
│   ├── base.html           # Base template with navigation
│   ├── index.html          # Dashboard page
│   ├── analyze.html        # Text analysis page
│   ├── data_management.html # Data management interface
│   ├── statistics.html     # Analytics and charts
│   ├── labels.html         # Sentiment labels reference
│   └── error.html          # Error pages
└── sentiment_data.db        # SQLite database (created automatically)
```

## Sentiment Labels in Detail

### Risk Levels
- **Low Risk**: Positive, constructive, or neutral content
- **Medium Risk**: Emotional content that may need monitoring
- **High Risk**: Potentially harmful or inflammatory content
- **Very High Risk**: Malicious, coordinated, or dangerous content

### Classification Guidelines
1. Consider overall tone and intent
2. Look for emotional indicators and context clues
3. Pay attention to sarcasm and implicit meanings
4. Consider potential impact on the K-Pop community
5. When in doubt, choose the most conservative classification

## Machine Learning Integration

The tool is designed to support machine learning workflows:

1. **Data Collection**: Automatically stores all analyses in SQLite database
2. **Human Feedback**: Web interface allows manual correction of predictions
3. **Quality Tracking**: Confidence scores and verification status
4. **Export Capabilities**: JSON export for training external models
5. **Performance Monitoring**: Statistics track correction rates and accuracy

## API Endpoints

- `POST /api/analyze` - Analyze text sentiment
- `GET /export` - Export all data as JSON
- `POST /update_label/<id>` - Update sentiment label
- `POST /delete_analysis/<id>` - Delete analysis record

## Database Schema

```sql
CREATE TABLE sentiment_analysis (
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
);
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Future Enhancements

- [ ] Advanced machine learning models (BERT, RoBERTa)
- [ ] Real-time social media integration
- [ ] Batch processing capabilities
- [ ] Advanced analytics and reporting
- [ ] Multi-language support
- [ ] API rate limiting and authentication
- [ ] Docker containerization
- [ ] Cloud deployment options

## License

This project is open source and available under the MIT License.

## Support

For questions, issues, or contributions, please open an issue on the project repository.

---

Built with ❤️ for the K-Pop community