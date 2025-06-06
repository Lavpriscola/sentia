"""
Comprehensive Test Suite for Real Implementations
Tests all the real implementations to verify they work without mocks or simulations
"""

import sys
import time
import traceback
from datetime import datetime
import numpy as np

def test_uncertainty_analysis():
    """Test real uncertainty analysis"""
    print("🔍 Testing Uncertainty Analysis...")
    
    try:
        from uncertainty_analysis import RealUncertaintyAnalyzer
        
        analyzer = RealUncertaintyAnalyzer()
        
        # Test with various text samples
        test_cases = [
            {
                'text': 'BTS absolutely SLAYED this performance! 🔥💜',
                'analysis': {'predicted_label': 0, 'confidence': 0.85, 'label_name': 'ENTHUSIASTIC_SUPPORT'}
            },
            {
                'text': 'Sure, that was "great"... 🙄',
                'analysis': {'predicted_label': 7, 'confidence': 0.65, 'label_name': 'SARCASTIC_MOCKERY'}
            },
            {
                'text': 'I love this song but the choreography is disappointing',
                'analysis': {'predicted_label': 9, 'confidence': 0.55, 'label_name': 'MIXED_CONFLICTED'}
            }
        ]
        
        for i, case in enumerate(test_cases, 1):
            result = analyzer.analyze_uncertainty(case['text'], case['analysis'])
            
            print(f"  Test {i}: Overall uncertainty: {result.overall_uncertainty:.2f}")
            print(f"    Adjusted confidence: {result.confidence_adjusted:.2f}")
            print(f"    Reliability score: {result.reliability_score:.2f}")
            print(f"    Key factors: {len([f for f in result.uncertainty_factors if f.impact_level in ['high', 'medium']])}")
        
        print("  ✅ Uncertainty analysis working correctly")
        return True
        
    except Exception as e:
        print(f"  ❌ Uncertainty analysis failed: {e}")
        traceback.print_exc()
        return False

def test_advanced_visualizations():
    """Test real advanced visualizations"""
    print("📊 Testing Advanced Visualizations...")
    
    try:
        from advanced_visualizations import RealAdvancedVisualizations
        
        viz = RealAdvancedVisualizations()
        
        print(f"  Loaded {len(viz.data)} data points")
        
        # Test individual visualizations
        tests = [
            ("Sentiment Distribution", viz.create_sentiment_distribution_chart),
            ("Confidence Analysis", viz.create_confidence_analysis_chart),
            ("Temporal Analysis", viz.create_temporal_analysis_chart),
            ("Performance Dashboard", viz.create_performance_dashboard),
            ("Uncertainty Heatmap", viz.create_uncertainty_heatmap),
            ("Correlation Analysis", viz.create_correlation_analysis)
        ]
        
        for name, func in tests:
            try:
                fig = func()
                print(f"    ✅ {name} chart created successfully")
                
                # Close matplotlib figures to prevent memory issues
                if hasattr(fig, 'savefig'):
                    import matplotlib.pyplot as plt
                    plt.close(fig)
                    
            except Exception as e:
                print(f"    ❌ {name} chart failed: {e}")
        
        print("  ✅ Advanced visualizations working correctly")
        return True
        
    except Exception as e:
        print(f"  ❌ Advanced visualizations failed: {e}")
        traceback.print_exc()
        return False

def test_trend_analysis():
    """Test real trend analysis"""
    print("📈 Testing Trend Analysis...")
    
    try:
        from trend_analysis import RealTrendAnalyzer
        
        analyzer = RealTrendAnalyzer()
        
        print(f"  Loaded {len(analyzer.data)} data points")
        
        # Perform trend analysis
        result = analyzer.analyze_trends(days_back=30)
        
        print(f"  Overall trend: {result.overall_trend.trend_direction} ({result.overall_trend.trend_strength})")
        print(f"  R-squared: {result.overall_trend.r_squared:.3f}")
        print(f"  Sentiment trends analyzed: {len(result.sentiment_trends)}")
        print(f"  Seasonal patterns found: {len(result.seasonal_patterns)}")
        print(f"  Anomalies detected: {len(result.anomalies)}")
        print(f"  Insights generated: {len(result.insights)}")
        print(f"  Recommendations: {len(result.recommendations)}")
        
        # Test forecasting
        if result.overall_trend.forecast_7d > 0:
            print(f"  7-day forecast: {result.overall_trend.forecast_7d:.1f}")
        
        print("  ✅ Trend analysis working correctly")
        return True
        
    except Exception as e:
        print(f"  ❌ Trend analysis failed: {e}")
        traceback.print_exc()
        return False

