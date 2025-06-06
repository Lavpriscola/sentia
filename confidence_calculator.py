"""
Real Confidence Calculator Implementation
Provides sophisticated confidence scoring using statistical methods and validation
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import sqlite3
from datetime import datetime, timedelta
from collections import Counter
import re
from scipy import stats
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import math

@dataclass
class ConfidenceComponents:
    """Individual components that contribute to confidence score"""
    base_confidence: float
    keyword_strength: float
    pattern_clarity: float
    historical_accuracy: float
    text_quality: float
    context_consistency: float
    uncertainty_penalty: float
    final_confidence: float

@dataclass
class ValidationMetrics:
    """Validation metrics for confidence calibration"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    calibration_error: float
    reliability_score: float

@dataclass
class ConfidenceAnalysis:
    """Complete confidence analysis result"""
    confidence_score: float
    confidence_components: ConfidenceComponents
    validation_metrics: ValidationMetrics
    reliability_indicators: Dict[str, float]
    recommendations: List[str]

class RealConfidenceCalculator:
    """Real implementation of confidence calculation using statistical validation"""
    
    def __init__(self, db_path: str = "sentiment_data.db"):
        self.db_path = db_path
        self.historical_data = self._load_historical_data()
        self.validation_metrics = self._calculate_validation_metrics()
        
        # Confidence calculation weights
        self.component_weights = {
            'base_confidence': 0.25,
            'keyword_strength': 0.20,
            'pattern_clarity': 0.15,
            'historical_accuracy': 0.15,
            'text_quality': 0.10,
            'context_consistency': 0.10,
            'uncertainty_penalty': -0.05  # Negative weight (penalty)
        }
        
        # Keyword strength mappings
        self.strong_keywords = {
            'ENTHUSIASTIC_SUPPORT': ['amazing', 'incredible', 'perfect', 'love', 'best', 'awesome', 'fantastic'],
            'NOSTALGIC_APPRECIATION': ['remember', 'miss', 'nostalgia', 'back then', 'old days', 'memories'],
            'ANTICIPATORY_EXCITEMENT': ['can\'t wait', 'excited', 'upcoming', 'soon', 'anticipate', 'looking forward'],
            'PROTECTIVE_DEFENSIVE': ['defend', 'protect', 'unfair', 'wrong', 'misunderstood', 'support'],
            'CRITICAL_DISAPPOINTMENT': ['disappointed', 'expected better', 'not good', 'could be better'],
            'NEUTRAL_FACTUAL': ['announced', 'reported', 'confirmed', 'stated', 'according to'],
            'COMPETITIVE_RIVALRY': ['better than', 'superior', 'beat', 'outperform', 'compete'],
            'SARCASTIC_MOCKERY': ['sure', 'right', 'obviously', 'totally', 'great job'],
            'MALICIOUS_COORDINATED': ['hate', 'destroy', 'attack', 'boycott', 'cancel'],
            'MIXED_CONFLICTED': ['but', 'however', 'although', 'mixed feelings', 'torn']
        }
    
    def _load_historical_data(self) -> pd.DataFrame:
        """Load historical data for validation"""
        try:
            conn = sqlite3.connect(self.db_path)
            query = """
            SELECT text, predicted_label, confidence, label_name, 
                   user_corrected_label, is_verified, timestamp
            FROM sentiment_analysis 
            WHERE timestamp >= datetime('now', '-90 days')
            ORDER BY timestamp DESC
            """
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except Exception:
            return pd.DataFrame()
    
    def _calculate_validation_metrics(self) -> ValidationMetrics:
        """Calculate validation metrics from historical data"""
        if self.historical_data.empty:
            return ValidationMetrics(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        
        # Filter data with corrections
        corrected_data = self.historical_data[self.historical_data['user_corrected_label'].notna()]
        
        if len(corrected_data) < 10:  # Need minimum data for meaningful metrics
            return ValidationMetrics(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        
        y_true = corrected_data['user_corrected_label'].values
        y_pred = corrected_data['predicted_label'].values
        
        # Calculate standard metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
        
        # Calculate calibration error
        calibration_error = self._calculate_calibration_error(corrected_data)
        
        # Calculate reliability score
        reliability_score = (accuracy + precision + recall + f1) / 4 * (1 - calibration_error)
        
        return ValidationMetrics(accuracy, precision, recall, f1, calibration_error, reliability_score)
    
    def _calculate_calibration_error(self, data: pd.DataFrame) -> float:
        """Calculate Expected Calibration Error (ECE)"""
        if len(data) < 10:
            return 0.5  # High uncertainty for small datasets
        
        # Bin predictions by confidence
        n_bins = 10
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        bin_lowers = bin_boundaries[:-1]
        bin_uppers = bin_boundaries[1:]
        
        ece = 0
        total_samples = len(data)
        
        for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
            # Find samples in this confidence bin
            in_bin = (data['confidence'] > bin_lower) & (data['confidence'] <= bin_upper)
            prop_in_bin = in_bin.sum() / total_samples
            
            if prop_in_bin > 0:
                # Calculate accuracy in this bin
                bin_data = data[in_bin]
                accuracy_in_bin = (bin_data['predicted_label'] == bin_data['user_corrected_label']).mean()
                avg_confidence_in_bin = bin_data['confidence'].mean()
                
                # Add to ECE
                ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin
        
        return ece
    
    def calculate_confidence(self, text: str, analysis_result: Dict) -> ConfidenceAnalysis:
        """Calculate comprehensive confidence score"""
        # Extract basic information
        predicted_label = analysis_result.get('predicted_label', 0)
        label_name = analysis_result.get('label_name', 'UNKNOWN')
        base_confidence = analysis_result.get('confidence', 0.5)
        
        # Calculate individual components
        components = self._calculate_confidence_components(text, label_name, base_confidence)
        
        # Calculate final confidence score
        final_confidence = self._combine_confidence_components(components)
        
        # Calculate reliability indicators
        reliability_indicators = self._calculate_reliability_indicators(text, analysis_result, final_confidence)
        
        # Generate recommendations
        recommendations = self._generate_confidence_recommendations(components, reliability_indicators)
        
        return ConfidenceAnalysis(
            confidence_score=final_confidence,
            confidence_components=components,
            validation_metrics=self.validation_metrics,
            reliability_indicators=reliability_indicators,
            recommendations=recommendations
        )
    
    def _calculate_confidence_components(self, text: str, label_name: str, base_confidence: float) -> ConfidenceComponents:
        """Calculate individual confidence components"""
        
        # 1. Keyword strength analysis
        keyword_strength = self._analyze_keyword_strength(text, label_name)
        
        # 2. Pattern clarity analysis
        pattern_clarity = self._analyze_pattern_clarity(text, label_name)
        
        # 3. Historical accuracy for this label
        historical_accuracy = self._get_historical_accuracy(label_name)
        
        # 4. Text quality assessment
        text_quality = self._assess_text_quality(text)
        
        # 5. Context consistency
        context_consistency = self._assess_context_consistency(text, label_name)
        
        # 6. Uncertainty penalty
        uncertainty_penalty = self._calculate_uncertainty_penalty(text)
        
        # Combine components
        final_confidence = self._combine_confidence_components_raw(
            base_confidence, keyword_strength, pattern_clarity, 
            historical_accuracy, text_quality, context_consistency, uncertainty_penalty
        )
        
        return ConfidenceComponents(
            base_confidence=base_confidence,
            keyword_strength=keyword_strength,
            pattern_clarity=pattern_clarity,
            historical_accuracy=historical_accuracy,
            text_quality=text_quality,
            context_consistency=context_consistency,
            uncertainty_penalty=uncertainty_penalty,
            final_confidence=final_confidence
        )
    
    def _analyze_keyword_strength(self, text: str, label_name: str) -> float:
        """Analyze strength of keywords for the predicted label"""
        text_lower = text.lower()
        
        # Get strong keywords for this label
        strong_keywords = self.strong_keywords.get(label_name, [])
        
        if not strong_keywords:
            return 0.5  # Neutral if no keywords defined
        
        # Count keyword matches
        keyword_matches = sum(1 for keyword in strong_keywords if keyword in text_lower)
        
        # Calculate strength based on matches and text length
        text_words = len(text.split())
        keyword_density = keyword_matches / max(1, text_words)
        
        # Normalize to 0-1 scale
        strength = min(1.0, keyword_density * 10)  # Scale factor of 10
        
        # Boost for multiple strong keywords
        if keyword_matches >= 2:
            strength = min(1.0, strength * 1.2)
        
        return strength
    
    def _analyze_pattern_clarity(self, text: str, label_name: str) -> float:
        """Analyze clarity of sentiment patterns in text"""
        text_lower = text.lower()
        
        # Pattern indicators for different sentiment types
        pattern_scores = {
            'ENTHUSIASTIC_SUPPORT': self._score_enthusiasm_patterns(text_lower),
            'NOSTALGIC_APPRECIATION': self._score_nostalgia_patterns(text_lower),
            'ANTICIPATORY_EXCITEMENT': self._score_anticipation_patterns(text_lower),
            'PROTECTIVE_DEFENSIVE': self._score_defensive_patterns(text_lower),
            'CRITICAL_DISAPPOINTMENT': self._score_criticism_patterns(text_lower),
            'NEUTRAL_FACTUAL': self._score_neutral_patterns(text_lower),
            'COMPETITIVE_RIVALRY': self._score_competitive_patterns(text_lower),
            'SARCASTIC_MOCKERY': self._score_sarcasm_patterns(text_lower),
            'MALICIOUS_COORDINATED': self._score_malicious_patterns(text_lower),
            'MIXED_CONFLICTED': self._score_mixed_patterns(text_lower)
        }
        
        # Get score for predicted label
        predicted_score = pattern_scores.get(label_name, 0.5)
        
        # Calculate clarity by comparing with other labels
        other_scores = [score for label, score in pattern_scores.items() if label != label_name]
        
        if other_scores:
            max_other_score = max(other_scores)
            clarity = max(0, predicted_score - max_other_score + 0.5)  # Add baseline
        else:
            clarity = predicted_score
        
        return min(1.0, clarity)
    
    def _score_enthusiasm_patterns(self, text: str) -> float:
        """Score enthusiasm patterns"""
        score = 0.0
        
        # Exclamation marks
        exclamations = text.count('!')
        score += min(0.3, exclamations * 0.1)
        
        # Caps words
        caps_words = len(re.findall(r'\b[A-Z]{2,}\b', text))
        score += min(0.2, caps_words * 0.1)
        
        # Positive emojis (simplified detection)
        positive_emojis = ['🔥', '💜', '❤️', '😍', '🤩', '✨']
        emoji_count = sum(text.count(emoji) for emoji in positive_emojis)
        score += min(0.3, emoji_count * 0.15)
        
        # Enthusiasm words
        enthusiasm_words = ['amazing', 'incredible', 'awesome', 'fantastic', 'perfect', 'love']
        word_count = sum(1 for word in enthusiasm_words if word in text)
        score += min(0.4, word_count * 0.2)
        
        return min(1.0, score)
    
    def _score_nostalgia_patterns(self, text: str) -> float:
        """Score nostalgia patterns"""
        score = 0.0
        
        # Time references
        time_words = ['remember', 'miss', 'back then', 'old', 'used to', 'before', 'past']
        time_count = sum(1 for word in time_words if word in text)
        score += min(0.5, time_count * 0.25)
        
        # Emotional words
        emotion_words = ['memories', 'nostalgia', 'feels', 'emotional']
        emotion_count = sum(1 for word in emotion_words if word in text)
        score += min(0.3, emotion_count * 0.3)
        
        # Gentle tone (fewer exclamations, more periods)
        if text.count('.') > text.count('!'):
            score += 0.2
        
        return min(1.0, score)
    
    def _score_anticipation_patterns(self, text: str) -> float:
        """Score anticipation patterns"""
        score = 0.0
        
        # Future tense words
        future_words = ['will', 'going to', 'soon', 'upcoming', 'next', 'can\'t wait']
        future_count = sum(1 for word in future_words if word in text)
        score += min(0.4, future_count * 0.2)
        
        # Excitement indicators
        excitement_words = ['excited', 'anticipate', 'looking forward', 'hope']
        excitement_count = sum(1 for word in excitement_words if word in text)
        score += min(0.4, excitement_count * 0.2)
        
        # Question marks (anticipatory questions)
        questions = text.count('?')
        score += min(0.2, questions * 0.1)
        
        return min(1.0, score)
    
    def _score_defensive_patterns(self, text: str) -> float:
        """Score defensive patterns"""
        score = 0.0
        
        # Defensive words
        defensive_words = ['defend', 'protect', 'unfair', 'wrong', 'misunderstood', 'actually']
        defensive_count = sum(1 for word in defensive_words if word in text)
        score += min(0.5, defensive_count * 0.25)
        
        # Contradiction patterns
        contradiction_words = ['but', 'however', 'actually', 'no', 'not true']
        contradiction_count = sum(1 for word in contradiction_words if word in text)
        score += min(0.3, contradiction_count * 0.15)
        
        return min(1.0, score)
    
    def _score_criticism_patterns(self, text: str) -> float:
        """Score criticism patterns"""
        score = 0.0
        
        # Critical words
        critical_words = ['disappointed', 'expected better', 'not good', 'could be better', 'lacking']
        critical_count = sum(1 for word in critical_words if word in text)
        score += min(0.5, critical_count * 0.25)
        
        # Comparative criticism
        if 'better' in text or 'worse' in text:
            score += 0.2
        
        return min(1.0, score)
    
    def _score_neutral_patterns(self, text: str) -> float:
        """Score neutral patterns"""
        score = 0.0
        
        # Factual words
        factual_words = ['announced', 'reported', 'confirmed', 'stated', 'according to']
        factual_count = sum(1 for word in factual_words if word in text)
        score += min(0.5, factual_count * 0.25)
        
        # Lack of emotional indicators
        emotional_indicators = text.count('!') + text.count('?') + len(re.findall(r'[😀-🙏]', text))
        if emotional_indicators == 0:
            score += 0.3
        
        return min(1.0, score)
    
    def _score_competitive_patterns(self, text: str) -> float:
        """Score competitive patterns"""
        score = 0.0
        
        # Competitive words
        competitive_words = ['better than', 'superior', 'beat', 'outperform', 'vs', 'versus']
        competitive_count = sum(1 for word in competitive_words if word in text)
        score += min(0.5, competitive_count * 0.25)
        
        # Comparison patterns
        if ' vs ' in text or ' versus ' in text:
            score += 0.3
        
        return min(1.0, score)
    
    def _score_sarcasm_patterns(self, text: str) -> float:
        """Score sarcasm patterns"""
        score = 0.0
        
        # Sarcastic words
        sarcastic_words = ['sure', 'right', 'obviously', 'totally', 'great job']
        sarcastic_count = sum(1 for word in sarcastic_words if word in text)
        score += min(0.4, sarcastic_count * 0.2)
        
        # Quotes (often sarcastic)
        if '"' in text or "'" in text:
            score += 0.2
        
        # Ellipsis
        if '...' in text:
            score += 0.2
        
        return min(1.0, score)
    
    def _score_malicious_patterns(self, text: str) -> float:
        """Score malicious patterns"""
        score = 0.0
        
        # Malicious words
        malicious_words = ['hate', 'destroy', 'attack', 'boycott', 'cancel', 'toxic']
        malicious_count = sum(1 for word in malicious_words if word in text)
        score += min(0.6, malicious_count * 0.3)
        
        # Aggressive punctuation
        if text.count('!') > 3:
            score += 0.2
        
        return min(1.0, score)
    
    def _score_mixed_patterns(self, text: str) -> float:
        """Score mixed/conflicted patterns"""
        score = 0.0
        
        # Contradiction words
        contradiction_words = ['but', 'however', 'although', 'though', 'yet']
        contradiction_count = sum(1 for word in contradiction_words if word in text)
        score += min(0.5, contradiction_count * 0.25)
        
        # Mixed emotional indicators
        positive_words = ['love', 'great', 'good', 'amazing']
        negative_words = ['hate', 'bad', 'terrible', 'awful']
        
        pos_count = sum(1 for word in positive_words if word in text)
        neg_count = sum(1 for word in negative_words if word in text)
        
        if pos_count > 0 and neg_count > 0:
            score += 0.4
        
        return min(1.0, score)
    
    def _get_historical_accuracy(self, label_name: str) -> float:
        """Get historical accuracy for this specific label"""
        if self.historical_data.empty:
            return 0.5  # Neutral if no historical data
        
        # Filter data for this label
        label_data = self.historical_data[self.historical_data['label_name'] == label_name]
        
        if len(label_data) < 5:  # Need minimum data
            return 0.5
        
        # Calculate accuracy for this label
        corrected_data = label_data[label_data['user_corrected_label'].notna()]
        
        if len(corrected_data) == 0:
            return 0.7  # Assume good if no corrections
        
        correct_predictions = (corrected_data['predicted_label'] == corrected_data['user_corrected_label']).sum()
        accuracy = correct_predictions / len(corrected_data)
        
        return accuracy
    
    def _assess_text_quality(self, text: str) -> float:
        """Assess overall text quality for analysis"""
        score = 0.0
        
        # Length assessment
        length = len(text.strip())
        if 20 <= length <= 200:  # Optimal length
            score += 0.3
        elif 10 <= length <= 300:  # Acceptable length
            score += 0.2
        else:
            score += 0.1  # Too short or too long
        
        # Language clarity (simplified)
        words = text.split()
        if len(words) >= 3:  # Has multiple words
            score += 0.2
        
        # Punctuation appropriateness
        if text.count('!') <= 3 and text.count('?') <= 2:  # Not excessive
            score += 0.2
        
        # Character variety (not just repeated characters)
        unique_chars = len(set(text.lower()))
        if unique_chars >= 10:
            score += 0.2
        
        # Grammar indicators (simplified)
        if text[0].isupper() and text.endswith(('.', '!', '?')):  # Basic sentence structure
            score += 0.1
        
        return min(1.0, score)
    
    def _assess_context_consistency(self, text: str, label_name: str) -> float:
        """Assess consistency between text context and predicted label"""
        # This is a simplified implementation
        # In a real system, this would use more sophisticated NLP
        
        text_lower = text.lower()
        
        # Check for K-Pop context
        kpop_terms = ['bts', 'blackpink', 'twice', 'stray kids', 'itzy', 'aespa', 'comeback', 'mv', 'album']
        has_kpop_context = any(term in text_lower for term in kpop_terms)
        
        context_score = 0.7 if has_kpop_context else 0.5
        
        # Check for sentiment-context alignment
        if label_name == 'ENTHUSIASTIC_SUPPORT' and ('love' in text_lower or 'amazing' in text_lower):
            context_score += 0.2
        elif label_name == 'CRITICAL_DISAPPOINTMENT' and ('disappointed' in text_lower or 'not good' in text_lower):
            context_score += 0.2
        elif label_name == 'NEUTRAL_FACTUAL' and any(word in text_lower for word in ['announced', 'reported', 'confirmed']):
            context_score += 0.2
        
        return min(1.0, context_score)
    
    def _calculate_uncertainty_penalty(self, text: str) -> float:
        """Calculate penalty based on uncertainty factors"""
        penalty = 0.0
        
        # Mixed signals penalty
        positive_indicators = text.lower().count('good') + text.lower().count('great') + text.lower().count('love')
        negative_indicators = text.lower().count('bad') + text.lower().count('hate') + text.lower().count('terrible')
        
        if positive_indicators > 0 and negative_indicators > 0:
            penalty += 0.3
        
        # Sarcasm risk penalty
        sarcasm_indicators = ['sure', 'right', 'obviously', 'totally']
        sarcasm_count = sum(1 for indicator in sarcasm_indicators if indicator in text.lower())
        penalty += min(0.3, sarcasm_count * 0.15)
        
        # Length penalty
        if len(text) < 10:
            penalty += 0.2
        elif len(text) > 300:
            penalty += 0.1
        
        return min(1.0, penalty)
    
    def _combine_confidence_components_raw(self, base_confidence: float, keyword_strength: float,
                                         pattern_clarity: float, historical_accuracy: float,
                                         text_quality: float, context_consistency: float,
                                         uncertainty_penalty: float) -> float:
        """Combine confidence components using weighted average"""
        
        weighted_sum = (
            base_confidence * self.component_weights['base_confidence'] +
            keyword_strength * self.component_weights['keyword_strength'] +
            pattern_clarity * self.component_weights['pattern_clarity'] +
            historical_accuracy * self.component_weights['historical_accuracy'] +
            text_quality * self.component_weights['text_quality'] +
            context_consistency * self.component_weights['context_consistency'] +
            uncertainty_penalty * self.component_weights['uncertainty_penalty']
        )
        
        return max(0.1, min(1.0, weighted_sum))
    
    def _combine_confidence_components(self, components: ConfidenceComponents) -> float:
        """Combine confidence components"""
        return components.final_confidence
    
    def _calculate_reliability_indicators(self, text: str, analysis_result: Dict, final_confidence: float) -> Dict[str, float]:
        """Calculate various reliability indicators"""
        indicators = {}
        
        # Text-based reliability
        text_length = len(text.strip())
        indicators['text_length_reliability'] = min(1.0, text_length / 100) if text_length <= 100 else max(0.5, 100 / text_length)
        
        # Confidence calibration
        indicators['confidence_calibration'] = 1 - self.validation_metrics.calibration_error
        
        # Historical performance
        indicators['historical_reliability'] = self.validation_metrics.reliability_score
        
        # Consistency check
        base_confidence = analysis_result.get('confidence', 0.5)
        confidence_consistency = 1 - abs(final_confidence - base_confidence)
        indicators['confidence_consistency'] = confidence_consistency
        
        # Overall reliability
        indicators['overall_reliability'] = np.mean(list(indicators.values()))
        
        return indicators
    
    def _generate_confidence_recommendations(self, components: ConfidenceComponents, 
                                           reliability_indicators: Dict[str, float]) -> List[str]:
        """Generate recommendations based on confidence analysis"""
        recommendations = []
        
        # Low confidence recommendations
        if components.final_confidence < 0.5:
            recommendations.append("⚠️ Low confidence score - consider manual review")
            
            if components.keyword_strength < 0.3:
                recommendations.append("🔍 Weak keyword indicators - text may be ambiguous")
            
            if components.text_quality < 0.5:
                recommendations.append("📝 Poor text quality - may affect analysis accuracy")
        
        # Medium confidence recommendations
        elif components.final_confidence < 0.7:
            recommendations.append("📊 Medium confidence - result likely reliable but monitor for edge cases")
            
            if components.uncertainty_penalty > 0.3:
                recommendations.append("🤔 High uncertainty detected - check for mixed signals or sarcasm")
        
        # High confidence recommendations
        else:
            recommendations.append("✅ High confidence - result highly reliable")
        
        # Specific component recommendations
        if components.historical_accuracy < 0.6:
            recommendations.append("📈 This sentiment type has lower historical accuracy - extra caution advised")
        
        if reliability_indicators.get('confidence_calibration', 0) < 0.7:
            recommendations.append("⚖️ Model calibration could be improved - confidence scores may be overconfident")
        
        if reliability_indicators.get('text_length_reliability', 0) < 0.5:
            recommendations.append("📏 Text length suboptimal for analysis - consider requesting more context")
        
        return recommendations

def test_confidence_calculator():
    """Test the confidence calculator"""
    print("=== TESTING CONFIDENCE CALCULATOR ===")
    
    calculator = RealConfidenceCalculator()
    
    print(f"Historical data points: {len(calculator.historical_data)}")
    print(f"Validation accuracy: {calculator.validation_metrics.accuracy:.3f}")
    print(f"Calibration error: {calculator.validation_metrics.calibration_error:.3f}")
    
    # Test cases
    test_cases = [
        {
            'text': 'OMG BTS absolutely SLAYED this performance! 🔥💜',
            'analysis': {'predicted_label': 0, 'confidence': 0.85, 'label_name': 'ENTHUSIASTIC_SUPPORT'}
        },
        {
            'text': 'Sure, that was a "great" performance... 🙄',
            'analysis': {'predicted_label': 7, 'confidence': 0.65, 'label_name': 'SARCASTIC_MOCKERY'}
        },
        {
            'text': 'The group announced their comeback date.',
            'analysis': {'predicted_label': 5, 'confidence': 0.75, 'label_name': 'NEUTRAL_FACTUAL'}
        },
        {
            'text': 'I love this song but the choreography is disappointing',
            'analysis': {'predicted_label': 9, 'confidence': 0.55, 'label_name': 'MIXED_CONFLICTED'}
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n=== Test Case {i} ===")
        print(f"Text: {case['text']}")
        
        result = calculator.calculate_confidence(case['text'], case['analysis'])
        
        print(f"Original confidence: {case['analysis']['confidence']:.3f}")
        print(f"Calculated confidence: {result.confidence_score:.3f}")
        print(f"Overall reliability: {result.reliability_indicators['overall_reliability']:.3f}")
        
        print("Component breakdown:")
        components = result.confidence_components
        print(f"  Base: {components.base_confidence:.3f}")
        print(f"  Keywords: {components.keyword_strength:.3f}")
        print(f"  Patterns: {components.pattern_clarity:.3f}")
        print(f"  Historical: {components.historical_accuracy:.3f}")
        print(f"  Quality: {components.text_quality:.3f}")
        print(f"  Uncertainty penalty: {components.uncertainty_penalty:.3f}")
        
        print("Recommendations:")
        for rec in result.recommendations:
            print(f"  • {rec}")

if __name__ == "__main__":
    test_confidence_calculator()