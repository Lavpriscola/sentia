"""
Enhanced Visualizations for K-Pop Sentiment Analysis
Provides interactive charts, confidence gauges, and uncertainty visualizations
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Wedge
import seaborn as sns
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import json

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.figure_factory as ff
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Set style for better-looking plots
plt.style.use('dark_background')
sns.set_palette("husl")

class ConfidenceVisualizer:
    """Create visual representations of confidence and uncertainty"""
    
    def __init__(self, style='dark'):
        self.style = style
        self.colors = self._get_color_scheme()
    
    def _get_color_scheme(self):
        """Get color scheme based on style"""
        if self.style == 'dark':
            return {
                'background': '#2b2b2b',
                'text': '#ffffff',
                'high_confidence': '#28a745',
                'medium_confidence': '#ffc107',
                'low_confidence': '#fd7e14',
                'very_low_confidence': '#dc3545',
                'uncertainty': '#6c757d'
            }
        else:
            return {
                'background': '#ffffff',
                'text': '#000000',
                'high_confidence': '#28a745',
                'medium_confidence': '#ffc107',
                'low_confidence': '#fd7e14',
                'very_low_confidence': '#dc3545',
                'uncertainty': '#6c757d'
            }
    
    def create_confidence_gauge(self, confidence: float, uncertainty_factors: List = None, 
                               title: str = "Confidence Level") -> plt.Figure:
        """Create a speedometer-style confidence gauge"""
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor(self.colors['background'])
        ax.set_facecolor(self.colors['background'])
        
        # Create gauge background
        theta = np.linspace(0, np.pi, 100)
        r = np.ones_like(theta)
        
        # Background arc
        ax.plot(theta, r, color=self.colors['text'], linewidth=3)
        ax.fill_between(theta, 0, r, alpha=0.1, color=self.colors['text'])
        
        # Confidence zones
        zones = [
            (0, 0.4, self.colors['very_low_confidence'], 'Very Low'),
            (0.4, 0.6, self.colors['low_confidence'], 'Low'),
            (0.6, 0.8, self.colors['medium_confidence'], 'Medium'),
            (0.8, 1.0, self.colors['high_confidence'], 'High')
        ]
        
        for start, end, color, label in zones:
            zone_theta = theta[int(start*100):int(end*100)]
            zone_r = r[int(start*100):int(end*100)]
            ax.fill_between(zone_theta, 0, zone_r, alpha=0.3, color=color, label=label)
        
        # Confidence needle
        needle_angle = confidence * np.pi
        needle_x = [needle_angle, needle_angle]
        needle_y = [0, 0.9]
        ax.plot(needle_x, needle_y, color=self.colors['text'], linewidth=4)
        
        # Needle tip
        ax.plot(needle_angle, 0.9, 'o', color=self.colors['text'], markersize=8)
        
        # Center circle
        center_circle = plt.Circle((np.pi/2, 0), 0.1, color=self.colors['text'])
        ax.add_patch(center_circle)
        
        # Labels and formatting
        ax.set_xlim(0, np.pi)
        ax.set_ylim(0, 1.2)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Title and confidence value
        ax.text(np.pi/2, 1.1, title, ha='center', va='center', 
                fontsize=16, fontweight='bold', color=self.colors['text'])
        ax.text(np.pi/2, 0.5, f'{confidence:.1%}', ha='center', va='center',
                fontsize=24, fontweight='bold', color=self.colors['text'])
        
        # Zone labels
        zone_positions = [0.2, 0.5, 0.7, 0.9]
        zone_labels = ['Very Low', 'Low', 'Medium', 'High']
        for pos, label in zip(zone_positions, zone_labels):
            angle = pos * np.pi
            ax.text(angle, 1.05, label, ha='center', va='center',
                   fontsize=10, color=self.colors['text'], rotation=0)
        
        # Uncertainty indicators
        if uncertainty_factors:
            self._add_uncertainty_indicators(ax, uncertainty_factors)
        
        plt.tight_layout()
        return fig
    
    def _add_uncertainty_indicators(self, ax, uncertainty_factors):
        """Add uncertainty indicators to the gauge"""
        high_uncertainty = [f for f in uncertainty_factors if f.impact_level in ['high', 'very_high']]
        
        if high_uncertainty:
            # Add warning indicators
            for i, factor in enumerate(high_uncertainty[:3]):  # Show max 3
                y_pos = -0.2 - (i * 0.1)
                ax.text(np.pi/2, y_pos, f"⚠️ {factor.name.replace('_', ' ').title()}", 
                       ha='center', va='center', fontsize=10, 
                       color=self.colors['very_low_confidence'])
    
    def create_factor_breakdown_chart(self, factor_scores: Dict[str, float]) -> plt.Figure:
        """Create horizontal bar chart showing confidence factor breakdown"""
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor(self.colors['background'])
        ax.set_facecolor(self.colors['background'])
        
        # Prepare data
        factors = list(factor_scores.keys())
        scores = list(factor_scores.values())
        
        # Clean factor names
        clean_factors = [f.replace('_', ' ').title() for f in factors]
        
        # Color bars based on score
        colors = []
        for score in scores:
            if score >= 0.8:
                colors.append(self.colors['high_confidence'])
            elif score >= 0.6:
                colors.append(self.colors['medium_confidence'])
            elif score >= 0.4:
                colors.append(self.colors['low_confidence'])
            else:
                colors.append(self.colors['very_low_confidence'])
        
        # Create horizontal bar chart
        bars = ax.barh(clean_factors, scores, color=colors, alpha=0.8)
        
        # Add value labels on bars
        for bar, score in zip(bars, scores):
            width = bar.get_width()
            ax.text(width + 0.01, bar.get_y() + bar.get_height()/2, 
                   f'{score:.2f}', ha='left', va='center', 
                   color=self.colors['text'], fontweight='bold')
        
        # Formatting
        ax.set_xlim(0, 1.1)
        ax.set_xlabel('Confidence Score', color=self.colors['text'], fontsize=12)
        ax.set_title('Confidence Factor Breakdown', color=self.colors['text'], 
                    fontsize=14, fontweight='bold')
        ax.tick_params(colors=self.colors['text'])
        ax.spines['bottom'].set_color(self.colors['text'])
        ax.spines['left'].set_color(self.colors['text'])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Add reference lines
        for threshold in [0.4, 0.6, 0.8]:
            ax.axvline(x=threshold, color=self.colors['text'], linestyle='--', alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def create_uncertainty_heatmap(self, uncertainty_factors: List) -> plt.Figure:
        """Create heatmap showing uncertainty factors and their impacts"""
        if not uncertainty_factors:
            return self._create_no_uncertainty_chart()
        
        fig, ax = plt.subplots(figsize=(12, 6))
        fig.patch.set_facecolor(self.colors['background'])
        
        # Prepare data
        factor_names = [f.name.replace('_', ' ').title() for f in uncertainty_factors]
        impact_levels = [f.impact_level for f in uncertainty_factors]
        impact_scores = [f.impact_score for f in uncertainty_factors]
        
        # Create impact level mapping
        level_mapping = {'low': 1, 'medium': 2, 'high': 3, 'very_high': 4}
        impact_values = [level_mapping.get(level, 1) for level in impact_levels]
        
        # Create heatmap data
        heatmap_data = np.array([impact_values])
        
        # Create heatmap
        im = ax.imshow(heatmap_data, cmap='Reds', aspect='auto', alpha=0.8)
        
        # Set ticks and labels
        ax.set_xticks(range(len(factor_names)))
        ax.set_xticklabels(factor_names, rotation=45, ha='right', color=self.colors['text'])
        ax.set_yticks([0])
        ax.set_yticklabels(['Uncertainty Impact'], color=self.colors['text'])
        
        # Add text annotations
        for i, (score, level) in enumerate(zip(impact_scores, impact_levels)):
            ax.text(i, 0, f'{score:.2f}\n({level})', ha='center', va='center',
                   color='white', fontweight='bold', fontsize=10)
        
        # Title and formatting
        ax.set_title('Uncertainty Factor Analysis', color=self.colors['text'],
                    fontsize=14, fontweight='bold', pad=20)
        
        # Remove spines
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        plt.tight_layout()
        return fig
    
    def _create_no_uncertainty_chart(self) -> plt.Figure:
        """Create chart when no uncertainty factors are present"""
        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor(self.colors['background'])
        ax.set_facecolor(self.colors['background'])
        
        ax.text(0.5, 0.5, '✅ No Significant Uncertainty Factors Detected', 
               ha='center', va='center', fontsize=16, color=self.colors['high_confidence'],
               fontweight='bold', transform=ax.transAxes)
        
        ax.text(0.5, 0.3, 'Analysis appears reliable with minimal uncertainty', 
               ha='center', va='center', fontsize=12, color=self.colors['text'],
               transform=ax.transAxes)
        
        ax.axis('off')
        return fig

class InteractiveDashboard:
    """Create interactive dashboards using Plotly (if available)"""
    
    def __init__(self):
        self.available = PLOTLY_AVAILABLE
    
    def create_comprehensive_dashboard(self, analysis_result: Dict, 
                                     confidence_breakdown: Dict,
                                     uncertainty_factors: List) -> Optional[go.Figure]:
        """Create comprehensive interactive dashboard"""
        if not self.available:
            return None
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Confidence Gauge', 'Factor Breakdown', 
                          'Uncertainty Analysis', 'Analysis Summary'),
            specs=[[{"type": "indicator"}, {"type": "bar"}],
                   [{"type": "heatmap"}, {"type": "table"}]]
        )
        
        # Confidence gauge
        confidence = confidence_breakdown.get('overall_confidence', 0.5)
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=confidence,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Overall Confidence"},
                gauge={
                    'axis': {'range': [None, 1]},
                    'bar': {'color': self._get_gauge_color(confidence)},
                    'steps': [
                        {'range': [0, 0.4], 'color': "lightgray"},
                        {'range': [0.4, 0.6], 'color': "yellow"},
                        {'range': [0.6, 0.8], 'color': "orange"},
                        {'range': [0.8, 1], 'color': "lightgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 0.9
                    }
                }
            ),
            row=1, col=1
        )
        
        # Factor breakdown
        factor_scores = confidence_breakdown.get('factor_scores', {})
        if factor_scores:
            factors = list(factor_scores.keys())
            scores = list(factor_scores.values())
            colors = [self._get_bar_color(score) for score in scores]
            
            fig.add_trace(
                go.Bar(
                    x=scores,
                    y=[f.replace('_', ' ').title() for f in factors],
                    orientation='h',
                    marker_color=colors,
                    text=[f'{score:.2f}' for score in scores],
                    textposition='auto'
                ),
                row=1, col=2
            )
        
        # Uncertainty heatmap
        if uncertainty_factors:
            factor_names = [f.name.replace('_', ' ').title() for f in uncertainty_factors]
            impact_scores = [f.impact_score for f in uncertainty_factors]
            
            fig.add_trace(
                go.Heatmap(
                    z=[impact_scores],
                    x=factor_names,
                    y=['Impact Level'],
                    colorscale='Reds',
                    text=[[f'{score:.2f}' for score in impact_scores]],
                    texttemplate='%{text}',
                    textfont={'size': 12}
                ),
                row=2, col=1
            )
        
        # Analysis summary table
        summary_data = self._prepare_summary_table(analysis_result, confidence_breakdown)
        fig.add_trace(
            go.Table(
                header=dict(values=['Metric', 'Value'],
                           fill_color='paleturquoise',
                           align='left'),
                cells=dict(values=[summary_data['metrics'], summary_data['values']],
                          fill_color='lavender',
                          align='left')
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            title_text="K-Pop Sentiment Analysis Dashboard",
            showlegend=False,
            height=800,
            template="plotly_dark"
        )
        
        return fig
    
    def create_trend_analysis_chart(self, trend_data: Dict) -> Optional[go.Figure]:
        """Create interactive trend analysis chart"""
        if not self.available or not trend_data:
            return None
        
        fig = go.Figure()
        
        # Add trend lines for each sentiment
        for sentiment, data in trend_data.get('sentiment_trends', {}).items():
            daily_counts = data.get('daily_counts', [])
            if daily_counts:
                dates = pd.date_range(end=datetime.now(), periods=len(daily_counts), freq='D')
                
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=daily_counts,
                    mode='lines+markers',
                    name=sentiment.replace('_', ' ').title(),
                    line=dict(width=2),
                    marker=dict(size=6)
                ))
        
        fig.update_layout(
            title="Sentiment Trends Over Time",
            xaxis_title="Date",
            yaxis_title="Count",
            template="plotly_dark",
            hovermode='x unified'
        )
        
        return fig
    
    def create_risk_assessment_chart(self, risk_data: Dict) -> Optional[go.Figure]:
        """Create risk assessment visualization"""
        if not self.available or not risk_data:
            return None
        
        risk_distribution = risk_data.get('risk_distribution', {})
        
        # Create pie chart for risk distribution
        fig = go.Figure(data=[go.Pie(
            labels=list(risk_distribution.keys()),
            values=list(risk_distribution.values()),
            hole=0.3,
            marker_colors=['#28a745', '#ffc107', '#fd7e14', '#dc3545']
        )])
        
        fig.update_layout(
            title="Risk Level Distribution",
            template="plotly_dark",
            annotations=[dict(text='Risk<br>Levels', x=0.5, y=0.5, font_size=16, showarrow=False)]
        )
        
        return fig
    
    def _get_gauge_color(self, confidence: float) -> str:
        """Get color for confidence gauge"""
        if confidence >= 0.8:
            return "#28a745"
        elif confidence >= 0.6:
            return "#ffc107"
        elif confidence >= 0.4:
            return "#fd7e14"
        else:
            return "#dc3545"
    
    def _get_bar_color(self, score: float) -> str:
        """Get color for bar chart"""
        if score >= 0.8:
            return "#28a745"
        elif score >= 0.6:
            return "#ffc107"
        elif score >= 0.4:
            return "#fd7e14"
        else:
            return "#dc3545"
    
    def _prepare_summary_table(self, analysis_result: Dict, confidence_breakdown: Dict) -> Dict:
        """Prepare data for summary table"""
        metrics = [
            'Predicted Label',
            'Confidence',
            'Risk Level',
            'Reliability',
            'Language'
        ]
        
        values = [
            analysis_result.get('label_name', 'Unknown'),
            f"{analysis_result.get('confidence', 0):.1%}",
            analysis_result.get('risk_level', 'Unknown'),
            confidence_breakdown.get('reliability_assessment', 'Unknown'),
            analysis_result.get('language', 'English')
        ]
        
        return {'metrics': metrics, 'values': values}

class StaticVisualizationGenerator:
    """Generate static visualizations for reports"""
    
    def __init__(self):
        self.style = 'dark_background'
        plt.style.use(self.style)
    
    def create_analytics_report_charts(self, analytics_report) -> Dict[str, plt.Figure]:
        """Create all charts for analytics report"""
        charts = {}
        
        # Summary statistics chart
        charts['summary'] = self.create_summary_chart(analytics_report.summary_stats)
        
        # Trend analysis chart
        charts['trends'] = self.create_trend_chart(analytics_report.trend_analysis)
        
        # Quality metrics chart
        charts['quality'] = self.create_quality_chart(analytics_report.quality_metrics)
        
        # Risk assessment chart
        charts['risk'] = self.create_risk_chart(analytics_report.risk_assessment)
        
        return charts
    
    def create_summary_chart(self, summary_stats: Dict) -> plt.Figure:
        """Create summary statistics visualization"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Summary Statistics', fontsize=16, fontweight='bold')
        
        # Sentiment distribution
        sentiment_dist = summary_stats.get('sentiment_distribution', {})
        if sentiment_dist:
            labels = [s.replace('_', ' ').title() for s in sentiment_dist.keys()]
            sizes = list(sentiment_dist.values())
            ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax1.set_title('Sentiment Distribution')
        
        # Risk distribution
        risk_dist = summary_stats.get('risk_distribution', {})
        if risk_dist:
            colors = {'Low': '#28a745', 'Medium': '#ffc107', 'High': '#fd7e14', 'Very High': '#dc3545'}
            risk_colors = [colors.get(risk, '#6c757d') for risk in risk_dist.keys()]
            ax2.bar(risk_dist.keys(), risk_dist.values(), color=risk_colors)
            ax2.set_title('Risk Level Distribution')
            ax2.tick_params(axis='x', rotation=45)
        
        # Confidence ranges
        conf_ranges = summary_stats.get('confidence_ranges', {})
        if conf_ranges:
            ax3.bar(conf_ranges.keys(), conf_ranges.values())
            ax3.set_title('Confidence Ranges')
            ax3.tick_params(axis='x', rotation=45)
        
        # Key metrics
        metrics = {
            'Total Analyses': summary_stats.get('total_analyses', 0),
            'Avg Confidence': f"{summary_stats.get('average_confidence', 0):.2%}",
            'Std Deviation': f"{summary_stats.get('confidence_std', 0):.3f}"
        }
        
        ax4.axis('off')
        y_pos = 0.8
        for metric, value in metrics.items():
            ax4.text(0.1, y_pos, f'{metric}:', fontweight='bold', fontsize=12)
            ax4.text(0.6, y_pos, str(value), fontsize=12)
            y_pos -= 0.2
        ax4.set_title('Key Metrics')
        
        plt.tight_layout()
        return fig
    
    def create_trend_chart(self, trend_analysis: Dict) -> plt.Figure:
        """Create trend analysis visualization"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        sentiment_trends = trend_analysis.get('sentiment_trends', {})
        
        for sentiment, data in sentiment_trends.items():
            daily_counts = data.get('daily_counts', [])
            if daily_counts:
                dates = pd.date_range(end=datetime.now(), periods=len(daily_counts), freq='D')
                ax.plot(dates, daily_counts, marker='o', label=sentiment.replace('_', ' ').title())
        
        ax.set_title('Sentiment Trends Over Time', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('Count')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        return fig
    
    def create_quality_chart(self, quality_metrics: Dict) -> plt.Figure:
        """Create quality metrics visualization"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Quality rates
        rates = {
            'Correction Rate': quality_metrics.get('correction_rate', 0),
            'Verification Rate': quality_metrics.get('verification_rate', 0),
            'Low Confidence Rate': quality_metrics.get('low_confidence_rate', 0)
        }
        
        colors = ['#dc3545', '#28a745', '#ffc107']
        ax1.bar(rates.keys(), [r * 100 for r in rates.values()], color=colors)
        ax1.set_title('Quality Metrics (%)')
        ax1.set_ylabel('Percentage')
        ax1.tick_params(axis='x', rotation=45)
        
        # Confidence by sentiment
        conf_by_sentiment = quality_metrics.get('average_confidence_by_sentiment', {})
        if conf_by_sentiment:
            sentiments = [s.replace('_', ' ').title() for s in conf_by_sentiment.keys()]
            confidences = [c * 100 for c in conf_by_sentiment.values()]
            ax2.barh(sentiments, confidences)
            ax2.set_title('Average Confidence by Sentiment')
            ax2.set_xlabel('Confidence (%)')
        
        plt.tight_layout()
        return fig
    
    def create_risk_chart(self, risk_assessment: Dict) -> plt.Figure:
        """Create risk assessment visualization"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Risk distribution pie chart
        risk_dist = risk_assessment.get('risk_distribution', {})
        if risk_dist:
            colors = ['#28a745', '#ffc107', '#fd7e14', '#dc3545']
            ax1.pie(risk_dist.values(), labels=risk_dist.keys(), autopct='%1.1f%%', 
                   colors=colors, startangle=90)
            ax1.set_title('Risk Level Distribution')
        
        # Risk status indicator
        risk_status = risk_assessment.get('overall_risk_status', 'unknown')
        risk_ratio = risk_assessment.get('high_risk_ratio', 0)
        
        status_colors = {'low': '#28a745', 'moderate': '#ffc107', 'elevated': '#dc3545'}
        status_color = status_colors.get(risk_status, '#6c757d')
        
        ax2.bar(['Risk Status'], [risk_ratio * 100], color=status_color)
        ax2.set_title(f'Overall Risk Status: {risk_status.title()}')
        ax2.set_ylabel('High Risk Percentage')
        ax2.set_ylim(0, 100)
        
        # Add status text
        ax2.text(0, risk_ratio * 100 + 5, f'{risk_ratio:.1%}', ha='center', 
                fontweight='bold', fontsize=14)
        
        plt.tight_layout()
        return fig

# Example usage
if __name__ == "__main__":
    # Test confidence visualization
    visualizer = ConfidenceVisualizer()
    
    # Sample data
    confidence = 0.75
    factor_scores = {
        'linguistic_confidence': 0.8,
        'pattern_confidence': 0.7,
        'context_confidence': 0.6,
        'language_support_confidence': 0.9,
        'text_quality_confidence': 0.8
    }
    
    # Create visualizations
    gauge_fig = visualizer.create_confidence_gauge(confidence)
    factor_fig = visualizer.create_factor_breakdown_chart(factor_scores)
    
    # Show plots
    plt.show()
    
    print("Enhanced visualizations created successfully!")
    if PLOTLY_AVAILABLE:
        print("Interactive dashboards are available with Plotly.")
    else:
        print("Install Plotly for interactive dashboards: pip install plotly")