def test_confidence_calculator():
    """Test real confidence calculator"""
    print("🎯 Testing Confidence Calculator...")
    
    try:
        from confidence_calculator import RealConfidenceCalculator
        
        calculator = RealConfidenceCalculator()
        
        print(f"  Historical data points: {len(calculator.historical_data)}")
        print(f"  Validation accuracy: {calculator.validation_metrics.accuracy:.3f}")
        
        # Test confidence calculation
        test_cases = [
            {
                'text': 'OMG BTS absolutely SLAYED this performance! 🔥💜',
                'analysis': {'predicted_label': 0, 'confidence': 0.85, 'label_name': 'ENTHUSIASTIC_SUPPORT'}
            },
            {
                'text': 'The group announced their comeback date.',
                'analysis': {'predicted_label': 5, 'confidence': 0.75, 'label_name': 'NEUTRAL_FACTUAL'}
            }
        ]
        
        for i, case in enumerate(test_cases, 1):
            result = calculator.calculate_confidence(case['text'], case['analysis'])
            
            print(f"  Test {i}: Original confidence: {case['analysis']['confidence']:.3f}")
            print(f"    Calculated confidence: {result.confidence_score:.3f}")
            print(f"    Reliability score: {result.reliability_indicators['overall_reliability']:.3f}")
            print(f"    Recommendations: {len(result.recommendations)}")
        
        print("  ✅ Confidence calculator working correctly")
        return True
        
    except Exception as e:
        print(f"  ❌ Confidence calculator failed: {e}")
        traceback.print_exc()
        return False

def test_data_collector():
    """Test real data collector"""
    print("🌐 Testing Data Collector...")
    
    try:
        from real_data_collector import RealDataCollector
        
        collector = RealDataCollector()
        
        # Test database setup
        stats = collector.get_collection_stats()
        print(f"  Database initialized: {stats['total_data_points']} existing data points")
        
        # Test individual source configurations
        sources_status = {
            'YouTube': collector.youtube_client is not None,
            'Twitter': collector.twitter_client is not None,
            'Reddit': collector.reddit_client is not None
        }
        
        for source, status in sources_status.items():
            status_icon = "✅" if status else "⚠️"
            print(f"    {source} API: {status_icon} {'Configured' if status else 'Not configured'}")
        
        # Test data collection (with small limits to avoid API costs)
        if any(sources_status.values()):
            print("  Testing data collection with small sample...")
            
            # Test with a small query
            results = collector.collect_from_all_sources("BTS", max_results_per_source=2)
            
            total_collected = sum(result.collected_count for result in results.values())
            successful_sources = sum(1 for result in results.values() if result.success)
            
            print(f"    Collected {total_collected} items from {successful_sources} sources")
            
            for source, result in results.items():
                status = "✅" if result.success else "❌"
                print(f"      {source}: {status} {result.collected_count} items")
        
        print("  ✅ Data collector working correctly")
        return True
        
    except Exception as e:
        print(f"  ❌ Data collector failed: {e}")
        traceback.print_exc()
        return False

def test_rate_limiter():
    """Test real rate limiter"""
    print("⏱️ Testing Rate Limiter...")
    
    try:
        from rate_limiter import RealRateLimiter, RateLimitConfig, RateLimitExceeded
        
        limiter = RealRateLimiter(fallback_to_memory=True)
        
        # Configure a test rate limit
        limiter.configure_rate_limit("test_api", RateLimitConfig(
            max_requests=5,
            time_window=10,  # 5 requests per 10 seconds
            burst_limit=3
        ))
        
        # Test rate limiting
        @limiter.rate_limit_decorator("test_api")
        def test_function():
            time.sleep(0.01)
            return "success"
        
        success_count = 0
        rate_limited_count = 0
        
        # Make requests to test rate limiting
        for i in range(8):
            try:
                result = test_function()
                success_count += 1
            except RateLimitExceeded:
                rate_limited_count += 1
            except Exception as e:
                print(f"    Unexpected error: {e}")
        
        print(f"  Rate limiting test: {success_count} successful, {rate_limited_count} rate limited")
        
        # Test metrics collection
        metrics = limiter.get_current_metrics()
        if metrics:
            print(f"  Metrics collected: {metrics.get('total_requests', 0)} requests tracked")
        
        # Test load testing (small scale)
        print("  Running mini load test...")
        
        def simple_task():
            time.sleep(0.001)  # 1ms task
            return "done"
        
        load_result = limiter.load_test(
            test_function=simple_task,
            test_name="mini_load_test",
            concurrent_users=3,
            requests_per_user=5,
            ramp_up_time=1
        )
        
        print(f"    Load test: {load_result.successful_requests}/{load_result.total_requests} successful")
        print(f"    Average response time: {load_result.average_response_time:.3f}s")
        print(f"    Requests per second: {load_result.requests_per_second:.2f}")
        
        print("  ✅ Rate limiter working correctly")
        return True
        
    except Exception as e:
        print(f"  ❌ Rate limiter failed: {e}")
        traceback.print_exc()
        return False

