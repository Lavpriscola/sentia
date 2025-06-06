"""
Advanced Visualization Example using Matplotlib
Demonstrates interactive charts and graphs for K-Pop sentiment analysis
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
from wordcloud import WordCloud
import tkinter as tk
from tkinter import ttk

# Set style for better-looking plots
plt.style.use('dark_background')
sns.set_palette("husl")

class KPopSentimentVisualizer:
    def __init__(self, parent_frame=None):
        self.parent = parent_frame
        self.setup_sample_data()
        
    def setup_sample_data(self):
        """Create sample data for demonstration"""
        # Sample sentiment data
        self.sentiment_data = {
            'Enthusiastic Support': 35,
            'Nostalgic Appreciation': 15,
            'Anticipatory Excitement': 20,
            'Protective Defensive': 10,
            'Critical Disappointment': 8,
            'Neutral Factual': 5,
            'Competitive Rivalry': 4,
            'Sarcastic Mockery': 2,
            'Malicious Coordinated': 1
        }
        
        # Sample emotion data
        self.emotion_data = {
            'Joy': 0.7,
            'Excitement': 0.6,
            'Love': 0.5,
            'Anger': 0.2,
            'Sadness': 0.1,
            'Fear': 0.05,
            'Surprise': 0.4,
            'Disgust': 0.1
        }
        
        # Sample time series data
        dates = [datetime.now() - timedelta(days=x) for x in range(30, 0, -1)]
        self.timeline_data = pd.DataFrame({
            'date': dates,
            'positive': [random.uniform(0.3, 0.8) for _ in range(30)],
            'negative': [random.uniform(0.1, 0.4) for _ in range(30)],
            'neutral': [random.uniform(0.2, 0.5) for _ in range(30)]
        })
        
        # Sample K-Pop groups data
        self.groups_data = {
            'BTS': {'positive': 85, 'negative': 10, 'neutral': 5},
            'BLACKPINK': {'positive': 80, 'negative': 15, 'neutral': 5},
            'TWICE': {'positive': 75, 'negative': 20, 'neutral': 5},
            'Stray Kids': {'positive': 70, 'negative': 25, 'neutral': 5},
            'ITZY': {'positive': 65, 'negative': 30, 'neutral': 5}
        }
        
        # Sample text for word cloud
        self.sample_text = """
        BTS amazing performance love incredible talent music video
        BLACKPINK stunning vocals dance choreography beautiful
        TWICE cute concept catchy song melody harmony
        Stray Kids powerful rap energy stage presence
        ITZY confident charismatic fierce attitude
        comeback debut album single chart success
        fandom ARMY Blink Once Stay Midzy
        """

    def create_sentiment_distribution_pie(self, fig=None, ax=None):
        """Create a pie chart showing sentiment distribution"""
        if fig is None or ax is None:
            fig, ax = plt.subplots(figsize=(10, 8))
            fig.patch.set_facecolor('#2b2b2b')
        
        # Prepare data
        labels = list(self.sentiment_data.keys())
        sizes = list(self.sentiment_data.values())
        
        # Create color palette
        colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            sizes, 
            labels=labels, 
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 10, 'color': 'white'}
        )
        
        # Customize appearance
        for autotext in autotexts:
            autotext.set_color('black')
            autotext.set_fontweight('bold')
        
        ax.set_title('K-Pop Sentiment Distribution', 
                    fontsize=16, fontweight='bold', color='white', pad=20)
        
        return fig, ax

    def create_emotion_radar_chart(self, fig=None, ax=None):
        """Create a radar chart for multi-dimensional emotions"""
        if fig is None or ax is None:
            fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(projection='polar'))
            fig.patch.set_facecolor('#2b2b2b')
        
        # Prepare data
        emotions = list(self.emotion_data.keys())
        values = list(self.emotion_data.values())
        
        # Number of variables
        N = len(emotions)
        
        # Compute angle for each axis
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # Complete the circle
        
        # Add values to complete the circle
        values += values[:1]
        
        # Plot
        ax.plot(angles, values, 'o-', linewidth=2, label='Emotions', color='#ff6b6b')
        ax.fill(angles, values, alpha=0.25, color='#ff6b6b')
        
        # Add labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(emotions, color='white', fontsize=12)
        
        # Set y-axis limits
        ax.set_ylim(0, 1)
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], color='gray', fontsize=10)
        
        # Add grid
        ax.grid(True, alpha=0.3)
        
        # Title
        ax.set_title('Emotion Analysis Radar Chart', 
                    fontsize=16, fontweight='bold', color='white', pad=30)
        
        return fig, ax

    def create_sentiment_timeline(self, fig=None, ax=None):
        """Create a timeline showing sentiment changes over time"""
        if fig is None or ax is None:
            fig, ax = plt.subplots(figsize=(12, 6))
            fig.patch.set_facecolor('#2b2b2b')
        
        # Plot lines
        ax.plot(self.timeline_data['date'], self.timeline_data['positive'], 
               label='Positive', color='#2ecc71', linewidth=2, marker='o', markersize=4)
        ax.plot(self.timeline_data['date'], self.timeline_data['negative'], 
               label='Negative', color='#e74c3c', linewidth=2, marker='s', markersize=4)
        ax.plot(self.timeline_data['date'], self.timeline_data['neutral'], 
               label='Neutral', color='#95a5a6', linewidth=2, marker='^', markersize=4)
        
        # Fill areas
        ax.fill_between(self.timeline_data['date'], self.timeline_data['positive'], 
                       alpha=0.3, color='#2ecc71')
        ax.fill_between(self.timeline_data['date'], self.timeline_data['negative'], 
                       alpha=0.3, color='#e74c3c')
        
        # Customize appearance
        ax.set_xlabel('Date', fontsize=12, color='white')
        ax.set_ylabel('Sentiment Score', fontsize=12, color='white')
        ax.set_title('Sentiment Timeline (Last 30 Days)', 
                    fontsize=16, fontweight='bold', color='white')
        
        # Rotate x-axis labels
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right', color='white')
        ax.tick_params(colors='white')
        
        # Legend
        ax.legend(loc='upper left', framealpha=0.8)
        
        # Grid
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig, ax

    def create_risk_heatmap(self, fig=None, ax=None):
        """Create a heatmap showing risk levels across different content"""
        if fig is None or ax is None:
            fig, ax = plt.subplots(figsize=(10, 8))
            fig.patch.set_facecolor('#2b2b2b')
        
        # Sample risk data
        risk_data = np.array([
            [0.1, 0.2, 0.1, 0.3, 0.2],  # BTS
            [0.2, 0.1, 0.2, 0.4, 0.1],  # BLACKPINK
            [0.1, 0.3, 0.1, 0.2, 0.3],  # TWICE
            [0.3, 0.2, 0.4, 0.1, 0.2],  # Stray Kids
            [0.2, 0.4, 0.2, 0.1, 0.1]   # ITZY
        ])
        
        groups = ['BTS', 'BLACKPINK', 'TWICE', 'Stray Kids', 'ITZY']
        content_types = ['Music Videos', 'Live Performances', 'Variety Shows', 'Social Media', 'News Articles']
        
        # Create heatmap
        im = ax.imshow(risk_data, cmap='Reds', aspect='auto')
        
        # Set ticks and labels
        ax.set_xticks(np.arange(len(content_types)))
        ax.set_yticks(np.arange(len(groups)))
        ax.set_xticklabels(content_types, color='white')
        ax.set_yticklabels(groups, color='white')
        
        # Rotate the tick labels and set their alignment
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        
        # Add text annotations
        for i in range(len(groups)):
            for j in range(len(content_types)):
                text = ax.text(j, i, f'{risk_data[i, j]:.1f}',
                             ha="center", va="center", color="white", fontweight='bold')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Risk Level', color='white', fontsize=12)
        cbar.ax.tick_params(colors='white')
        
        ax.set_title('Risk Level Heatmap by Group and Content Type', 
                    fontsize=16, fontweight='bold', color='white', pad=20)
        
        plt.tight_layout()
        return fig, ax

    def create_group_comparison_bar(self, fig=None, ax=None):
        """Create a bar chart comparing sentiment across K-Pop groups"""
        if fig is None or ax is None:
            fig, ax = plt.subplots(figsize=(12, 6))
            fig.patch.set_facecolor('#2b2b2b')
        
        groups = list(self.groups_data.keys())
        positive = [self.groups_data[group]['positive'] for group in groups]
        negative = [self.groups_data[group]['negative'] for group in groups]
        neutral = [self.groups_data[group]['neutral'] for group in groups]
        
        x = np.arange(len(groups))
        width = 0.25
        
        # Create bars
        bars1 = ax.bar(x - width, positive, width, label='Positive', color='#2ecc71', alpha=0.8)
        bars2 = ax.bar(x, negative, width, label='Negative', color='#e74c3c', alpha=0.8)
        bars3 = ax.bar(x + width, neutral, width, label='Neutral', color='#95a5a6', alpha=0.8)
        
        # Add value labels on bars
        def add_value_labels(bars):
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                       f'{height}%', ha='center', va='bottom', color='white', fontweight='bold')
        
        add_value_labels(bars1)
        add_value_labels(bars2)
        add_value_labels(bars3)
        
        # Customize appearance
        ax.set_xlabel('K-Pop Groups', fontsize=12, color='white')
        ax.set_ylabel('Sentiment Percentage', fontsize=12, color='white')
        ax.set_title('Sentiment Comparison Across K-Pop Groups', 
                    fontsize=16, fontweight='bold', color='white')
        ax.set_xticks(x)
        ax.set_xticklabels(groups, color='white')
        ax.tick_params(colors='white')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        return fig, ax

    def create_wordcloud(self, fig=None, ax=None):
        """Create a word cloud from K-Pop sentiment text"""
        if fig is None or ax is None:
            fig, ax = plt.subplots(figsize=(12, 8))
            fig.patch.set_facecolor('#2b2b2b')
        
        # Create word cloud
        wordcloud = WordCloud(
            width=800, 
            height=600,
            background_color='#2b2b2b',
            colormap='viridis',
            max_words=100,
            relative_scaling=0.5,
            random_state=42
        ).generate(self.sample_text)
        
        # Display word cloud
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title('K-Pop Sentiment Word Cloud', 
                    fontsize=16, fontweight='bold', color='white', pad=20)
        
        plt.tight_layout()
        return fig, ax

    def create_interactive_dashboard(self, master_window=None):
        """Create an interactive dashboard with multiple visualizations"""
        if master_window is None:
            master_window = tk.Tk()
            master_window.title("K-Pop Sentiment Analysis Dashboard")
            master_window.geometry("1400x900")
            master_window.configure(bg='#2b2b2b')
        
        # Create notebook for tabs
        notebook = ttk.Notebook(master_window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Sentiment Distribution
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="Sentiment Distribution")
        
        fig1, ax1 = self.create_sentiment_distribution_pie()
        canvas1 = FigureCanvasTkAgg(fig1, tab1)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill='both', expand=True)
        
        # Tab 2: Emotion Radar
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="Emotion Analysis")
        
        fig2, ax2 = self.create_emotion_radar_chart()
        canvas2 = FigureCanvasTkAgg(fig2, tab2)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill='both', expand=True)
        
        # Tab 3: Timeline
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text="Timeline Analysis")
        
        fig3, ax3 = self.create_sentiment_timeline()
        canvas3 = FigureCanvasTkAgg(fig3, tab3)
        canvas3.draw()
        canvas3.get_tk_widget().pack(fill='both', expand=True)
        
        # Tab 4: Risk Heatmap
        tab4 = ttk.Frame(notebook)
        notebook.add(tab4, text="Risk Assessment")
        
        fig4, ax4 = self.create_risk_heatmap()
        canvas4 = FigureCanvasTkAgg(fig4, tab4)
        canvas4.draw()
        canvas4.get_tk_widget().pack(fill='both', expand=True)
        
        # Tab 5: Group Comparison
        tab5 = ttk.Frame(notebook)
        notebook.add(tab5, text="Group Comparison")
        
        fig5, ax5 = self.create_group_comparison_bar()
        canvas5 = FigureCanvasTkAgg(fig5, tab5)
        canvas5.draw()
        canvas5.get_tk_widget().pack(fill='both', expand=True)
        
        # Tab 6: Word Cloud
        tab6 = ttk.Frame(notebook)
        notebook.add(tab6, text="Word Cloud")
        
        fig6, ax6 = self.create_wordcloud()
        canvas6 = FigureCanvasTkAgg(fig6, tab6)
        canvas6.draw()
        canvas6.get_tk_widget().pack(fill='both', expand=True)
        
        return master_window

    def create_real_time_chart(self, fig=None, ax=None):
        """Create a real-time updating chart"""
        if fig is None or ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
            fig.patch.set_facecolor('#2b2b2b')
        
        # Initialize data
        self.real_time_data = {'x': [], 'y': []}
        self.line, = ax.plot([], [], 'o-', color='#3498db', linewidth=2)
        
        ax.set_xlim(0, 50)
        ax.set_ylim(-1, 1)
        ax.set_xlabel('Time', color='white')
        ax.set_ylabel('Sentiment Score', color='white')
        ax.set_title('Real-time Sentiment Analysis', color='white', fontweight='bold')
        ax.tick_params(colors='white')
        ax.grid(True, alpha=0.3)
        
        def animate(frame):
            # Simulate real-time data
            if len(self.real_time_data['x']) >= 50:
                self.real_time_data['x'].pop(0)
                self.real_time_data['y'].pop(0)
            
            self.real_time_data['x'].append(frame)
            self.real_time_data['y'].append(random.uniform(-1, 1))
            
            self.line.set_data(self.real_time_data['x'], self.real_time_data['y'])
            return self.line,
        
        # Create animation
        ani = animation.FuncAnimation(fig, animate, interval=100, blit=True, cache_frame_data=False)
        
        return fig, ax, ani

# Example usage and testing
if __name__ == "__main__":
    # Create visualizer
    visualizer = KPopSentimentVisualizer()
    
    # Option 1: Create individual charts
    print("Creating individual charts...")
    
    # Sentiment distribution pie chart
    fig1, ax1 = visualizer.create_sentiment_distribution_pie()
    plt.show()
    
    # Emotion radar chart
    fig2, ax2 = visualizer.create_emotion_radar_chart()
    plt.show()
    
    # Timeline analysis
    fig3, ax3 = visualizer.create_sentiment_timeline()
    plt.show()
    
    # Option 2: Create interactive dashboard (uncomment to run)
    # print("Creating interactive dashboard...")
    # dashboard = visualizer.create_interactive_dashboard()
    # dashboard.mainloop()
    
    print("Visualization examples completed!")