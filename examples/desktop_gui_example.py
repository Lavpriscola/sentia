"""
Desktop GUI Example using CustomTkinter
Demonstrates a modern desktop interface for K-Pop sentiment analysis
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
from datetime import datetime
import json

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class KPopSentimentDesktopApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("K-Pop Sentiment Analyzer Pro")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Initialize variables
        self.current_analysis = None
        self.analysis_history = []
        
        # Setup the UI
        self.setup_ui()
        
    def setup_ui(self):
        """Create the main user interface"""
        # Create main container
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_main_content()
        
        # Show analysis panel by default
        self.show_analysis_panel()
    
    def create_sidebar(self):
        """Create the navigation sidebar"""
        self.sidebar = ctk.CTkFrame(self.main_container, width=200)
        self.sidebar.pack(side="left", fill="y", padx=(0, 10))
        self.sidebar.pack_propagate(False)
        
        # App title
        title_label = ctk.CTkLabel(
            self.sidebar, 
            text="K-Pop Sentiment\nAnalyzer Pro",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(20, 30))
        
        # Navigation buttons
        nav_buttons = [
            ("🔍 Text Analysis", self.show_analysis_panel),
            ("📊 Visualizations", self.show_visualization_panel),
            ("🎥 YouTube Data", self.show_youtube_panel),
            ("📁 Data Management", self.show_data_panel),
            ("⚙️ Settings", self.show_settings_panel)
        ]
        
        self.nav_buttons = {}
        for text, command in nav_buttons:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=command,
                height=40,
                font=ctk.CTkFont(size=14)
            )
            btn.pack(pady=5, padx=20, fill="x")
            self.nav_buttons[text] = btn
        
        # Status section
        status_frame = ctk.CTkFrame(self.sidebar)
        status_frame.pack(side="bottom", fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(status_frame, text="Status", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.status_label = ctk.CTkLabel(status_frame, text="Ready", text_color="green")
        self.status_label.pack(pady=5)
    
    def create_main_content(self):
        """Create the main content area"""
        self.content_frame = ctk.CTkFrame(self.main_container)
        self.content_frame.pack(side="right", fill="both", expand=True)
        
        # Create different panels
        self.create_analysis_panel()
        self.create_visualization_panel()
        self.create_youtube_panel()
        self.create_data_panel()
        self.create_settings_panel()
    
    def create_analysis_panel(self):
        """Create the text analysis panel"""
        self.analysis_panel = ctk.CTkFrame(self.content_frame)
        
        # Title
        title = ctk.CTkLabel(
            self.analysis_panel,
            text="Text Sentiment Analysis",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Input section
        input_frame = ctk.CTkFrame(self.analysis_panel)
        input_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(input_frame, text="Enter K-Pop related text:", font=ctk.CTkFont(size=16)).pack(anchor="w", padx=20, pady=(20, 5))
        
        self.text_input = ctk.CTkTextbox(input_frame, height=120, font=ctk.CTkFont(size=14))
        self.text_input.pack(fill="x", padx=20, pady=(0, 10))
        
        # Buttons
        button_frame = ctk.CTkFrame(input_frame)
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        analyze_btn = ctk.CTkButton(
            button_frame,
            text="🔍 Analyze Sentiment",
            command=self.analyze_text,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        analyze_btn.pack(side="left", padx=(0, 10))
        
        clear_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ Clear",
            command=self.clear_text,
            height=40,
            fg_color="gray"
        )
        clear_btn.pack(side="left", padx=(0, 10))
        
        load_btn = ctk.CTkButton(
            button_frame,
            text="📁 Load File",
            command=self.load_text_file,
            height=40,
            fg_color="gray"
        )
        load_btn.pack(side="left")
        
        # Results section
        self.results_frame = ctk.CTkFrame(self.analysis_panel)
        self.results_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.create_results_display()
    
    def create_results_display(self):
        """Create the results display area"""
        # Results title
        results_title = ctk.CTkLabel(
            self.results_frame,
            text="Analysis Results",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        results_title.pack(pady=(20, 10))
        
        # Results content
        self.results_content = ctk.CTkFrame(self.results_frame)
        self.results_content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Placeholder text
        self.placeholder_label = ctk.CTkLabel(
            self.results_content,
            text="Enter text above and click 'Analyze Sentiment' to see results",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.placeholder_label.pack(expand=True)
    
    def create_visualization_panel(self):
        """Create the visualization panel"""
        self.visualization_panel = ctk.CTkFrame(self.content_frame)
        
        title = ctk.CTkLabel(
            self.visualization_panel,
            text="Sentiment Visualizations",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Chart controls
        controls_frame = ctk.CTkFrame(self.visualization_panel)
        controls_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(controls_frame, text="Chart Type:", font=ctk.CTkFont(size=14)).pack(side="left", padx=20, pady=20)
        
        self.chart_type = ctk.CTkOptionMenu(
            controls_frame,
            values=["Sentiment Distribution", "Emotion Radar", "Timeline Analysis", "Risk Assessment"],
            command=self.update_chart
        )
        self.chart_type.pack(side="left", padx=10, pady=20)
        
        refresh_btn = ctk.CTkButton(
            controls_frame,
            text="🔄 Refresh",
            command=self.refresh_charts,
            height=35
        )
        refresh_btn.pack(side="right", padx=20, pady=20)
        
        # Chart area
        self.chart_frame = ctk.CTkFrame(self.visualization_panel)
        self.chart_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.create_sample_chart()
    
    def create_youtube_panel(self):
        """Create the YouTube data collection panel"""
        self.youtube_panel = ctk.CTkFrame(self.content_frame)
        
        title = ctk.CTkLabel(
            self.youtube_panel,
            text="YouTube Data Collection",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # API key section
        api_frame = ctk.CTkFrame(self.youtube_panel)
        api_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(api_frame, text="YouTube API Key:", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20, pady=(20, 5))
        
        self.api_key_entry = ctk.CTkEntry(api_frame, placeholder_text="Enter your YouTube Data API key", show="*")
        self.api_key_entry.pack(fill="x", padx=20, pady=(0, 20))
        
        # Search section
        search_frame = ctk.CTkFrame(self.youtube_panel)
        search_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(search_frame, text="Search Query:", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20, pady=(20, 5))
        
        query_input_frame = ctk.CTkFrame(search_frame)
        query_input_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.query_entry = ctk.CTkEntry(query_input_frame, placeholder_text="e.g., BTS, BLACKPINK, K-pop")
        self.query_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        search_btn = ctk.CTkButton(
            query_input_frame,
            text="🔍 Search",
            command=self.search_youtube,
            width=100
        )
        search_btn.pack(side="right")
        
        # Results area
        self.youtube_results = ctk.CTkScrollableFrame(self.youtube_panel)
        self.youtube_results.pack(fill="both", expand=True, padx=20, pady=10)
    
    def create_data_panel(self):
        """Create the data management panel"""
        self.data_panel = ctk.CTkFrame(self.content_frame)
        
        title = ctk.CTkLabel(
            self.data_panel,
            text="Data Management",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Data operations
        operations_frame = ctk.CTkFrame(self.data_panel)
        operations_frame.pack(fill="x", padx=20, pady=10)
        
        export_btn = ctk.CTkButton(
            operations_frame,
            text="📤 Export Data",
            command=self.export_data,
            height=40
        )
        export_btn.pack(side="left", padx=20, pady=20)
        
        import_btn = ctk.CTkButton(
            operations_frame,
            text="📥 Import Data",
            command=self.import_data,
            height=40
        )
        import_btn.pack(side="left", padx=10, pady=20)
        
        clear_data_btn = ctk.CTkButton(
            operations_frame,
            text="🗑️ Clear All Data",
            command=self.clear_all_data,
            height=40,
            fg_color="red"
        )
        clear_data_btn.pack(side="right", padx=20, pady=20)
        
        # Data display
        self.data_display = ctk.CTkScrollableFrame(self.data_panel)
        self.data_display.pack(fill="both", expand=True, padx=20, pady=10)
    
    def create_settings_panel(self):
        """Create the settings panel"""
        self.settings_panel = ctk.CTkFrame(self.content_frame)
        
        title = ctk.CTkLabel(
            self.settings_panel,
            text="Settings",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Appearance settings
        appearance_frame = ctk.CTkFrame(self.settings_panel)
        appearance_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(appearance_frame, text="Appearance", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=20, pady=(20, 10))
        
        theme_frame = ctk.CTkFrame(appearance_frame)
        theme_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(theme_frame, text="Theme:", font=ctk.CTkFont(size=14)).pack(side="left", padx=20, pady=20)
        
        self.theme_option = ctk.CTkOptionMenu(
            theme_frame,
            values=["Dark", "Light", "System"],
            command=self.change_theme
        )
        self.theme_option.pack(side="left", padx=10, pady=20)
        
        # Analysis settings
        analysis_frame = ctk.CTkFrame(self.settings_panel)
        analysis_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(analysis_frame, text="Analysis Settings", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=20, pady=(20, 10))
        
        confidence_frame = ctk.CTkFrame(analysis_frame)
        confidence_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(confidence_frame, text="Confidence Threshold:", font=ctk.CTkFont(size=14)).pack(side="left", padx=20, pady=20)
        
        self.confidence_slider = ctk.CTkSlider(confidence_frame, from_=0.1, to=1.0, number_of_steps=9)
        self.confidence_slider.set(0.5)
        self.confidence_slider.pack(side="left", padx=10, pady=20, fill="x", expand=True)
        
        self.confidence_value = ctk.CTkLabel(confidence_frame, text="0.5")
        self.confidence_value.pack(side="left", padx=10, pady=20)
        
        self.confidence_slider.configure(command=self.update_confidence_value)
    
    def create_sample_chart(self):
        """Create a sample chart for demonstration"""
        # Clear existing chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(8, 6))
        fig.patch.set_facecolor('#2b2b2b')
        ax.set_facecolor('#2b2b2b')
        
        # Sample data
        labels = ['Positive', 'Negative', 'Neutral', 'Mixed']
        sizes = [45, 25, 20, 10]
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.set_title('Sentiment Distribution', color='white', fontsize=16)
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    # Event handlers
    def show_analysis_panel(self):
        """Show the analysis panel"""
        self.hide_all_panels()
        self.analysis_panel.pack(fill="both", expand=True)
        self.update_nav_button_colors("🔍 Text Analysis")
    
    def show_visualization_panel(self):
        """Show the visualization panel"""
        self.hide_all_panels()
        self.visualization_panel.pack(fill="both", expand=True)
        self.update_nav_button_colors("📊 Visualizations")
    
    def show_youtube_panel(self):
        """Show the YouTube panel"""
        self.hide_all_panels()
        self.youtube_panel.pack(fill="both", expand=True)
        self.update_nav_button_colors("🎥 YouTube Data")
    
    def show_data_panel(self):
        """Show the data management panel"""
        self.hide_all_panels()
        self.data_panel.pack(fill="both", expand=True)
        self.update_nav_button_colors("📁 Data Management")
    
    def show_settings_panel(self):
        """Show the settings panel"""
        self.hide_all_panels()
        self.settings_panel.pack(fill="both", expand=True)
        self.update_nav_button_colors("⚙️ Settings")
    
    def hide_all_panels(self):
        """Hide all content panels"""
        panels = [self.analysis_panel, self.visualization_panel, self.youtube_panel, 
                 self.data_panel, self.settings_panel]
        for panel in panels:
            panel.pack_forget()
    
    def update_nav_button_colors(self, active_button):
        """Update navigation button colors"""
        for text, button in self.nav_buttons.items():
            if text == active_button:
                button.configure(fg_color=("gray75", "gray25"))
            else:
                button.configure(fg_color=("gray85", "gray15"))
    
    def analyze_text(self):
        """Analyze the input text"""
        text = self.text_input.get("1.0", "end-1c").strip()
        
        if not text:
            messagebox.showwarning("Warning", "Please enter some text to analyze.")
            return
        
        self.status_label.configure(text="Analyzing...", text_color="orange")
        self.root.update()
        
        # Simulate analysis (replace with actual analysis)
        def run_analysis():
            import time
            time.sleep(2)  # Simulate processing time
            
            # Mock results
            result = {
                'text': text,
                'sentiment': 'Positive',
                'confidence': 0.85,
                'emotions': {'joy': 0.7, 'excitement': 0.6, 'love': 0.5},
                'risk_level': 'Low'
            }
            
            self.root.after(0, lambda: self.display_results(result))
        
        # Run analysis in separate thread
        threading.Thread(target=run_analysis, daemon=True).start()
    
    def display_results(self, result):
        """Display analysis results"""
        # Clear existing results
        for widget in self.results_content.winfo_children():
            widget.destroy()
        
        # Create results display
        results_scroll = ctk.CTkScrollableFrame(self.results_content)
        results_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Sentiment result
        sentiment_frame = ctk.CTkFrame(results_scroll)
        sentiment_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            sentiment_frame,
            text=f"Sentiment: {result['sentiment']}",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=20, pady=10)
        
        ctk.CTkLabel(
            sentiment_frame,
            text=f"Confidence: {result['confidence']:.2%}",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", padx=20, pady=(0, 10))
        
        # Risk level
        risk_frame = ctk.CTkFrame(results_scroll)
        risk_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            risk_frame,
            text=f"Risk Level: {result['risk_level']}",
            font=ctk.CTkFont(size=16)
        ).pack(anchor="w", padx=20, pady=10)
        
        # Emotions
        emotions_frame = ctk.CTkFrame(results_scroll)
        emotions_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            emotions_frame,
            text="Detected Emotions:",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=20, pady=(10, 5))
        
        for emotion, score in result['emotions'].items():
            ctk.CTkLabel(
                emotions_frame,
                text=f"  • {emotion.title()}: {score:.2%}",
                font=ctk.CTkFont(size=14)
            ).pack(anchor="w", padx=20, pady=2)
        
        ctk.CTkLabel(emotions_frame, text="").pack(pady=5)  # Spacer
        
        self.status_label.configure(text="Analysis Complete", text_color="green")
        
        # Store result
        self.current_analysis = result
        self.analysis_history.append(result)
    
    def clear_text(self):
        """Clear the text input"""
        self.text_input.delete("1.0", "end")
    
    def load_text_file(self):
        """Load text from a file"""
        file_path = filedialog.askopenfilename(
            title="Select text file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.text_input.delete("1.0", "end")
                    self.text_input.insert("1.0", content)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
    
    def search_youtube(self):
        """Search YouTube for K-Pop content"""
        query = self.query_entry.get().strip()
        api_key = self.api_key_entry.get().strip()
        
        if not query:
            messagebox.showwarning("Warning", "Please enter a search query.")
            return
        
        if not api_key:
            messagebox.showwarning("Warning", "Please enter your YouTube API key.")
            return
        
        # Clear existing results
        for widget in self.youtube_results.winfo_children():
            widget.destroy()
        
        # Show loading message
        loading_label = ctk.CTkLabel(self.youtube_results, text="Searching YouTube...")
        loading_label.pack(pady=20)
        
        # Simulate search (replace with actual YouTube API call)
        def run_search():
            import time
            time.sleep(2)
            
            # Mock results
            results = [
                {"title": f"{query} - Official Music Video", "channel": "Official Channel", "views": "10M"},
                {"title": f"{query} Live Performance", "channel": "Music Show", "views": "5M"},
                {"title": f"{query} Dance Practice", "channel": "Official Channel", "views": "3M"}
            ]
            
            self.root.after(0, lambda: self.display_youtube_results(results))
        
        threading.Thread(target=run_search, daemon=True).start()
    
    def display_youtube_results(self, results):
        """Display YouTube search results"""
        # Clear loading message
        for widget in self.youtube_results.winfo_children():
            widget.destroy()
        
        for result in results:
            result_frame = ctk.CTkFrame(self.youtube_results)
            result_frame.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(
                result_frame,
                text=result["title"],
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(anchor="w", padx=20, pady=(10, 5))
            
            ctk.CTkLabel(
                result_frame,
                text=f"{result['channel']} • {result['views']} views",
                font=ctk.CTkFont(size=12),
                text_color="gray"
            ).pack(anchor="w", padx=20, pady=(0, 10))
    
    def update_chart(self, chart_type):
        """Update the visualization chart"""
        self.create_sample_chart()  # For now, just recreate the sample chart
    
    def refresh_charts(self):
        """Refresh all charts"""
        self.create_sample_chart()
    
    def export_data(self):
        """Export analysis data"""
        if not self.analysis_history:
            messagebox.showinfo("Info", "No data to export.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export data",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv")]
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(self.analysis_history, f, indent=2, ensure_ascii=False)
                else:
                    df = pd.DataFrame(self.analysis_history)
                    df.to_csv(file_path, index=False)
                
                messagebox.showinfo("Success", f"Data exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data: {str(e)}")
    
    def import_data(self):
        """Import analysis data"""
        file_path = filedialog.askopenfilename(
            title="Import data",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv")]
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.analysis_history.extend(data)
                else:
                    df = pd.read_csv(file_path)
                    self.analysis_history.extend(df.to_dict('records'))
                
                messagebox.showinfo("Success", f"Data imported from {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import data: {str(e)}")
    
    def clear_all_data(self):
        """Clear all analysis data"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all data?"):
            self.analysis_history.clear()
            self.current_analysis = None
            messagebox.showinfo("Success", "All data cleared.")
    
    def change_theme(self, theme):
        """Change the application theme"""
        ctk.set_appearance_mode(theme.lower())
    
    def update_confidence_value(self, value):
        """Update confidence threshold value display"""
        self.confidence_value.configure(text=f"{value:.1f}")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

# Example usage
if __name__ == "__main__":
    app = KPopSentimentDesktopApp()
    app.run()