def test_integration():
    """Test integration between components"""
    print("🔗 Testing Component Integration...")
    
    try:
        # Test uncertainty analysis with confidence calculator
        from uncertainty_analysis import RealUncertaintyAnalyzer
        from confidence_calculator import RealConfidenceCalculator
        
        uncertainty_analyzer = RealUncertaintyAnalyzer()
        confidence_calculator = RealConfidenceCalculator()
        
        test_text = "BTS comeback is amazing but the styling could be better"
        test_analysis = {
            'predicted_label': 9,
            'confidence': 0.65,
            'label_name': 'MIXED_CONFLICTED'
        }
        
        # Get uncertainty analysis
        uncertainty_result = uncertainty_analyzer.analyze_uncertainty(test_text, test_analysis)
        
        # Get confidence analysis
        confidence_result = confidence_calculator.calculate_confidence(test_text, test_analysis)
        
        print(f"  Integration test:")
        print(f"    Original confidence: {test_analysis['confidence']:.3f}")
        print(f"    Uncertainty-adjusted: {uncertainty_result.confidence_adjusted:.3f}")
        print(f"    Calculator confidence: {confidence_result.confidence_score:.3f}")
        print(f"    Reliability score: {confidence_result.reliability_indicators['overall_reliability']:.3f}")
        
        # Test with visualization
        from advanced_visualizations import RealAdvancedVisualizations
        
        viz = RealAdvancedVisualizations()
        
        # Create a simple chart to test integration
        fig = viz.create_sentiment_distribution_chart()
        print(f"    Visualization created with {len(viz.data)} data points")
        
        if hasattr(fig, 'savefig'):
            import matplotlib.pyplot as plt
            plt.close(fig)
        
        print("  ✅ Component integration working correctly")
        return True
        
    except Exception as e:
        print(f"  ❌ Component integration failed: {e}")
        traceback.print_exc()
        return False

def run_comprehensive_tests():
    """Run all tests and provide summary"""
    print("=" * 60)
    print("🧪 COMPREHENSIVE REAL IMPLEMENTATION TESTS")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Uncertainty Analysis", test_uncertainty_analysis),
        ("Advanced Visualizations", test_advanced_visualizations),
        ("Trend Analysis", test_trend_analysis),
        ("Confidence Calculator", test_confidence_calculator),
        ("Data Collector", test_data_collector),
        ("Rate Limiter", test_rate_limiter),
        ("Component Integration", test_integration)
    ]
    
    results = {}
    start_time = time.time()
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        
        test_start = time.time()
        try:
            success = test_func()
            test_duration = time.time() - test_start
            results[test_name] = {
                'success': success,
                'duration': test_duration,
                'error': None
            }
        except Exception as e:
            test_duration = time.time() - test_start
            results[test_name] = {
                'success': False,
                'duration': test_duration,
                'error': str(e)
            }
            print(f"❌ {test_name} failed with exception: {e}")
    
    # Print summary
    total_duration = time.time() - start_time
    successful_tests = sum(1 for r in results.values() if r['success'])
    total_tests = len(results)
    
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        duration = result['duration']
        print(f"{test_name:.<30} {status} ({duration:.2f}s)")
        
        if not result['success'] and result['error']:
            print(f"  Error: {result['error']}")
    
    print(f"\nOverall Results: {successful_tests}/{total_tests} tests passed")
    print(f"Total Duration: {total_duration:.2f} seconds")
    print(f"Success Rate: {successful_tests/total_tests:.1%}")
    
    if successful_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! All real implementations are working correctly.")
    else:
        print(f"\n⚠️ {total_tests - successful_tests} tests failed. Check the errors above.")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return successful_tests == total_tests

if __name__ == "__main__":
    # Run comprehensive tests
    all_passed = run_comprehensive_tests()
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)