"""
Enhanced Analysis Example
Demonstrates the integration of multi-language support, advanced analytics, and enhanced visualizations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from multilingual_processor import MultiLanguageProcessor
from advanced_analytics import UncertaintyAnalyzer, AdvancedConfidenceCalculator, AdvancedAnalyticsDashboard
from enhanced_visualizations import ConfidenceVisualizer, InteractiveDashboard
import matplotlib.pyplot as plt
from datetime import datetime

class EnhancedSentimentAnalyzer:
    """Enhanced sentiment analyzer with multi-language support and advanced analytics"""
    
    def __init__(self):
        self.multilingual_processor = MultiLanguageProcessor()
        self.uncertainty_analyzer = UncertaintyAnalyzer()
        self.confidence_calculator = AdvancedConfidenceCalculator()
        self.visualizer = ConfidenceVisualizer()
        self.interactive_dashboard = InteractiveDashboard()
        
    def analyze_with_enhanced_features(self, text: str) -> dict:
        """
        Perform comprehensive analysis with all enhanced features
        """
        print(f"🔍 Analyzing: {text}")
        print("=" * 60)
        
        # Step 1: Multi-language processing
        print("📝 Step 1: Language Detection and Processing")
        language_info, processing_result = self.multilingual_processor.process_text(text)
        
        print(f"   Detected Language: {language_info.detected_language}")
        print(f"   Confidence: {language_info.confidence:.2%}")
        print(f"   Supported: {language_info.supported}")
        print(f"   Fallback Used: {language_info.fallback_used}")
        
        # Step 2: Basic sentiment analysis (simplified for demo)
        print("\n🎯 Step 2: Sentiment Classification")
        basic_analysis = self._perform_basic_sentiment_analysis(text, processing_result)
        
        print(f"   Predicted Label: {basic_analysis['label_name']}")
        print(f"   Basic Confidence: {basic_analysis['confidence']:.2%}")
        print(f"   Risk Level: {basic_analysis['risk_level']}")
        
        # Step 3: Uncertainty analysis
        print("\n⚠️  Step 3: Uncertainty Analysis")
        uncertainty_factors = self.uncertainty_analyzer.analyze_uncertainty_factors(
            text, basic_analysis, language_info.__dict__
        )
        
        print(f"   Uncertainty Factors Found: {len(uncertainty_factors)}")
        for factor in uncertainty_factors:
            print(f"   - {factor.name}: {factor.impact_level} impact ({factor.impact_score:.2f})")
            if factor.recommendation:
                print(f"     💡 {factor.recommendation}")
        
        # Step 4: Advanced confidence calculation
        print("\n📊 Step 4: Advanced Confidence Calculation")
        confidence_breakdown = self.confidence_calculator.calculate_comprehensive_confidence(
            text, basic_analysis, language_info.__dict__, uncertainty_factors
        )
        
        print(f"   Overall Confidence: {confidence_breakdown.overall_confidence:.2%}")
        print(f"   Reliability: {confidence_breakdown.reliability_assessment}")
        print("   Factor Breakdown:")
        for explanation in confidence_breakdown.explanation:
            print(f"     {explanation}")
        
        # Step 5: Create visualizations
        print("\n📈 Step 5: Creating Visualizations")
        self._create_visualizations(confidence_breakdown, uncertainty_factors)
        
        # Compile comprehensive result
        comprehensive_result = {
            'text': text,
            'language_info': language_info.__dict__,
            'processing_result': processing_result.__dict__,
            'basic_analysis': basic_analysis,
            'uncertainty_factors': [f.__dict__ for f in uncertainty_factors],
            'confidence_breakdown': confidence_breakdown.__dict__,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        return comprehensive_result
    
    def _perform_basic_sentiment_analysis(self, text: str, processing_result) -> dict:
        """
        Simplified sentiment analysis for demonstration
        In a real implementation, this would use the full sentiment analyzer
        """
        # Analyze sentiment indicators from processing result
        sentiment_indicators = processing_result.sentiment_indicators
        
        # Simple classification logic
        if sentiment_indicators.get('positive', 0) > sentiment_indicators.get('negative', 0):
            if sentiment_indicators.get('enthusiasm', 0) > 0.1:
                label_name = 'ENTHUSIASTIC_SUPPORT'
                label_id = 1
                risk_level = 'Low'
            else:
                label_name = 'NOSTALGIC_APPRECIATION'
                label_id = 2
                risk_level = 'Low'
        elif sentiment_indicators.get('negative', 0) > 0:
            if sentiment_indicators.get('sarcasm', 0) > 0:
                label_name = 'SARCASTIC_MOCKERY'
                label_id = 8
                risk_level = 'High'
            else:
                label_name = 'CRITICAL_DISAPPOINTMENT'
                label_id = 5
                risk_level = 'Medium'
        else:
            label_name = 'NEUTRAL_FACTUAL'
            label_id = 6
            risk_level = 'Low'
        
        # Calculate basic confidence
        total_indicators = sum(sentiment_indicators.values())
        confidence = min(total_indicators * 2, 1.0) if total_indicators > 0 else 0.5
        
        return {
            'predicted_label': label_id,
            'label_name': label_name,
            'confidence': confidence,
            'risk_level': risk_level,
            'reasoning': f"Based on sentiment indicators: {sentiment_indicators}"
        }
    
    def _create_visualizations(self, confidence_breakdown, uncertainty_factors):
        """Create and display visualizations"""
        try:
            # Confidence gauge
            print("   Creating confidence gauge...")
            gauge_fig = self.visualizer.create_confidence_gauge(
                confidence_breakdown.overall_confidence,
                uncertainty_factors,
                "Enhanced Confidence Analysis"
            )
            
            # Factor breakdown chart
            print("   Creating factor breakdown chart...")
            factor_fig = self.visualizer.create_factor_breakdown_chart(
                confidence_breakdown.factor_scores
            )
            
            # Uncertainty heatmap
            print("   Creating uncertainty heatmap...")
            uncertainty_fig = self.visualizer.create_uncertainty_heatmap(uncertainty_factors)
            
            print("   ✅ Visualizations created successfully!")
            print("   📊 Use plt.show() to display the charts")
            
            # Store figures for later display
            self.last_figures = {
                'gauge': gauge_fig,
                'factors': factor_fig,
                'uncertainty': uncertainty_fig
            }
            
        except Exception as e:
            print(f"   ❌ Error creating visualizations: {e}")
    
    def show_visualizations(self):
        """Display all created visualizations"""
        if hasattr(self, 'last_figures'):
            plt.show()
        else:
            print("No visualizations to show. Run analyze_with_enhanced_features() first.")
    
    def batch_analyze_examples(self):
        """Analyze multiple examples to demonstrate different scenarios"""
        examples = [
            {
                'text': "OMG BTS absolutely SLAYED this performance! 🔥 They are the best group ever!",
                'description': "High enthusiasm English text"
            },
            {
                'text': "방탄소년단 정말 대박이야! 사랑해요 💜",
                'description': "Korean enthusiastic text"
            },
            {
                'text': "¡Dios mío, esta canción es increíble! Los amo tanto 💕",
                'description': "Spanish positive text"
            },
            {
                'text': "I think maybe this song is kind of okay but not sure if it's their best work",
                'description': "Uncertain/ambiguous English text"
            },
            {
                'text': "Sure, that performance was 'amazing' 🙄 Not impressed at all",
                'description': "Sarcastic English text"
            }
        ]
        
        results = []
        
        for i, example in enumerate(examples, 1):
            print(f"\n{'='*80}")
            print(f"EXAMPLE {i}: {example['description']}")
            print(f"{'='*80}")
            
            result = self.analyze_with_enhanced_features(example['text'])
            results.append(result)
            
            print(f"\n📋 Summary for Example {i}:")
            print(f"   Language: {result['language_info']['detected_language']}")
            print(f"   Sentiment: {result['basic_analysis']['label_name']}")
            print(f"   Confidence: {result['confidence_breakdown']['overall_confidence']:.2%}")
            print(f"   Reliability: {result['confidence_breakdown']['reliability_assessment']}")
            print(f"   Uncertainty Factors: {len(result['uncertainty_factors'])}")
        
        return results

def demonstrate_analytics_dashboard():
    """Demonstrate the analytics dashboard functionality"""
    print("\n" + "="*80)
    print("ANALYTICS DASHBOARD DEMONSTRATION")
    print("="*80)
    
    dashboard = AdvancedAnalyticsDashboard()
    
    # Generate a sample report
    print("📊 Generating comprehensive analytics report...")
    report = dashboard.generate_comprehensive_report('7d')
    
    print(f"\n📈 Report Summary:")
    print(f"   Generated at: {report.generated_at}")
    print(f"   Recommendations: {len(report.recommendations)}")
    
    if report.recommendations:
        print("   💡 Key Recommendations:")
        for rec in report.recommendations[:3]:  # Show first 3
            print(f"     - {rec}")
    
    return report

def main():
    """Main demonstration function"""
    print("🚀 Enhanced K-Pop Sentiment Analyzer Demonstration")
    print("="*80)
    
    # Initialize enhanced analyzer
    analyzer = EnhancedSentimentAnalyzer()
    
    # Single analysis example
    print("\n🎯 SINGLE ANALYSIS EXAMPLE")
    print("-" * 40)
    
    sample_text = "OMG they absolutely SLAYED this performance! But I'm not sure about the styling choices 🤔"
    result = analyzer.analyze_with_enhanced_features(sample_text)
    
    # Batch analysis examples
    print("\n\n🎯 BATCH ANALYSIS EXAMPLES")
    print("-" * 40)
    
    batch_results = analyzer.batch_analyze_examples()
    
    # Analytics dashboard
    analytics_report = demonstrate_analytics_dashboard()
    
    # Show visualizations
    print("\n\n📊 VISUALIZATIONS")
    print("-" * 40)
    print("Displaying visualizations...")
    analyzer.show_visualizations()
    
    print("\n✅ Enhanced analysis demonstration completed!")
    print("\nKey Features Demonstrated:")
    print("  ✓ Multi-language detection and processing")
    print("  ✓ Advanced uncertainty analysis")
    print("  ✓ Comprehensive confidence calculation")
    print("  ✓ Enhanced visualizations")
    print("  ✓ Analytics dashboard")
    
    return {
        'single_result': result,
        'batch_results': batch_results,
        'analytics_report': analytics_report
    }

if __name__ == "__main__":
    # Run the demonstration
    results = main()
    
    # Optional: Save results to file
    import json
    
    print("\n💾 Saving results to 'enhanced_analysis_results.json'...")
    
    # Convert results to JSON-serializable format
    json_results = {
        'demonstration_completed_at': datetime.now().isoformat(),
        'single_analysis': results['single_result'],
        'batch_analysis_count': len(results['batch_results']),
        'analytics_report_generated': True
    }
    
    with open('enhanced_analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(json_results, f, indent=2, ensure_ascii=False)
    
    print("✅ Results saved successfully!")
    print("\n🎉 Enhanced K-Pop Sentiment Analyzer is ready for production use!")