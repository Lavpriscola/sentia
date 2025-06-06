"""
Real Uncertainty Analysis Implementation
Provides comprehensive uncertainty assessment for sentiment analysis results
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import Counter
import re
import math
from scipy import stats
# from sklearn.metrics import entropy  # Not available in this sklearn version
import sqlite3
from datetime import datetime, timedelta

@dataclass
class UncertaintyFactor:
    """Represents a specific uncertainty factor"""
    name: str
    value: float
    impact_level: str  # 'low', 'medium', 'high', 'critical'
    description: str
    confidence_penalty: float  # How much this reduces confidence (0-1)

@dataclass
class UncertaintyAnalysis:
    """Complete uncertainty analysis result"""
    overall_uncertainty: float
    confidence_adjusted: float
    uncertainty_factors: List[UncertaintyFactor]
    reliability_score: float
    recommendation: str

class RealUncertaintyAnalyzer:
    """Real implementation of uncertainty analysis using statistical methods"""
    
    def __init__(self, db_path: str = "sentiment_data.db"):
        self.db_path = db_path
        self.historical_data = self._load_historical_data()
        
        # Statistical thresholds based on empirical analysis
        self.length_optimal_range = (10, 200)  # characters
        self.mixed_signal_threshold = 0.3
        self.sarcasm_indicators = [
            'sure', 'right', 'totally', 'obviously', 'definitely',
            'wow', 'great', 'amazing', 'perfect', 'brilliant'
        ]
        self.uncertainty_weights = {
            'text_length': 0.15,
            'mixed_signals': 0.25,
            'language_confidence': 0.20,
            'sarcasm_risk': 0.15,
            'cultural_context': 0.10,
            'historical_variance': 0.10,
            'keyword_ambiguity': 0.05
        }
    
    def _load_historical_data(self) -> pd.DataFrame:
        """Load historical analysis data for statistical comparison"""
        try:
            conn = sqlite3.connect(self.db_path)
            query = """
            SELECT text, predicted_label, confidence, label_name, 
                   user_corrected_label, is_verified, timestamp
            FROM sentiment_analysis 
            WHERE timestamp >= datetime('now', '-30 days')
            """
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except Exception:
            # Return empty DataFrame if no historical data
            return pd.DataFrame()
    
    def analyze_uncertainty(self, text: str, analysis_result: Dict) -> UncertaintyAnalysis:
        """Perform comprehensive uncertainty analysis"""
        factors = []
        
        # 1. Text Length Analysis
        length_factor = self._analyze_text_length(text)
        factors.append(length_factor)
        
        # 2. Mixed Signal Detection
        mixed_signal_factor = self._analyze_mixed_signals(text, analysis_result)
        factors.append(mixed_signal_factor)
        
        # 3. Language Confidence Assessment
        language_factor = self._analyze_language_confidence(text, analysis_result)
        factors.append(language_factor)
        
        # 4. Sarcasm Detection Risk
        sarcasm_factor = self._analyze_sarcasm_risk(text, analysis_result)
        factors.append(sarcasm_factor)
        
        # 5. Cultural Context Assessment
        cultural_factor = self._analyze_cultural_context(text)
        factors.append(cultural_factor)
        
        # 6. Historical Variance Analysis
        historical_factor = self._analyze_historical_variance(text, analysis_result)
        factors.append(historical_factor)
        
        # 7. Keyword Ambiguity Assessment
        ambiguity_factor = self._analyze_keyword_ambiguity(text)
        factors.append(ambiguity_factor)
        
        # Calculate overall uncertainty
        overall_uncertainty = self._calculate_overall_uncertainty(factors)
        
        # Adjust confidence based on uncertainty
        original_confidence = analysis_result.get('confidence', 0.5)
        confidence_adjusted = self._adjust_confidence(original_confidence, factors)
        
        # Calculate reliability score
        reliability_score = self._calculate_reliability_score(factors, confidence_adjusted)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(overall_uncertainty, factors)
        
        return UncertaintyAnalysis(
            overall_uncertainty=overall_uncertainty,
            confidence_adjusted=confidence_adjusted,
            uncertainty_factors=factors,
            reliability_score=reliability_score,
            recommendation=recommendation
        )
    
    def _analyze_text_length(self, text: str) -> UncertaintyFactor:
        """Analyze uncertainty based on text length"""
        length = len(text.strip())
        
        if length < self.length_optimal_range[0]:
            # Too short
            uncertainty = 0.8 - (length / self.length_optimal_range[0]) * 0.6
            impact = 'high' if length < 5 else 'medium'
            description = f"Text too short ({length} chars) for reliable analysis"
            penalty = 0.3 if length < 5 else 0.15
        elif length > self.length_optimal_range[1]:
            # Too long
            excess = length - self.length_optimal_range[1]
            uncertainty = min(0.7, 0.2 + (excess / 500) * 0.5)
            impact = 'medium' if excess < 300 else 'high'
            description = f"Text very long ({length} chars), may contain mixed sentiments"
            penalty = min(0.25, 0.1 + (excess / 1000) * 0.15)
        else:
            # Optimal length
            uncertainty = 0.1
            impact = 'low'
            description = f"Text length optimal ({length} chars)"
            penalty = 0.0
        
        return UncertaintyFactor(
            name="text_length",
            value=uncertainty,
            impact_level=impact,
            description=description,
            confidence_penalty=penalty
        )
    
    def _analyze_mixed_signals(self, text: str, analysis_result: Dict) -> UncertaintyFactor:
        """Detect conflicting sentiment indicators in text"""
        from sentiment_labels import SENTIMENT_LABELS
        
        # Count positive and negative indicators
        positive_words = ['love', 'amazing', 'great', 'best', 'perfect', 'awesome', 'incredible']
        negative_words = ['hate', 'terrible', 'worst', 'awful', 'horrible', 'disappointing', 'bad']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        # Check for contradictory patterns
        has_but = ' but ' in text_lower or ' however ' in text_lower
        has_question = '?' in text
        has_mixed_punctuation = ('!' in text and '?' in text)
        
        # Calculate mixed signal score
        total_signals = positive_count + negative_count
        if total_signals == 0:
            signal_conflict = 0.0
        else:
            signal_conflict = min(positive_count, negative_count) / total_signals
        
        # Add contextual factors
        contextual_uncertainty = 0.0
        if has_but:
            contextual_uncertainty += 0.3
        if has_question:
            contextual_uncertainty += 0.2
        if has_mixed_punctuation:
            contextual_uncertainty += 0.1
        
        uncertainty = min(1.0, signal_conflict + contextual_uncertainty)
        
        if uncertainty > 0.5:
            impact = 'high'
            description = "Strong conflicting sentiment indicators detected"
            penalty = 0.25
        elif uncertainty > 0.3:
            impact = 'medium'
            description = "Some conflicting sentiment indicators present"
            penalty = 0.15
        else:
            impact = 'low'
            description = "Consistent sentiment indicators"
            penalty = uncertainty * 0.1
        
        return UncertaintyFactor(
            name="mixed_signals",
            value=uncertainty,
            impact_level=impact,
            description=description,
            confidence_penalty=penalty
        )
    
    def _analyze_language_confidence(self, text: str, analysis_result: Dict) -> UncertaintyFactor:
        """Assess confidence in language detection and processing"""
        # Check for mixed languages
        has_korean = bool(re.search(r'[\uAC00-\uD7AF]', text))
        has_japanese = bool(re.search(r'[\u3040-\u309F\u30A0-\u30FF]', text))
        has_chinese = bool(re.search(r'[\u4E00-\u9FFF]', text))
        has_latin = bool(re.search(r'[a-zA-Z]', text))
        
        language_count = sum([has_korean, has_japanese, has_chinese, has_latin])
        
        # Check for transliteration or romanization
        has_romanized = bool(re.search(r'\b(oppa|unnie|hyung|noona|aegyo|daebak|fighting)\b', text.lower()))
        
        # Assess language mixing uncertainty
        if language_count > 2:
            uncertainty = 0.7
            impact = 'high'
            description = "Multiple languages detected, processing may be unreliable"
            penalty = 0.3
        elif language_count == 2:
            uncertainty = 0.4
            impact = 'medium'
            description = "Mixed language content detected"
            penalty = 0.15
        elif has_romanized:
            uncertainty = 0.3
            impact = 'medium'
            description = "Romanized K-Pop terms detected"
            penalty = 0.1
        else:
            uncertainty = 0.1
            impact = 'low'
            description = "Single language, clear processing"
            penalty = 0.0
        
        return UncertaintyFactor(
            name="language_confidence",
            value=uncertainty,
            impact_level=impact,
            description=description,
            confidence_penalty=penalty
        )
    
    def _analyze_sarcasm_risk(self, text: str, analysis_result: Dict) -> UncertaintyFactor:
        """Detect potential sarcasm that could affect sentiment accuracy"""
        text_lower = text.lower()
        
        # Sarcasm indicators
        sarcasm_score = 0.0
        
        # Check for sarcastic words
        sarcasm_words_found = [word for word in self.sarcasm_indicators if word in text_lower]
        sarcasm_score += len(sarcasm_words_found) * 0.2
        
        # Check for excessive punctuation (often sarcastic)
        exclamation_count = text.count('!')
        if exclamation_count > 2:
            sarcasm_score += min(0.3, exclamation_count * 0.1)
        
        # Check for quotes (often indicate sarcasm)
        if '"' in text or "'" in text:
            sarcasm_score += 0.2
        
        # Check for ALL CAPS (can indicate sarcasm)
        caps_words = re.findall(r'\b[A-Z]{3,}\b', text)
        if caps_words:
            sarcasm_score += min(0.3, len(caps_words) * 0.1)
        
        # Check for ellipsis (often sarcastic)
        if '...' in text:
            sarcasm_score += 0.2
        
        uncertainty = min(1.0, sarcasm_score)
        
        if uncertainty > 0.6:
            impact = 'high'
            description = f"High sarcasm risk detected (indicators: {', '.join(sarcasm_words_found)})"
            penalty = 0.3
        elif uncertainty > 0.3:
            impact = 'medium'
            description = "Moderate sarcasm risk detected"
            penalty = 0.15
        else:
            impact = 'low'
            description = "Low sarcasm risk"
            penalty = uncertainty * 0.1
        
        return UncertaintyFactor(
            name="sarcasm_risk",
            value=uncertainty,
            impact_level=impact,
            description=description,
            confidence_penalty=penalty
        )
    
    def _analyze_cultural_context(self, text: str) -> UncertaintyFactor:
        """Assess uncertainty due to cultural context requirements"""
        # K-Pop specific terms and cultural references
        kpop_terms = [
            'comeback', 'debut', 'bias', 'stan', 'fandom', 'visual', 'maknae',
            'leader', 'main vocal', 'lead dancer', 'center', 'face of the group',
            'aegyo', 'skinship', 'sasaeng', 'anti', 'akgae'
        ]
        
        cultural_terms = [
            'sunbae', 'hoobae', 'hyung', 'oppa', 'unnie', 'noona',
            'fighting', 'daebak', 'jjang', 'hwaiting'
        ]
        
        text_lower = text.lower()
        
        kpop_count = sum(1 for term in kpop_terms if term in text_lower)
        cultural_count = sum(1 for term in cultural_terms if term in text_lower)
        
        # Calculate cultural complexity
        cultural_density = (kpop_count + cultural_count) / max(1, len(text.split()))
        
        if cultural_density > 0.3:
            uncertainty = 0.6
            impact = 'high'
            description = "High cultural context dependency"
            penalty = 0.2
        elif cultural_density > 0.1:
            uncertainty = 0.3
            impact = 'medium'
            description = "Moderate cultural context required"
            penalty = 0.1
        elif kpop_count > 0 or cultural_count > 0:
            uncertainty = 0.2
            impact = 'low'
            description = "Some cultural context present"
            penalty = 0.05
        else:
            uncertainty = 0.1
            impact = 'low'
            description = "Minimal cultural context required"
            penalty = 0.0
        
        return UncertaintyFactor(
            name="cultural_context",
            value=uncertainty,
            impact_level=impact,
            description=description,
            confidence_penalty=penalty
        )
    
    def _analyze_historical_variance(self, text: str, analysis_result: Dict) -> UncertaintyFactor:
        """Analyze uncertainty based on historical prediction variance"""
        if self.historical_data.empty:
            return UncertaintyFactor(
                name="historical_variance",
                value=0.3,
                impact_level='medium',
                description="No historical data available for comparison",
                confidence_penalty=0.1
            )
        
        # Find similar texts in historical data
        predicted_label = analysis_result.get('predicted_label', 0)
        confidence = analysis_result.get('confidence', 0.5)
        
        # Get historical data for same label
        same_label_data = self.historical_data[
            self.historical_data['predicted_label'] == predicted_label
        ]
        
        if len(same_label_data) < 5:
            uncertainty = 0.4
            impact = 'medium'
            description = f"Limited historical data for this sentiment type ({len(same_label_data)} samples)"
            penalty = 0.15
        else:
            # Calculate variance in confidence scores
            confidence_variance = same_label_data['confidence'].var()
            
            # Calculate correction rate
            corrected_data = same_label_data[same_label_data['user_corrected_label'].notna()]
            if len(same_label_data) > 0:
                correction_rate = len(corrected_data) / len(same_label_data)
            else:
                correction_rate = 0.0
            
            # Combine variance and correction rate
            uncertainty = min(1.0, confidence_variance * 2 + correction_rate)
            
            if uncertainty > 0.5:
                impact = 'high'
                description = f"High historical variance (correction rate: {correction_rate:.1%})"
                penalty = 0.2
            elif uncertainty > 0.3:
                impact = 'medium'
                description = f"Moderate historical variance (correction rate: {correction_rate:.1%})"
                penalty = 0.1
            else:
                impact = 'low'
                description = f"Low historical variance (correction rate: {correction_rate:.1%})"
                penalty = uncertainty * 0.1
        
        return UncertaintyFactor(
            name="historical_variance",
            value=uncertainty,
            impact_level=impact,
            description=description,
            confidence_penalty=penalty
        )
    
    def _analyze_keyword_ambiguity(self, text: str) -> UncertaintyFactor:
        """Assess uncertainty due to ambiguous keywords"""
        # Words that can have multiple meanings in K-Pop context
        ambiguous_words = {
            'fire': ['amazing', 'disaster'],
            'sick': ['cool', 'ill'],
            'mad': ['angry', 'crazy good'],
            'insane': ['crazy', 'amazing'],
            'dead': ['exhausted', 'extremely funny'],
            'killed': ['performed amazingly', 'destroyed'],
            'slayed': ['performed amazingly', 'killed'],
            'destroyed': ['performed amazingly', 'ruined']
        }
        
        text_lower = text.lower()
        ambiguous_found = []
        
        for word, meanings in ambiguous_words.items():
            if word in text_lower:
                ambiguous_found.append(word)
        
        # Calculate ambiguity score
        ambiguity_score = len(ambiguous_found) / max(1, len(text.split())) * 2
        uncertainty = min(1.0, ambiguity_score)
        
        if uncertainty > 0.4:
            impact = 'high'
            description = f"High keyword ambiguity (words: {', '.join(ambiguous_found)})"
            penalty = 0.2
        elif uncertainty > 0.2:
            impact = 'medium'
            description = f"Moderate keyword ambiguity (words: {', '.join(ambiguous_found)})"
            penalty = 0.1
        else:
            impact = 'low'
            description = "Low keyword ambiguity"
            penalty = uncertainty * 0.05
        
        return UncertaintyFactor(
            name="keyword_ambiguity",
            value=uncertainty,
            impact_level=impact,
            description=description,
            confidence_penalty=penalty
        )
    
    def _calculate_overall_uncertainty(self, factors: List[UncertaintyFactor]) -> float:
        """Calculate weighted overall uncertainty score"""
        total_uncertainty = 0.0
        
        for factor in factors:
            weight = self.uncertainty_weights.get(factor.name, 0.1)
            total_uncertainty += factor.value * weight
        
        return min(1.0, total_uncertainty)
    
    def _adjust_confidence(self, original_confidence: float, factors: List[UncertaintyFactor]) -> float:
        """Adjust confidence based on uncertainty factors"""
        total_penalty = sum(factor.confidence_penalty for factor in factors)
        adjusted_confidence = original_confidence * (1 - min(0.8, total_penalty))
        return max(0.1, adjusted_confidence)  # Minimum confidence of 0.1
    
    def _calculate_reliability_score(self, factors: List[UncertaintyFactor], adjusted_confidence: float) -> float:
        """Calculate overall reliability score (0-1)"""
        # Combine adjusted confidence with uncertainty factors
        high_impact_factors = sum(1 for f in factors if f.impact_level == 'high')
        medium_impact_factors = sum(1 for f in factors if f.impact_level == 'medium')
        
        reliability = adjusted_confidence
        reliability -= high_impact_factors * 0.15
        reliability -= medium_impact_factors * 0.08
        
        return max(0.0, min(1.0, reliability))
    
    def _generate_recommendation(self, overall_uncertainty: float, factors: List[UncertaintyFactor]) -> str:
        """Generate actionable recommendation based on uncertainty analysis"""
        high_impact_factors = [f for f in factors if f.impact_level == 'high']
        
        if overall_uncertainty > 0.7:
            return "HIGH UNCERTAINTY: Manual review strongly recommended. Consider additional context or human verification."
        elif overall_uncertainty > 0.5:
            return "MEDIUM UNCERTAINTY: Review recommended. Pay attention to context and potential ambiguity."
        elif overall_uncertainty > 0.3:
            return "LOW-MEDIUM UNCERTAINTY: Generally reliable but monitor for edge cases."
        elif high_impact_factors:
            primary_issue = high_impact_factors[0].name.replace('_', ' ').title()
            return f"CAUTION: {primary_issue} detected. Result likely reliable but verify if critical."
        else:
            return "LOW UNCERTAINTY: High confidence in analysis result."

def test_uncertainty_analyzer():
    """Test the uncertainty analyzer with real examples"""
    analyzer = RealUncertaintyAnalyzer()
    
    test_cases = [
        {
            'text': 'BTS is amazing!',
            'analysis': {'predicted_label': 1, 'confidence': 0.9, 'label_name': 'ENTHUSIASTIC_SUPPORT'}
        },
        {
            'text': 'Sure, that performance was "great"... 🙄',
            'analysis': {'predicted_label': 8, 'confidence': 0.7, 'label_name': 'SARCASTIC_MOCKERY'}
        },
        {
            'text': 'I love this song but the choreography is disappointing',
            'analysis': {'predicted_label': 10, 'confidence': 0.6, 'label_name': 'MIXED_CONFLICTED'}
        },
        {
            'text': '방탄소년단 정말 대박이야! But some fans are too much...',
            'analysis': {'predicted_label': 10, 'confidence': 0.5, 'label_name': 'MIXED_CONFLICTED'}
        }
    ]
    
    print("=== UNCERTAINTY ANALYSIS TEST ===")
    for i, case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {case['text']}")
        result = analyzer.analyze_uncertainty(case['text'], case['analysis'])
        
        print(f"Overall Uncertainty: {result.overall_uncertainty:.2f}")
        print(f"Adjusted Confidence: {result.confidence_adjusted:.2f}")
        print(f"Reliability Score: {result.reliability_score:.2f}")
        print(f"Recommendation: {result.recommendation}")
        
        print("Key Uncertainty Factors:")
        for factor in result.uncertainty_factors:
            if factor.impact_level in ['high', 'medium']:
                print(f"  - {factor.name}: {factor.value:.2f} ({factor.impact_level}) - {factor.description}")

if __name__ == "__main__":
    test_uncertainty_analyzer()