"""
K-Pop Sentiment Analysis Web Application

Flask web app providing a GUI for sentiment analysis with manual data correction capabilities.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
import json
import sqlite3
from datetime import datetime

from sentiment_analyzer import KPopSentimentAnalyzer
from sentiment_labels import SENTIMENT_LABELS, get_all_labels

app = Flask(__name__)
app.secret_key = 'kpop_sentiment_secret_key_2024'
CORS(app)

# Initialize sentiment analyzer
analyzer = KPopSentimentAnalyzer()

@app.route('/')
def index():
    """Main dashboard page"""
    stats = analyzer.get_statistics()
    recent_analyses = analyzer.get_analysis_history(limit=10)
    return render_template('index.html', stats=stats, recent_analyses=recent_analyses)

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    """Sentiment analysis page"""
    if request.method == 'POST':
        text = request.form.get('text', '').strip()
        if not text:
            flash('Please enter some text to analyze.', 'error')
            return redirect(url_for('analyze'))
        
        # Perform sentiment analysis
        result = analyzer.analyze_sentiment(text)
        
        return render_template('analyze.html', 
                             result=result, 
                             sentiment_labels=SENTIMENT_LABELS,
                             show_result=True)
    
    return render_template('analyze.html', 
                         sentiment_labels=SENTIMENT_LABELS,
                         show_result=False)

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for sentiment analysis"""
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    
    text = data['text'].strip()
    if not text:
        return jsonify({'error': 'Empty text provided'}), 400
    
    try:
        result = analyzer.analyze_sentiment(text)
        return jsonify({
            'success': True,
            'result': {
                'text': result.text,
                'predicted_label': result.predicted_label,
                'label_name': result.label_name,
                'confidence': result.confidence,
                'risk_level': result.risk_level,
                'reasoning': result.reasoning,
                'timestamp': result.timestamp.isoformat()
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/data')
def data_management():
    """Data management page"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get paginated results
    conn = sqlite3.connect(analyzer.db_path)
    cursor = conn.cursor()
    
    # Get total count
    cursor.execute('SELECT COUNT(*) FROM sentiment_analysis')
    total = cursor.fetchone()[0]
    
    # Get paginated data
    offset = (page - 1) * per_page
    cursor.execute('''
        SELECT * FROM sentiment_analysis 
        ORDER BY timestamp DESC 
        LIMIT ? OFFSET ?
    ''', (per_page, offset))
    
    columns = [description[0] for description in cursor.description]
    analyses = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    conn.close()
    
    # Calculate pagination info
    total_pages = (total + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    
    return render_template('data_management.html',
                         analyses=analyses,
                         sentiment_labels=SENTIMENT_LABELS,
                         page=page,
                         total_pages=total_pages,
                         has_prev=has_prev,
                         has_next=has_next,
                         total=total)

@app.route('/update_label/<int:analysis_id>', methods=['POST'])
def update_label(analysis_id):
    """Update sentiment label for an analysis"""
    corrected_label = request.form.get('corrected_label', type=int)
    
    if corrected_label not in SENTIMENT_LABELS:
        flash('Invalid sentiment label.', 'error')
        return redirect(url_for('data_management'))
    
    try:
        analyzer.update_label(analysis_id, corrected_label)
        flash('Label updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating label: {str(e)}', 'error')
    
    return redirect(url_for('data_management'))

@app.route('/delete_analysis/<int:analysis_id>', methods=['POST'])
def delete_analysis(analysis_id):
    """Delete an analysis record"""
    try:
        analyzer.delete_analysis(analysis_id)
        flash('Analysis deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting analysis: {str(e)}', 'error')
    
    return redirect(url_for('data_management'))

@app.route('/statistics')
def statistics():
    """Statistics and analytics page"""
    stats = analyzer.get_statistics()
    
    # Get detailed statistics
    conn = sqlite3.connect(analyzer.db_path)
    cursor = conn.cursor()
    
    # Daily analysis counts for the last 30 days
    cursor.execute('''
        SELECT DATE(timestamp) as date, COUNT(*) as count
        FROM sentiment_analysis 
        WHERE timestamp >= datetime('now', '-30 days')
        GROUP BY DATE(timestamp)
        ORDER BY date
    ''')
    daily_counts = cursor.fetchall()
    
    # Risk level trends
    cursor.execute('''
        SELECT risk_level, 
               COUNT(*) as total,
               AVG(confidence) as avg_confidence
        FROM sentiment_analysis 
        GROUP BY risk_level
    ''')
    risk_trends = cursor.fetchall()
    
    # Correction rates
    cursor.execute('''
        SELECT 
            COUNT(*) as total_analyses,
            SUM(CASE WHEN user_corrected_label IS NOT NULL THEN 1 ELSE 0 END) as corrected,
            SUM(CASE WHEN is_verified = 1 THEN 1 ELSE 0 END) as verified
        FROM sentiment_analysis
    ''')
    correction_stats = cursor.fetchone()
    
    conn.close()
    
    return render_template('statistics.html',
                         stats=stats,
                         daily_counts=daily_counts,
                         risk_trends=risk_trends,
                         correction_stats=correction_stats,
                         sentiment_labels=SENTIMENT_LABELS)

@app.route('/export')
def export_data():
    """Export data as JSON"""
    analyses = analyzer.get_analysis_history(limit=10000)  # Export all data
    
    # Clean up data for export
    export_data = []
    for analysis in analyses:
        export_item = {
            'id': analysis['id'],
            'text': analysis['text'],
            'predicted_label': analysis['predicted_label'],
            'label_name': analysis['label_name'],
            'confidence': analysis['confidence'],
            'risk_level': analysis['risk_level'],
            'reasoning': analysis['reasoning'],
            'timestamp': analysis['timestamp'],
            'user_corrected_label': analysis['user_corrected_label'],
            'is_verified': bool(analysis['is_verified'])
        }
        export_data.append(export_item)
    
    return jsonify({
        'export_timestamp': datetime.now().isoformat(),
        'total_records': len(export_data),
        'sentiment_labels': SENTIMENT_LABELS,
        'data': export_data
    })

@app.route('/labels')
def view_labels():
    """View sentiment labels information"""
    return render_template('labels.html', sentiment_labels=SENTIMENT_LABELS)

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', 
                         error_code=404, 
                         error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', 
                         error_code=500, 
                         error_message="Internal server error"), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12000, debug=True)