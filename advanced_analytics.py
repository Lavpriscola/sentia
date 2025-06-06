"""
Advanced Analytics and Uncertainty Assessment for K-Pop Sentiment Analysis
Provides comprehensive confidence scoring, uncertainty analysis, and visual feedback
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json
import sqlite3
from collections import defaultdict, Counter

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

@dataclass
class UncertaintyFactor:
    """Represents a factor contributing to analysis uncertainty"""
    name: str
    impact_level: str  # 'low', 'medium', 'high', 'very_high'
    impact_score: float  # 0.0 to 1.0
    description: str
    recommendation: Optional[str] = None

@dataclass
class ConfidenceBreakdown:
    """Detailed confidence analysis"""
    overall_confidence: float
    factor_scores: Dict[str, float]
    uncertainty_factors: List[UncertaintyFactor]
    reliability_assessment: str
    explanation: List[str]
    visual_indicators: Dict[str, any]

@dataclass
class AnalyticsReport:
    """Comprehensive analytics report"""
    summary_stats: Dict[str, any]
    trend_analysis: Dict[str, any]
    quality_metrics: Dict[str, any]
    language_distribution: Dict[str, any]
    uncertainty_patterns: Dict[str, any]
    risk_assessment: Dict[str, any]
    recommendations: List[str]
    generated_at: datetime

class UncertaintyAnalyzer:
    """Analyzes uncertainty factors in sentiment analysis"""
    
    def __init__(self):
        self.uncertainty_thresholds = {
            'text_length_min': 5,
            'text_length_max': 200,
            'confidence_threshold': 0.7,
            'mixed_signal_ratio': 0.4,
            'language_confidence_min': 0.8
        }
    
    def analyze_uncertainty_factors(self, text: str, analysis_result: Dict, language_info: Dict = None) -> List[UncertaintyFactor]:
        """Identify and analyze uncertainty factors"""
        factors = []
        
        # Text length analysis
        factors.append(self._assess_text_length(text))
        
        # Mixed signals detection
        factors.append(self._detect_mixed_signals(text, analysis_result))
        
        # Language confidence
        if language_info:
            factors.append(self._assess_language_confidence(language_info))
        
        # Ambiguous language patterns
        factors.append(self._detect_ambiguous_language(text))
        
        # Context dependency
        factors.append(self._assess_context_dependency(text))
        
        # Sarcasm uncertainty
        factors.append(self._assess_sarcasm_uncertainty(text))
        
        # Cultural context challenges
        factors.append(self._assess_cultural_context(text))
        
        return [f for f in factors if f.impact_score > 0.1]  # Filter low-impact factors
    
    def _assess_text_length(self, text: str) -> UncertaintyFactor:
        """Assess uncertainty due to text length"""
        word_count = len(text.split())
        
        if word_count < self.uncertainty_thresholds['text_length_min']:
            return UncertaintyFactor(
                name="text_length",
                impact_level="high",
                impact_score=0.8,
                description=f"Text is very short ({word_count} words), limiting analysis reliability",
                recommendation="Provide more context or combine with additional text for better accuracy"
            )
        elif word_count > self.uncertainty_thresholds['text_length_max']:
            return UncertaintyFactor(
                name="text_length",
                impact_level="medium",
                impact_score=0.5,
                description=f"Text is very long ({word_count} words), may contain mixed sentiments",
                recommendation="Consider analyzing in smaller segments for more precise results"
            )
        else:
            return UncertaintyFactor(
                name="text_length",
                impact_level="low",
                impact_score=0.1,
                description=f"Text length ({word_count} words) is optimal for analysis"
            )
    
    def _detect_mixed_signals(self, text: str, analysis_result: Dict) -> UncertaintyFactor:
        """Detect conflicting sentiment indicators"""
        # Count positive and negative indicators
        positive_words = ['love', 'amazing', 'perfect', 'best', 'incredible', 'beautiful']
        negative_words = ['hate', 'terrible', 'worst', 'awful', 'disappointing', 'bad']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > 0 and negative_count > 0:
            total_signals = positive_count + negative_count
            balance_ratio = min(positive_count, negative_count) / max(positive_count, negative_count)
            
            if balance_ratio > self.uncertainty_thresholds['mixed_signal_ratio']:
                return UncertaintyFactor(
                    name="mixed_signals",
                    impact_level="high",
                    impact_score=0.7,
                    description=f"Text contains both positive ({positive_count}) and negative ({negative_count}) indicators",
                    recommendation="Consider using MIXED_CONFLICTED label or analyze context more carefully"
                )
        
        return UncertaintyFactor(
            name="mixed_signals",
            impact_level="low",
            impact_score=0.1,
            description="Clear sentiment direction detected"
        )
    
    def _assess_language_confidence(self, language_info: Dict) -> UncertaintyFactor:
        """Assess uncertainty due to language detection confidence"""
        confidence = language_info.get('confidence', 0.5)
        detected_lang = language_info.get('detected_language', 'unknown')
        supported = language_info.get('supported', False)
        
        if confidence < self.uncertainty_thresholds['language_confidence_min']:
            return UncertaintyFactor(
                name="language_confidence",
                impact_level="high",
                impact_score=0.8,
                description=f"Low language detection confidence ({confidence:.1%}) for {detected_lang}",
                recommendation="Verify language manually or provide more text for better detection"
            )
        elif not supported:
            return UncertaintyFactor(
                name="language_support",
                impact_level="medium",
                impact_score=0.6,
                description=f"Language {detected_lang} not fully supported, using fallback processing",
                recommendation="Results may be less accurate for non-supported languages"
            )
        else:
            return UncertaintyFactor(
                name="language_confidence",
                impact_level="low",
                impact_score=0.1,
                description=f"High language detection confidence ({confidence:.1%}) for supported language"
            )
    
    def _detect_ambiguous_language(self, text: str) -> UncertaintyFactor:
        """Detect ambiguous language patterns"""
        ambiguous_patterns = [
            r'\b(kind of|sort of|maybe|perhaps|possibly)\b',
            r'\b(I guess|I think|I suppose)\b',
            r'\b(not sure|uncertain|unclear)\b'
        ]
        
        import re
        ambiguous_count = sum(len(re.findall(pattern, text.lower())) for pattern in ambiguous_patterns)
        
        if ambiguous_count > 2:
            return UncertaintyFactor(
                name="ambiguous_language",
                impact_level="medium",
                impact_score=0.6,
                description=f"Text contains {ambiguous_count} ambiguous expressions",
                recommendation="Author seems uncertain, consider lower confidence in classification"
            )
        elif ambiguous_count > 0:
            return UncertaintyFactor(
                name="ambiguous_language",
                impact_level="low",
                impact_score=0.3,
                description=f"Some ambiguous language detected ({ambiguous_count} instances)"
            )
        else:
            return UncertaintyFactor(
                name="ambiguous_language",
                impact_level="low",
                impact_score=0.1,
                description="Clear, definitive language used"
            )
    
    def _assess_context_dependency(self, text: str) -> UncertaintyFactor:
        """Assess how much the text depends on external context"""
        context_indicators = [
            r'\b(this|that|it|they)\b',  # Pronouns without clear antecedents
            r'\b(here|there|now|then)\b',  # Temporal/spatial references
            r'\b(the song|the video|the performance)\b'  # Definite articles without specification
        ]
        
        import re
        context_count = sum(len(re.findall(pattern, text.lower())) for pattern in context_indicators)
        word_count = len(text.split())
        context_ratio = context_count / word_count if word_count > 0 else 0
        
        if context_ratio > 0.3:
            return UncertaintyFactor(
                name="context_dependency",
                impact_level="medium",
                impact_score=0.5,
                description=f"Text heavily relies on external context ({context_ratio:.1%} context-dependent words)",
                recommendation="Provide more specific context for better analysis"
            )
        else:
            return UncertaintyFactor(
                name="context_dependency",
                impact_level="low",
                impact_score=0.2,
                description="Text is relatively self-contained"
            )
    
    def _assess_sarcasm_uncertainty(self, text: str) -> UncertaintyFactor:
        """Assess uncertainty in sarcasm detection"""
        sarcasm_indicators = [
            r'"[^"]*"',  # Quoted text
            r'\b(sure|right|okay|totally|obviously)\b',
            r'[😏😒🙄]',  # Sarcastic emojis
            r'\b(imagine|not)\b.*\b(thinking|saying)\b'
        ]
        
        import re
        sarcasm_count = sum(len(re.findall(pattern, text.lower())) for pattern in sarcasm_indicators)
        
        if sarcasm_count > 1:
            return UncertaintyFactor(
                name="sarcasm_uncertainty",
                impact_level="high",
                impact_score=0.7,
                description=f"Multiple sarcasm indicators detected ({sarcasm_count})",
                recommendation="Sarcasm is difficult to detect reliably, verify interpretation manually"
            )
        elif sarcasm_count > 0:
            return UncertaintyFactor(
                name="sarcasm_uncertainty",
                impact_level="medium",
                impact_score=0.4,
                description="Possible sarcasm detected, interpretation may vary"
            )
        else:
            return UncertaintyFactor(
                name="sarcasm_uncertainty",
                impact_level="low",
                impact_score=0.1,
                description="No clear sarcasm indicators"
            )
    
    def _assess_cultural_context(self, text: str) -> UncertaintyFactor:
        """Assess cultural context challenges"""
        cultural_terms = [
            'bias', 'stan', 'ult', 'visual', 'maknae', 'hyung', 'oppa', 'unnie',
            'comeback', 'debut', 'mv', 'choreography', 'fandom'
        ]
        
        text_lower = text.lower()
        cultural_count = sum(1 for term in cultural_terms if term in text_lower)
        
        if cultural_count > 3:
            return UncertaintyFactor(
                name="cultural_context",
                impact_level="low",
                impact_score=0.2,
                description=f"Rich K-Pop cultural context ({cultural_count} terms)",
                recommendation="High cultural relevance should improve analysis accuracy"
            )
        elif cultural_count > 0:
            return UncertaintyFactor(
                name="cultural_context",
                impact_level="low",
                impact_score=0.3,
                description=f"Some K-Pop cultural context present ({cultural_count} terms)"
            )
        else:
            return UncertaintyFactor(
                name="cultural_context",
                impact_level="medium",
                impact_score=0.5,
                description="Limited K-Pop cultural context, may affect accuracy",
                recommendation="Ensure text is relevant to K-Pop domain for best results"
            )

class AdvancedConfidenceCalculator:
    """Calculate comprehensive confidence scores with detailed breakdown"""
    
    def __init__(self):
        self.factor_weights = {
            'linguistic_confidence': 0.25,
            'pattern_confidence': 0.20,
            'context_confidence': 0.15,
            'language_support_confidence': 0.15,
            'text_quality_confidence': 0.15,
            'uncertainty_penalty': 0.10
        }
    
    def calculate_comprehensive_confidence(self, text: str, analysis_result: Dict, 
                                         language_info: Dict = None, 
                                         uncertainty_factors: List[UncertaintyFactor] = None) -> ConfidenceBreakdown:
        """Calculate comprehensive confidence with detailed breakdown"""
        
        # Calculate individual factor scores
        factor_scores = {}
        factor_scores['linguistic_confidence'] = self._calculate_linguistic_confidence(text, analysis_result)
        factor_scores['pattern_confidence'] = self._calculate_pattern_confidence(text, analysis_result)
        factor_scores['context_confidence'] = self._calculate_context_confidence(text)
        factor_scores['language_support_confidence'] = self._calculate_language_support_confidence(language_info)
        factor_scores['text_quality_confidence'] = self._calculate_text_quality_confidence(text)
        
        # Calculate uncertainty penalty
        uncertainty_penalty = self._calculate_uncertainty_penalty(uncertainty_factors or [])
        factor_scores['uncertainty_penalty'] = 1.0 - uncertainty_penalty
        
        # Calculate weighted overall confidence
        overall_confidence = sum(
            factor_scores[factor] * self.factor_weights[factor]
            for factor in factor_scores.keys()
        )
        
        # Generate explanations
        explanations = self._generate_confidence_explanations(factor_scores)
        
        # Assess reliability
        reliability = self._assess_reliability(overall_confidence, factor_scores, uncertainty_factors or [])
        
        # Create visual indicators
        visual_indicators = self._create_visual_indicators(overall_confidence, factor_scores)
        
        return ConfidenceBreakdown(
            overall_confidence=overall_confidence,
            factor_scores=factor_scores,
            uncertainty_factors=uncertainty_factors or [],
            reliability_assessment=reliability,
            explanation=explanations,
            visual_indicators=visual_indicators
        )
    
    def _calculate_linguistic_confidence(self, text: str, analysis_result: Dict) -> float:
        """Calculate confidence based on linguistic features"""
        base_confidence = analysis_result.get('confidence', 0.5)
        
        # Adjust based on text features
        word_count = len(text.split())
        if word_count < 5:
            return base_confidence * 0.7
        elif word_count > 100:
            return base_confidence * 0.9
        else:
            return base_confidence
    
    def _calculate_pattern_confidence(self, text: str, analysis_result: Dict) -> float:
        """Calculate confidence based on pattern matching"""
        # Count strong sentiment indicators
        strong_positive = ['amazing', 'incredible', 'perfect', 'love', 'best']
        strong_negative = ['hate', 'terrible', 'worst', 'awful']
        
        text_lower = text.lower()
        strong_indicators = sum(1 for word in strong_positive + strong_negative if word in text_lower)
        
        # More strong indicators = higher pattern confidence
        return min(0.5 + (strong_indicators * 0.2), 1.0)
    
    def _calculate_context_confidence(self, text: str) -> float:
        """Calculate confidence based on contextual clarity"""
        # Check for clear context indicators
        kpop_context = ['bts', 'blackpink', 'twice', 'kpop', 'idol', 'comeback', 'mv']
        text_lower = text.lower()
        context_score = sum(1 for term in kpop_context if term in text_lower)
        
        return min(0.3 + (context_score * 0.2), 1.0)
    
    def _calculate_language_support_confidence(self, language_info: Dict) -> float:
        """Calculate confidence based on language support"""
        if not language_info:
            return 0.7  # Default for unknown language info
        
        detection_confidence = language_info.get('confidence', 0.5)
        is_supported = language_info.get('supported', False)
        
        if is_supported:
            return detection_confidence
        else:
            return detection_confidence * 0.6  # Penalty for unsupported language
    
    def _calculate_text_quality_confidence(self, text: str) -> float:
        """Calculate confidence based on text quality"""
        # Check for quality indicators
        quality_score = 0.5
        
        # Proper capitalization
        if any(c.isupper() for c in text):
            quality_score += 0.1
        
        # Proper punctuation
        if any(p in text for p in '.!?'):
            quality_score += 0.1
        
        # Not all caps (shouting)
        if not text.isupper():
            quality_score += 0.1
        
        # Reasonable length
        word_count = len(text.split())
        if 5 <= word_count <= 50:
            quality_score += 0.2
        
        return min(quality_score, 1.0)
    
    def _calculate_uncertainty_penalty(self, uncertainty_factors: List[UncertaintyFactor]) -> float:
        """Calculate penalty based on uncertainty factors"""
        if not uncertainty_factors:
            return 0.0
        
        # Weight uncertainty factors by impact
        impact_weights = {'low': 0.1, 'medium': 0.3, 'high': 0.6, 'very_high': 0.9}
        
        total_penalty = 0.0
        for factor in uncertainty_factors:
            weight = impact_weights.get(factor.impact_level, 0.3)
            total_penalty += factor.impact_score * weight
        
        # Normalize penalty
        return min(total_penalty / len(uncertainty_factors), 0.8)
    
    def _generate_confidence_explanations(self, factor_scores: Dict[str, float]) -> List[str]:
        """Generate human-readable confidence explanations"""
        explanations = []
        
        for factor, score in factor_scores.items():
            factor_name = factor.replace('_', ' ').title()
            
            if score >= 0.8:
                level = "High"
                color = "🟢"
            elif score >= 0.6:
                level = "Medium"
                color = "🟡"
            elif score >= 0.4:
                level = "Low"
                color = "🟠"
            else:
                level = "Very Low"
                color = "🔴"
            
            explanations.append(f"{color} {factor_name}: {level} ({score:.1%})")
        
        return explanations
    
    def _assess_reliability(self, overall_confidence: float, factor_scores: Dict[str, float], 
                          uncertainty_factors: List[UncertaintyFactor]) -> str:
        """Assess overall reliability of the analysis"""
        high_uncertainty_count = sum(1 for f in uncertainty_factors if f.impact_level in ['high', 'very_high'])
        low_factor_count = sum(1 for score in factor_scores.values() if score < 0.5)
        
        if overall_confidence >= 0.8 and high_uncertainty_count == 0:
            return "High Reliability - Analysis is very trustworthy"
        elif overall_confidence >= 0.6 and high_uncertainty_count <= 1:
            return "Medium Reliability - Analysis is generally trustworthy"
        elif overall_confidence >= 0.4 or low_factor_count <= 2:
            return "Low Reliability - Use results with caution"
        else:
            return "Very Low Reliability - Results may be unreliable"
    
    def _create_visual_indicators(self, overall_confidence: float, factor_scores: Dict[str, float]) -> Dict[str, any]:
        """Create visual indicators for confidence display"""
        # Color coding
        if overall_confidence >= 0.8:
            color = "#28a745"  # Green
            status = "excellent"
        elif overall_confidence >= 0.6:
            color = "#ffc107"  # Yellow
            status = "good"
        elif overall_confidence >= 0.4:
            color = "#fd7e14"  # Orange
            status = "fair"
        else:
            color = "#dc3545"  # Red
            status = "poor"
        
        return {
            'color': color,
            'status': status,
            'gauge_value': overall_confidence,
            'factor_chart_data': factor_scores,
            'confidence_bar_width': f"{overall_confidence * 100}%"
        }

class AdvancedAnalyticsDashboard:
    """Generate comprehensive analytics reports and visualizations"""
    
    def __init__(self, db_path: str = 'sentiment_data.db'):
        self.db_path = db_path
    
    def generate_comprehensive_report(self, time_period: str = '7d') -> AnalyticsReport:
        """Generate comprehensive analytics report"""
        
        # Get data for the specified time period
        analyses = self._get_analyses_for_period(time_period)
        
        if not analyses:
            return self._empty_report()
        
        # Generate different sections of the report
        summary_stats = self._generate_summary_stats(analyses)
        trend_analysis = self._analyze_trends(analyses, time_period)
        quality_metrics = self._calculate_quality_metrics(analyses)
        language_distribution = self._analyze_language_distribution(analyses)
        uncertainty_patterns = self._analyze_uncertainty_patterns(analyses)
        risk_assessment = self._generate_risk_assessment(analyses)
        recommendations = self._generate_recommendations(analyses, summary_stats, quality_metrics)
        
        return AnalyticsReport(
            summary_stats=summary_stats,
            trend_analysis=trend_analysis,
            quality_metrics=quality_metrics,
            language_distribution=language_distribution,
            uncertainty_patterns=uncertainty_patterns,
            risk_assessment=risk_assessment,
            recommendations=recommendations,
            generated_at=datetime.now()
        )
    
    def _get_analyses_for_period(self, time_period: str) -> List[Dict]:
        """Get analyses for specified time period"""
        # Parse time period
        if time_period.endswith('d'):
            days = int(time_period[:-1])
        elif time_period.endswith('w'):
            days = int(time_period[:-1]) * 7
        elif time_period.endswith('m'):
            days = int(time_period[:-1]) * 30
        else:
            days = 7  # Default to 7 days
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM sentiment_analysis 
                WHERE timestamp > ? 
                ORDER BY timestamp DESC
            ''', (cutoff_date.isoformat(),))
            
            columns = [description[0] for description in cursor.description]
            analyses = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            conn.close()
            return analyses
            
        except Exception as e:
            print(f"Error fetching analyses: {e}")
            return []
    
    def _generate_summary_stats(self, analyses: List[Dict]) -> Dict[str, any]:
        """Generate summary statistics"""
        if not analyses:
            return {}
        
        confidences = [a['confidence'] for a in analyses]
        
        # Sentiment distribution
        sentiment_counts = Counter(a['label_name'] for a in analyses)
        
        # Risk distribution
        risk_counts = Counter(a['risk_level'] for a in analyses)
        
        # Confidence distribution
        confidence_ranges = {
            'very_high': sum(1 for c in confidences if c >= 0.8),
            'high': sum(1 for c in confidences if 0.6 <= c < 0.8),
            'medium': sum(1 for c in confidences if 0.4 <= c < 0.6),
            'low': sum(1 for c in confidences if c < 0.4)
        }
        
        return {
            'total_analyses': len(analyses),
            'average_confidence': np.mean(confidences),
            'median_confidence': np.median(confidences),
            'confidence_std': np.std(confidences),
            'sentiment_distribution': dict(sentiment_counts),
            'risk_distribution': dict(risk_counts),
            'confidence_ranges': confidence_ranges,
            'date_range': {
                'start': min(a['timestamp'] for a in analyses),
                'end': max(a['timestamp'] for a in analyses)
            }
        }
    
    def _analyze_trends(self, analyses: List[Dict], time_period: str) -> Dict[str, any]:
        """Analyze sentiment trends over time"""
        if not analyses:
            return {}
        
        # Group analyses by day
        daily_data = defaultdict(lambda: defaultdict(int))
        
        for analysis in analyses:
            date = analysis['timestamp'][:10]  # Extract date part
            sentiment = analysis['label_name']
            daily_data[date][sentiment] += 1
        
        # Calculate trends for each sentiment
        trends = {}
        for sentiment in set(a['label_name'] for a in analyses):
            daily_counts = [daily_data[date][sentiment] for date in sorted(daily_data.keys())]
            
            if len(daily_counts) > 1:
                # Simple trend calculation
                recent_avg = np.mean(daily_counts[-3:]) if len(daily_counts) >= 3 else daily_counts[-1]
                earlier_avg = np.mean(daily_counts[:3]) if len(daily_counts) >= 3 else daily_counts[0]
                
                if recent_avg > earlier_avg * 1.2:
                    trend_direction = 'increasing'
                elif recent_avg < earlier_avg * 0.8:
                    trend_direction = 'decreasing'
                else:
                    trend_direction = 'stable'
                
                trend_strength = abs(recent_avg - earlier_avg) / max(earlier_avg, 1)
            else:
                trend_direction = 'insufficient_data'
                trend_strength = 0
            
            trends[sentiment] = {
                'direction': trend_direction,
                'strength': trend_strength,
                'daily_counts': daily_counts,
                'volatility': np.std(daily_counts) if len(daily_counts) > 1 else 0
            }
        
        return {
            'daily_data': dict(daily_data),
            'sentiment_trends': trends,
            'overall_volume_trend': self._calculate_volume_trend(daily_data)
        }
    
    def _calculate_quality_metrics(self, analyses: List[Dict]) -> Dict[str, any]:
        """Calculate quality metrics"""
        if not analyses:
            return {}
        
        # Correction rate
        corrected_count = sum(1 for a in analyses if a.get('user_corrected_label'))
        correction_rate = corrected_count / len(analyses)
        
        # Verification rate
        verified_count = sum(1 for a in analyses if a.get('is_verified'))
        verification_rate = verified_count / len(analyses)
        
        # Low confidence rate
        low_confidence_count = sum(1 for a in analyses if a['confidence'] < 0.5)
        low_confidence_rate = low_confidence_count / len(analyses)
        
        # Average confidence by sentiment
        confidence_by_sentiment = {}
        for sentiment in set(a['label_name'] for a in analyses):
            sentiment_analyses = [a for a in analyses if a['label_name'] == sentiment]
            confidence_by_sentiment[sentiment] = np.mean([a['confidence'] for a in sentiment_analyses])
        
        return {
            'correction_rate': correction_rate,
            'verification_rate': verification_rate,
            'low_confidence_rate': low_confidence_rate,
            'average_confidence_by_sentiment': confidence_by_sentiment,
            'quality_score': self._calculate_overall_quality_score(analyses)
        }
    
    def _calculate_overall_quality_score(self, analyses: List[Dict]) -> float:
        """Calculate overall quality score"""
        if not analyses:
            return 0.0
        
        # Factors contributing to quality
        avg_confidence = np.mean([a['confidence'] for a in analyses])
        correction_rate = sum(1 for a in analyses if a.get('user_corrected_label')) / len(analyses)
        low_confidence_rate = sum(1 for a in analyses if a['confidence'] < 0.5) / len(analyses)
        
        # Quality score calculation
        quality_score = (
            avg_confidence * 0.5 +  # 50% weight on confidence
            (1 - correction_rate) * 0.3 +  # 30% weight on low correction rate
            (1 - low_confidence_rate) * 0.2  # 20% weight on low uncertainty rate
        )
        
        return quality_score
    
    def _analyze_language_distribution(self, analyses: List[Dict]) -> Dict[str, any]:
        """Analyze language distribution (placeholder for future implementation)"""
        # This would be implemented when language detection is added
        return {
            'supported_languages': ['en', 'ko', 'es'],
            'language_counts': {'en': len(analyses)},  # Placeholder
            'confidence_by_language': {'en': np.mean([a['confidence'] for a in analyses])}
        }
    
    def _analyze_uncertainty_patterns(self, analyses: List[Dict]) -> Dict[str, any]:
        """Analyze uncertainty patterns"""
        # This would analyze uncertainty factors when they're stored in the database
        return {
            'common_uncertainty_factors': ['text_length', 'mixed_signals'],
            'uncertainty_impact_distribution': {
                'low': 0.6,
                'medium': 0.3,
                'high': 0.1
            }
        }
    
    def _generate_risk_assessment(self, analyses: List[Dict]) -> Dict[str, any]:
        """Generate risk assessment"""
        if not analyses:
            return {}
        
        risk_counts = Counter(a['risk_level'] for a in analyses)
        total = len(analyses)
        
        # Calculate risk percentages
        risk_percentages = {level: count/total for level, count in risk_counts.items()}
        
        # Risk trend (simplified)
        high_risk_count = risk_counts.get('High', 0) + risk_counts.get('Very High', 0)
        risk_ratio = high_risk_count / total
        
        if risk_ratio > 0.2:
            risk_status = 'elevated'
        elif risk_ratio > 0.1:
            risk_status = 'moderate'
        else:
            risk_status = 'low'
        
        return {
            'risk_distribution': dict(risk_counts),
            'risk_percentages': risk_percentages,
            'overall_risk_status': risk_status,
            'high_risk_ratio': risk_ratio,
            'recommendations': self._generate_risk_recommendations(risk_status, risk_ratio)
        }
    
    def _generate_recommendations(self, analyses: List[Dict], summary_stats: Dict, quality_metrics: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Quality-based recommendations
        if quality_metrics.get('correction_rate', 0) > 0.2:
            recommendations.append("High correction rate detected. Consider reviewing and updating sentiment labels.")
        
        if quality_metrics.get('low_confidence_rate', 0) > 0.3:
            recommendations.append("Many analyses have low confidence. Consider improving keyword coverage or adding more training data.")
        
        # Volume-based recommendations
        if summary_stats.get('total_analyses', 0) < 50:
            recommendations.append("Low analysis volume. Consider collecting more data for better insights.")
        
        # Confidence-based recommendations
        avg_confidence = summary_stats.get('average_confidence', 0)
        if avg_confidence < 0.6:
            recommendations.append("Average confidence is low. Review and enhance the analysis model.")
        
        return recommendations
    
    def _generate_risk_recommendations(self, risk_status: str, risk_ratio: float) -> List[str]:
        """Generate risk-specific recommendations"""
        recommendations = []
        
        if risk_status == 'elevated':
            recommendations.append("High risk content detected. Increase monitoring and review processes.")
            recommendations.append("Consider implementing automated alerts for very high risk content.")
        elif risk_status == 'moderate':
            recommendations.append("Moderate risk levels. Maintain current monitoring practices.")
        
        return recommendations
    
    def _calculate_volume_trend(self, daily_data: Dict) -> Dict[str, any]:
        """Calculate overall volume trend"""
        daily_totals = [sum(day_data.values()) for day_data in daily_data.values()]
        
        if len(daily_totals) > 1:
            recent_avg = np.mean(daily_totals[-3:]) if len(daily_totals) >= 3 else daily_totals[-1]
            earlier_avg = np.mean(daily_totals[:3]) if len(daily_totals) >= 3 else daily_totals[0]
            
            if recent_avg > earlier_avg * 1.2:
                trend = 'increasing'
            elif recent_avg < earlier_avg * 0.8:
                trend = 'decreasing'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        return {
            'direction': trend,
            'daily_totals': daily_totals,
            'average_daily_volume': np.mean(daily_totals) if daily_totals else 0
        }
    
    def _empty_report(self) -> AnalyticsReport:
        """Return empty report when no data is available"""
        return AnalyticsReport(
            summary_stats={},
            trend_analysis={},
            quality_metrics={},
            language_distribution={},
            uncertainty_patterns={},
            risk_assessment={},
            recommendations=["No data available for analysis. Start by analyzing some K-Pop content."],
            generated_at=datetime.now()
        )

# Example usage
if __name__ == "__main__":
    # Test uncertainty analysis
    uncertainty_analyzer = UncertaintyAnalyzer()
    confidence_calculator = AdvancedConfidenceCalculator()
    
    test_text = "I think this song is kind of okay but maybe not their best work"
    test_analysis = {'confidence': 0.6, 'label_name': 'MIXED_CONFLICTED'}
    
    # Analyze uncertainty
    uncertainty_factors = uncertainty_analyzer.analyze_uncertainty_factors(test_text, test_analysis)
    
    print("Uncertainty Factors:")
    for factor in uncertainty_factors:
        print(f"- {factor.name}: {factor.impact_level} impact ({factor.impact_score:.2f})")
        print(f"  {factor.description}")
        if factor.recommendation:
            print(f"  Recommendation: {factor.recommendation}")
        print()
    
    # Calculate comprehensive confidence
    confidence_breakdown = confidence_calculator.calculate_comprehensive_confidence(
        test_text, test_analysis, uncertainty_factors=uncertainty_factors
    )
    
    print(f"Overall Confidence: {confidence_breakdown.overall_confidence:.2%}")
    print(f"Reliability: {confidence_breakdown.reliability_assessment}")
    print("\nFactor Breakdown:")
    for explanation in confidence_breakdown.explanation:
        print(f"  {explanation}")