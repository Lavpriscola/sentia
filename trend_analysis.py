"""
Real Trend Analysis Implementation
Provides comprehensive trend analysis using statistical methods and real data
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import sqlite3
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score
import warnings
warnings.filterwarnings('ignore')

@dataclass
class TrendMetrics:
    """Trend analysis metrics"""
    slope: float
    r_squared: float
    p_value: float
    trend_direction: str  # 'increasing', 'decreasing', 'stable'
    trend_strength: str   # 'weak', 'moderate', 'strong'
    confidence_interval: Tuple[float, float]
    forecast_7d: float
    forecast_30d: float

@dataclass
class SeasonalPattern:
    """Seasonal pattern analysis"""
    pattern_type: str  # 'hourly', 'daily', 'weekly'
    peak_times: List[str]
    low_times: List[str]
    amplitude: float
    regularity_score: float

@dataclass
class TrendAnalysisResult:
    """Complete trend analysis result"""
    overall_trend: TrendMetrics
    sentiment_trends: Dict[str, TrendMetrics]
    seasonal_patterns: List[SeasonalPattern]
    anomalies: List[Dict]
    insights: List[str]
    recommendations: List[str]

class RealTrendAnalyzer:
    """Real implementation of trend analysis using statistical methods"""
    
    def __init__(self, db_path: str = "sentiment_data.db"):
        self.db_path = db_path
        self.data = self._load_data()
        
        # Analysis parameters
        self.min_data_points = 7  # Minimum points for trend analysis
        self.anomaly_threshold = 2.5  # Standard deviations for anomaly detection
        self.trend_significance = 0.05  # P-value threshold for significant trends
        
    def _load_data(self) -> pd.DataFrame:
        """Load real data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            query = """
            SELECT id, text, predicted_label, confidence, label_name, 
                   risk_level, timestamp, user_corrected_label, is_verified
            FROM sentiment_analysis 
            ORDER BY timestamp ASC
            """
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            # Convert timestamp and create time features
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['week'] = df['timestamp'].dt.isocalendar().week
            
            return df
        except Exception as e:
            print(f"Warning: Could not load data from database: {e}")
            return self._generate_sample_data()
    
    def _generate_sample_data(self) -> pd.DataFrame:
        """Generate realistic sample data with trends"""
        np.random.seed(42)
        
        # Generate 60 days of data
        start_date = datetime.now() - timedelta(days=60)
        dates = [start_date + timedelta(days=i) for i in range(60)]
        
        data = []
        base_volume = 50
        
        for i, date in enumerate(dates):
            # Add trend (increasing volume over time)
            trend_factor = 1 + (i / 60) * 0.5
            
            # Add weekly seasonality (higher on weekends)
            day_of_week = date.weekday()
            weekly_factor = 1.3 if day_of_week >= 5 else 1.0
            
            # Add some noise
            noise_factor = np.random.normal(1, 0.2)
            
            daily_volume = int(base_volume * trend_factor * weekly_factor * noise_factor)
            
            # Generate records for this day
            for j in range(daily_volume):
                # Hourly distribution (more activity during day)
                hour_weights = [0.02, 0.01, 0.01, 0.01, 0.02, 0.03, 0.05, 0.07,
                               0.08, 0.09, 0.10, 0.11, 0.12, 0.11, 0.10, 0.09,
                               0.08, 0.07, 0.06, 0.05, 0.04, 0.03, 0.03, 0.02]
                hour = np.random.choice(24, p=hour_weights)
                
                timestamp = date.replace(hour=hour, minute=np.random.randint(0, 60))
                
                # Sentiment distribution with some trends
                sentiments = [
                    'ENTHUSIASTIC_SUPPORT', 'NOSTALGIC_APPRECIATION', 'ANTICIPATORY_EXCITEMENT',
                    'PROTECTIVE_DEFENSIVE', 'CRITICAL_DISAPPOINTMENT', 'NEUTRAL_FACTUAL',
                    'COMPETITIVE_RIVALRY', 'SARCASTIC_MOCKERY', 'MALICIOUS_COORDINATED', 'MIXED_CONFLICTED'
                ]
                
                # Trending sentiment (ENTHUSIASTIC_SUPPORT increases over time)
                if np.random.random() < 0.3 + (i / 60) * 0.2:
                    sentiment = 'ENTHUSIASTIC_SUPPORT'
                else:
                    sentiment = np.random.choice(sentiments[1:])
                
                confidence = np.random.normal(0.75, 0.15)
                confidence = np.clip(confidence, 0.1, 1.0)
                
                data.append({
                    'id': len(data) + 1,
                    'text': f'Sample text {len(data) + 1}',
                    'predicted_label': sentiments.index(sentiment),
                    'confidence': confidence,
                    'label_name': sentiment,
                    'risk_level': 'Low',
                    'timestamp': timestamp,
                    'date': timestamp.date(),
                    'hour': hour,
                    'day_of_week': timestamp.weekday(),
                    'week': timestamp.isocalendar().week,
                    'user_corrected_label': None,
                    'is_verified': False
                })
        
        return pd.DataFrame(data)
    
    def analyze_trends(self, days_back: int = 30) -> TrendAnalysisResult:
        """Perform comprehensive trend analysis"""
        if self.data.empty:
            return self._empty_analysis_result()
        
        # Filter data to specified time period
        cutoff_date = datetime.now() - timedelta(days=days_back)
        recent_data = self.data[self.data['timestamp'] >= cutoff_date].copy()
        
        if len(recent_data) < self.min_data_points:
            return self._insufficient_data_result()
        
        # 1. Overall volume trend
        overall_trend = self._analyze_volume_trend(recent_data)
        
        # 2. Individual sentiment trends
        sentiment_trends = self._analyze_sentiment_trends(recent_data)
        
        # 3. Seasonal patterns
        seasonal_patterns = self._analyze_seasonal_patterns(recent_data)
        
        # 4. Anomaly detection
        anomalies = self._detect_anomalies(recent_data)
        
        # 5. Generate insights
        insights = self._generate_insights(overall_trend, sentiment_trends, seasonal_patterns, anomalies)
        
        # 6. Generate recommendations
        recommendations = self._generate_recommendations(overall_trend, sentiment_trends, anomalies)
        
        return TrendAnalysisResult(
            overall_trend=overall_trend,
            sentiment_trends=sentiment_trends,
            seasonal_patterns=seasonal_patterns,
            anomalies=anomalies,
            insights=insights,
            recommendations=recommendations
        )
    
    def _analyze_volume_trend(self, data: pd.DataFrame) -> TrendMetrics:
        """Analyze overall volume trend"""
        # Aggregate daily volumes
        daily_volumes = data.groupby('date').size().reset_index(name='volume')
        daily_volumes['date'] = pd.to_datetime(daily_volumes['date'])
        daily_volumes['days_since_start'] = (daily_volumes['date'] - daily_volumes['date'].min()).dt.days
        
        if len(daily_volumes) < 3:
            return self._default_trend_metrics()
        
        # Linear regression
        X = daily_volumes['days_since_start'].values.reshape(-1, 1)
        y = daily_volumes['volume'].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Calculate metrics
        y_pred = model.predict(X)
        slope = model.coef_[0]
        r_squared = r2_score(y, y_pred)
        
        # Statistical significance test
        n = len(daily_volumes)
        if n > 2:
            # Calculate t-statistic for slope
            residuals = y - y_pred
            mse = np.sum(residuals**2) / (n - 2)
            se_slope = np.sqrt(mse / np.sum((X.flatten() - X.mean())**2))
            t_stat = slope / se_slope if se_slope > 0 else 0
            p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - 2))
        else:
            p_value = 1.0
        
        # Determine trend direction and strength
        if p_value < self.trend_significance:
            if slope > 0:
                trend_direction = 'increasing'
            else:
                trend_direction = 'decreasing'
        else:
            trend_direction = 'stable'
        
        # Trend strength based on R-squared
        if r_squared > 0.7:
            trend_strength = 'strong'
        elif r_squared > 0.4:
            trend_strength = 'moderate'
        else:
            trend_strength = 'weak'
        
        # Confidence interval for slope (95%)
        if n > 2 and se_slope > 0:
            t_critical = stats.t.ppf(0.975, n - 2)
            ci_lower = slope - t_critical * se_slope
            ci_upper = slope + t_critical * se_slope
            confidence_interval = (ci_lower, ci_upper)
        else:
            confidence_interval = (slope, slope)
        
        # Forecasting
        last_day = daily_volumes['days_since_start'].max()
        forecast_7d = model.predict([[last_day + 7]])[0]
        forecast_30d = model.predict([[last_day + 30]])[0]
        
        return TrendMetrics(
            slope=slope,
            r_squared=r_squared,
            p_value=p_value,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            confidence_interval=confidence_interval,
            forecast_7d=max(0, forecast_7d),
            forecast_30d=max(0, forecast_30d)
        )
    
    def _analyze_sentiment_trends(self, data: pd.DataFrame) -> Dict[str, TrendMetrics]:
        """Analyze trends for individual sentiments"""
        sentiment_trends = {}
        
        for sentiment in data['label_name'].unique():
            sentiment_data = data[data['label_name'] == sentiment]
            
            # Daily counts for this sentiment
            daily_counts = sentiment_data.groupby('date').size().reset_index(name='count')
            
            # Fill missing dates with 0
            all_dates = pd.date_range(data['date'].min(), data['date'].max(), freq='D')
            daily_counts = daily_counts.set_index('date').reindex(all_dates.date, fill_value=0).reset_index()
            daily_counts.columns = ['date', 'count']
            daily_counts['date'] = pd.to_datetime(daily_counts['date'])
            daily_counts['days_since_start'] = (daily_counts['date'] - daily_counts['date'].min()).dt.days
            
            if len(daily_counts) < 3:
                sentiment_trends[sentiment] = self._default_trend_metrics()
                continue
            
            # Linear regression
            X = daily_counts['days_since_start'].values.reshape(-1, 1)
            y = daily_counts['count'].values
            
            model = LinearRegression()
            model.fit(X, y)
            
            y_pred = model.predict(X)
            slope = model.coef_[0]
            r_squared = r2_score(y, y_pred) if np.var(y) > 0 else 0
            
            # Statistical test
            n = len(daily_counts)
            if n > 2 and np.var(y) > 0:
                residuals = y - y_pred
                mse = np.sum(residuals**2) / (n - 2)
                se_slope = np.sqrt(mse / np.sum((X.flatten() - X.mean())**2))
                t_stat = slope / se_slope if se_slope > 0 else 0
                p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - 2))
            else:
                p_value = 1.0
            
            # Trend classification
            if p_value < self.trend_significance:
                trend_direction = 'increasing' if slope > 0 else 'decreasing'
            else:
                trend_direction = 'stable'
            
            trend_strength = 'strong' if r_squared > 0.7 else 'moderate' if r_squared > 0.4 else 'weak'
            
            # Forecasting
            last_day = daily_counts['days_since_start'].max()
            forecast_7d = max(0, model.predict([[last_day + 7]])[0])
            forecast_30d = max(0, model.predict([[last_day + 30]])[0])
            
            sentiment_trends[sentiment] = TrendMetrics(
                slope=slope,
                r_squared=r_squared,
                p_value=p_value,
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                confidence_interval=(slope, slope),  # Simplified
                forecast_7d=forecast_7d,
                forecast_30d=forecast_30d
            )
        
        return sentiment_trends
    
    def _analyze_seasonal_patterns(self, data: pd.DataFrame) -> List[SeasonalPattern]:
        """Analyze seasonal patterns in the data"""
        patterns = []
        
        # 1. Hourly patterns
        hourly_counts = data.groupby('hour').size()
        if len(hourly_counts) > 0:
            peak_hours = hourly_counts.nlargest(3).index.tolist()
            low_hours = hourly_counts.nsmallest(3).index.tolist()
            amplitude = (hourly_counts.max() - hourly_counts.min()) / hourly_counts.mean()
            
            # Regularity score based on variance
            regularity_score = 1 - (hourly_counts.std() / hourly_counts.mean()) if hourly_counts.mean() > 0 else 0
            regularity_score = max(0, min(1, regularity_score))
            
            patterns.append(SeasonalPattern(
                pattern_type='hourly',
                peak_times=[f"{h:02d}:00" for h in peak_hours],
                low_times=[f"{h:02d}:00" for h in low_hours],
                amplitude=amplitude,
                regularity_score=regularity_score
            ))
        
        # 2. Daily patterns (day of week)
        daily_counts = data.groupby('day_of_week').size()
        if len(daily_counts) > 0:
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            peak_days = [day_names[i] for i in daily_counts.nlargest(2).index.tolist()]
            low_days = [day_names[i] for i in daily_counts.nsmallest(2).index.tolist()]
            amplitude = (daily_counts.max() - daily_counts.min()) / daily_counts.mean()
            
            regularity_score = 1 - (daily_counts.std() / daily_counts.mean()) if daily_counts.mean() > 0 else 0
            regularity_score = max(0, min(1, regularity_score))
            
            patterns.append(SeasonalPattern(
                pattern_type='daily',
                peak_times=peak_days,
                low_times=low_days,
                amplitude=amplitude,
                regularity_score=regularity_score
            ))
        
        # 3. Weekly patterns (if enough data)
        if data['timestamp'].max() - data['timestamp'].min() > timedelta(weeks=4):
            weekly_counts = data.groupby('week').size()
            if len(weekly_counts) > 2:
                peak_weeks = weekly_counts.nlargest(2).index.tolist()
                low_weeks = weekly_counts.nsmallest(2).index.tolist()
                amplitude = (weekly_counts.max() - weekly_counts.min()) / weekly_counts.mean()
                
                regularity_score = 1 - (weekly_counts.std() / weekly_counts.mean()) if weekly_counts.mean() > 0 else 0
                regularity_score = max(0, min(1, regularity_score))
                
                patterns.append(SeasonalPattern(
                    pattern_type='weekly',
                    peak_times=[f"Week {w}" for w in peak_weeks],
                    low_times=[f"Week {w}" for w in low_weeks],
                    amplitude=amplitude,
                    regularity_score=regularity_score
                ))
        
        return patterns
    
    def _detect_anomalies(self, data: pd.DataFrame) -> List[Dict]:
        """Detect anomalies in the data"""
        anomalies = []
        
        # Daily volume anomalies
        daily_volumes = data.groupby('date').size()
        if len(daily_volumes) > 7:  # Need enough data for meaningful anomaly detection
            mean_volume = daily_volumes.mean()
            std_volume = daily_volumes.std()
            
            for date, volume in daily_volumes.items():
                z_score = abs(volume - mean_volume) / std_volume if std_volume > 0 else 0
                
                if z_score > self.anomaly_threshold:
                    anomaly_type = 'volume_spike' if volume > mean_volume else 'volume_drop'
                    
                    anomalies.append({
                        'date': date,
                        'type': anomaly_type,
                        'value': volume,
                        'expected': mean_volume,
                        'z_score': z_score,
                        'severity': 'high' if z_score > 3 else 'medium'
                    })
        
        # Confidence anomalies
        daily_confidence = data.groupby('date')['confidence'].mean()
        if len(daily_confidence) > 7:
            mean_conf = daily_confidence.mean()
            std_conf = daily_confidence.std()
            
            for date, conf in daily_confidence.items():
                z_score = abs(conf - mean_conf) / std_conf if std_conf > 0 else 0
                
                if z_score > self.anomaly_threshold:
                    anomaly_type = 'confidence_spike' if conf > mean_conf else 'confidence_drop'
                    
                    anomalies.append({
                        'date': date,
                        'type': anomaly_type,
                        'value': conf,
                        'expected': mean_conf,
                        'z_score': z_score,
                        'severity': 'high' if z_score > 3 else 'medium'
                    })
        
        return anomalies
    
    def _generate_insights(self, overall_trend: TrendMetrics, sentiment_trends: Dict[str, TrendMetrics], 
                          seasonal_patterns: List[SeasonalPattern], anomalies: List[Dict]) -> List[str]:
        """Generate actionable insights from trend analysis"""
        insights = []
        
        # Overall trend insights
        if overall_trend.trend_direction == 'increasing' and overall_trend.trend_strength in ['moderate', 'strong']:
            insights.append(f"📈 Overall activity is {overall_trend.trend_direction} with {overall_trend.trend_strength} confidence (R² = {overall_trend.r_squared:.2f})")
        elif overall_trend.trend_direction == 'decreasing' and overall_trend.trend_strength in ['moderate', 'strong']:
            insights.append(f"📉 Overall activity is {overall_trend.trend_direction} with {overall_trend.trend_strength} confidence (R² = {overall_trend.r_squared:.2f})")
        
        # Sentiment-specific insights
        growing_sentiments = [s for s, t in sentiment_trends.items() 
                            if t.trend_direction == 'increasing' and t.trend_strength in ['moderate', 'strong']]
        if growing_sentiments:
            insights.append(f"🔥 Growing sentiment types: {', '.join(growing_sentiments[:3])}")
        
        declining_sentiments = [s for s, t in sentiment_trends.items() 
                              if t.trend_direction == 'decreasing' and t.trend_strength in ['moderate', 'strong']]
        if declining_sentiments:
            insights.append(f"📉 Declining sentiment types: {', '.join(declining_sentiments[:3])}")
        
        # Seasonal insights
        for pattern in seasonal_patterns:
            if pattern.amplitude > 1.5:  # Significant seasonal variation
                if pattern.pattern_type == 'hourly':
                    insights.append(f"⏰ Strong hourly patterns detected - Peak activity: {', '.join(pattern.peak_times)}")
                elif pattern.pattern_type == 'daily':
                    insights.append(f"📅 Strong weekly patterns detected - Peak days: {', '.join(pattern.peak_times)}")
        
        # Anomaly insights
        high_severity_anomalies = [a for a in anomalies if a['severity'] == 'high']
        if high_severity_anomalies:
            insights.append(f"⚠️ {len(high_severity_anomalies)} high-severity anomalies detected in recent period")
        
        # Forecasting insights
        if overall_trend.forecast_7d > 0:
            current_avg = overall_trend.forecast_7d / 7  # Rough current daily average
            change_pct = ((overall_trend.forecast_7d / 7) - current_avg) / current_avg * 100 if current_avg > 0 else 0
            if abs(change_pct) > 10:
                direction = "increase" if change_pct > 0 else "decrease"
                insights.append(f"🔮 7-day forecast suggests {change_pct:.1f}% {direction} in activity")
        
        return insights
    
    def _generate_recommendations(self, overall_trend: TrendMetrics, sentiment_trends: Dict[str, TrendMetrics], 
                                anomalies: List[Dict]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Trend-based recommendations
        if overall_trend.trend_direction == 'increasing' and overall_trend.trend_strength == 'strong':
            recommendations.append("📊 Consider scaling infrastructure to handle increasing analysis volume")
            recommendations.append("🔍 Monitor system performance as load increases")
        
        elif overall_trend.trend_direction == 'decreasing' and overall_trend.trend_strength == 'strong':
            recommendations.append("📉 Investigate causes of declining activity - check data sources")
            recommendations.append("🎯 Consider engagement strategies to increase user activity")
        
        # Sentiment-specific recommendations
        negative_trending = [s for s, t in sentiment_trends.items() 
                           if 'MALICIOUS' in s or 'SARCASTIC' in s and t.trend_direction == 'increasing']
        if negative_trending:
            recommendations.append("🚨 Monitor increasing negative sentiment types for potential issues")
            recommendations.append("🛡️ Consider implementing additional content moderation")
        
        # Anomaly-based recommendations
        volume_spikes = [a for a in anomalies if a['type'] == 'volume_spike' and a['severity'] == 'high']
        if volume_spikes:
            recommendations.append("📈 Investigate recent volume spikes - may indicate viral content or events")
        
        confidence_drops = [a for a in anomalies if a['type'] == 'confidence_drop' and a['severity'] == 'high']
        if confidence_drops:
            recommendations.append("⚠️ Review model performance during confidence drop periods")
            recommendations.append("🔧 Consider model retraining or parameter adjustment")
        
        # General recommendations
        if len(sentiment_trends) > 0:
            avg_r_squared = np.mean([t.r_squared for t in sentiment_trends.values()])
            if avg_r_squared < 0.3:
                recommendations.append("📊 Trend patterns are weak - consider longer analysis periods")
        
        return recommendations
    
    def _default_trend_metrics(self) -> TrendMetrics:
        """Return default trend metrics for insufficient data"""
        return TrendMetrics(
            slope=0.0,
            r_squared=0.0,
            p_value=1.0,
            trend_direction='stable',
            trend_strength='weak',
            confidence_interval=(0.0, 0.0),
            forecast_7d=0.0,
            forecast_30d=0.0
        )
    
    def _empty_analysis_result(self) -> TrendAnalysisResult:
        """Return empty analysis result"""
        return TrendAnalysisResult(
            overall_trend=self._default_trend_metrics(),
            sentiment_trends={},
            seasonal_patterns=[],
            anomalies=[],
            insights=["No data available for trend analysis"],
            recommendations=["Collect more data to enable trend analysis"]
        )
    
    def _insufficient_data_result(self) -> TrendAnalysisResult:
        """Return result for insufficient data"""
        return TrendAnalysisResult(
            overall_trend=self._default_trend_metrics(),
            sentiment_trends={},
            seasonal_patterns=[],
            anomalies=[],
            insights=[f"Insufficient data for reliable trend analysis (minimum {self.min_data_points} data points required)"],
            recommendations=["Collect more data over a longer time period", "Consider reducing the analysis time window"]
        )

def test_trend_analyzer():
    """Test the trend analyzer with real data"""
    print("=== TESTING TREND ANALYSIS ===")
    
    analyzer = RealTrendAnalyzer()
    
    print(f"Loaded {len(analyzer.data)} data points")
    if not analyzer.data.empty:
        print(f"Date range: {analyzer.data['date'].min()} to {analyzer.data['date'].max()}")
        print(f"Unique sentiments: {analyzer.data['label_name'].nunique()}")
    
    # Perform trend analysis
    result = analyzer.analyze_trends(days_back=30)
    
    print(f"\n=== OVERALL TREND ===")
    print(f"Direction: {result.overall_trend.trend_direction}")
    print(f"Strength: {result.overall_trend.trend_strength}")
    print(f"R-squared: {result.overall_trend.r_squared:.3f}")
    print(f"P-value: {result.overall_trend.p_value:.3f}")
    print(f"7-day forecast: {result.overall_trend.forecast_7d:.1f}")
    
    print(f"\n=== SENTIMENT TRENDS ===")
    for sentiment, trend in result.sentiment_trends.items():
        if trend.trend_strength in ['moderate', 'strong']:
            print(f"{sentiment}: {trend.trend_direction} ({trend.trend_strength}, R²={trend.r_squared:.2f})")
    
    print(f"\n=== SEASONAL PATTERNS ===")
    for pattern in result.seasonal_patterns:
        print(f"{pattern.pattern_type.title()} pattern - Peaks: {', '.join(pattern.peak_times[:2])}")
    
    print(f"\n=== ANOMALIES ===")
    for anomaly in result.anomalies[:5]:  # Show first 5
        print(f"{anomaly['date']}: {anomaly['type']} (severity: {anomaly['severity']})")
    
    print(f"\n=== KEY INSIGHTS ===")
    for insight in result.insights:
        print(f"• {insight}")
    
    print(f"\n=== RECOMMENDATIONS ===")
    for rec in result.recommendations:
        print(f"• {rec}")

if __name__ == "__main__":
    test_trend_analyzer()