"""
Image Processing Example using Pillow
Demonstrates image analysis and processing for K-Pop sentiment analysis
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import pytesseract
import cv2
import numpy as np
import os
import requests
from io import BytesIO
import json
from datetime import datetime

class KPopImageSentimentAnalyzer:
    def __init__(self):
        """Initialize the image sentiment analyzer"""
        # Configure pytesseract (you may need to set the path to tesseract executable)
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows
        
        # Common K-Pop related terms for text analysis
        self.kpop_keywords = [
            'BTS', 'BLACKPINK', 'TWICE', 'Stray Kids', 'ITZY', 'aespa',
            'comeback', 'debut', 'MV', 'music video', 'performance',
            'concert', 'tour', 'album', 'single', 'choreography',
            'bias', 'stan', 'fandom', 'ARMY', 'Blink', 'Once'
        ]
        
        # Sentiment keywords for extracted text
        self.sentiment_keywords = {
            'positive': ['love', 'amazing', 'perfect', 'incredible', 'best', 'beautiful', 'talented'],
            'negative': ['hate', 'terrible', 'worst', 'awful', 'disappointing', 'bad'],
            'neutral': ['okay', 'fine', 'normal', 'average']
        }

    def extract_text_from_image(self, image_path):
        """
        Extract text from K-Pop images using OCR
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            dict: Extracted text and metadata
        """
        try:
            # Load image
            if isinstance(image_path, str):
                image = Image.open(image_path)
            else:
                image = image_path
            
            # Preprocess image for better OCR
            processed_image = self.preprocess_image_for_ocr(image)
            
            # Extract text using pytesseract
            extracted_text = pytesseract.image_to_string(processed_image, lang='eng')
            
            # Get detailed OCR data
            ocr_data = pytesseract.image_to_data(processed_image, output_type=pytesseract.Output.DICT)
            
            # Filter and clean text
            cleaned_text = self.clean_extracted_text(extracted_text)
            
            # Analyze K-Pop relevance
            kpop_relevance = self.analyze_kpop_relevance(cleaned_text)
            
            result = {
                'raw_text': extracted_text,
                'cleaned_text': cleaned_text,
                'kpop_relevance': kpop_relevance,
                'ocr_confidence': self.calculate_ocr_confidence(ocr_data),
                'detected_keywords': self.find_kpop_keywords(cleaned_text),
                'text_sentiment': self.analyze_text_sentiment(cleaned_text)
            }
            
            return result
            
        except Exception as e:
            return {'error': f"Failed to extract text: {str(e)}"}

    def preprocess_image_for_ocr(self, image):
        """
        Preprocess image to improve OCR accuracy
        
        Args:
            image (PIL.Image): Input image
            
        Returns:
            PIL.Image: Processed image
        """
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize image if too small
        width, height = image.size
        if width < 300 or height < 300:
            scale_factor = max(300/width, 300/height)
            new_size = (int(width * scale_factor), int(height * scale_factor))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.2)
        
        # Convert to grayscale for better OCR
        image = image.convert('L')
        
        # Apply slight blur to reduce noise
        image = image.filter(ImageFilter.MedianFilter(size=3))
        
        return image

    def clean_extracted_text(self, text):
        """
        Clean and normalize extracted text
        
        Args:
            text (str): Raw extracted text
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace and newlines
        cleaned = ' '.join(text.split())
        
        # Remove special characters but keep basic punctuation
        import re
        cleaned = re.sub(r'[^\w\s\.\!\?\,\-\:]', '', cleaned)
        
        return cleaned.strip()

    def analyze_kpop_relevance(self, text):
        """
        Analyze how relevant the text is to K-Pop
        
        Args:
            text (str): Input text
            
        Returns:
            dict: Relevance analysis
        """
        if not text:
            return {'score': 0, 'keywords_found': []}
        
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in self.kpop_keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
        
        # Calculate relevance score
        relevance_score = len(found_keywords) / len(self.kpop_keywords)
        
        return {
            'score': relevance_score,
            'keywords_found': found_keywords,
            'is_kpop_related': relevance_score > 0.1
        }

    def calculate_ocr_confidence(self, ocr_data):
        """
        Calculate average OCR confidence
        
        Args:
            ocr_data (dict): OCR data from pytesseract
            
        Returns:
            float: Average confidence score
        """
        confidences = [int(conf) for conf in ocr_data['conf'] if int(conf) > 0]
        return sum(confidences) / len(confidences) if confidences else 0

    def find_kpop_keywords(self, text):
        """
        Find K-Pop related keywords in text
        
        Args:
            text (str): Input text
            
        Returns:
            list: Found keywords
        """
        if not text:
            return []
        
        text_lower = text.lower()
        found = []
        
        for keyword in self.kpop_keywords:
            if keyword.lower() in text_lower:
                found.append(keyword)
        
        return found

    def analyze_text_sentiment(self, text):
        """
        Analyze sentiment of extracted text
        
        Args:
            text (str): Input text
            
        Returns:
            dict: Sentiment analysis
        """
        if not text:
            return {'sentiment': 'neutral', 'score': 0}
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in self.sentiment_keywords['positive'] if word in text_lower)
        negative_count = sum(1 for word in self.sentiment_keywords['negative'] if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = 'positive'
            score = positive_count / (positive_count + negative_count + 1)
        elif negative_count > positive_count:
            sentiment = 'negative'
            score = negative_count / (positive_count + negative_count + 1)
        else:
            sentiment = 'neutral'
            score = 0
        
        return {'sentiment': sentiment, 'score': score}

    def analyze_visual_sentiment(self, image_path):
        """
        Analyze visual sentiment from image colors and composition
        
        Args:
            image_path (str): Path to image file
            
        Returns:
            dict: Visual sentiment analysis
        """
        try:
            # Load image
            if isinstance(image_path, str):
                image = Image.open(image_path)
            else:
                image = image_path
            
            # Convert to RGB
            image = image.convert('RGB')
            
            # Analyze color distribution
            color_analysis = self.analyze_color_sentiment(image)
            
            # Analyze brightness and contrast
            brightness_analysis = self.analyze_brightness_sentiment(image)
            
            # Combine analyses
            visual_sentiment = self.combine_visual_analyses(color_analysis, brightness_analysis)
            
            return {
                'color_sentiment': color_analysis,
                'brightness_sentiment': brightness_analysis,
                'overall_visual_sentiment': visual_sentiment
            }
            
        except Exception as e:
            return {'error': f"Failed to analyze visual sentiment: {str(e)}"}

    def analyze_color_sentiment(self, image):
        """
        Analyze sentiment based on color distribution
        
        Args:
            image (PIL.Image): Input image
            
        Returns:
            dict: Color sentiment analysis
        """
        # Resize for faster processing
        image = image.resize((100, 100))
        
        # Get color data
        colors = image.getdata()
        
        # Calculate average RGB values
        r_avg = sum(color[0] for color in colors) / len(colors)
        g_avg = sum(color[1] for color in colors) / len(colors)
        b_avg = sum(color[2] for color in colors) / len(colors)
        
        # Analyze color sentiment
        # Warm colors (red, orange, yellow) tend to be more energetic/positive
        # Cool colors (blue, green, purple) tend to be more calm/neutral
        
        warmth_score = (r_avg + (g_avg * 0.5)) / 255
        coolness_score = (b_avg + (g_avg * 0.5)) / 255
        
        if warmth_score > coolness_score:
            color_sentiment = 'warm/energetic'
            sentiment_score = warmth_score
        else:
            color_sentiment = 'cool/calm'
            sentiment_score = coolness_score
        
        return {
            'dominant_sentiment': color_sentiment,
            'score': sentiment_score,
            'avg_rgb': [r_avg, g_avg, b_avg],
            'warmth_score': warmth_score,
            'coolness_score': coolness_score
        }

    def analyze_brightness_sentiment(self, image):
        """
        Analyze sentiment based on brightness and contrast
        
        Args:
            image (PIL.Image): Input image
            
        Returns:
            dict: Brightness sentiment analysis
        """
        # Convert to grayscale
        gray_image = image.convert('L')
        
        # Get brightness data
        brightness_data = list(gray_image.getdata())
        
        # Calculate statistics
        avg_brightness = sum(brightness_data) / len(brightness_data)
        brightness_std = np.std(brightness_data)
        
        # Analyze sentiment
        # Brighter images tend to be more positive
        # Higher contrast (std) tends to be more dynamic/energetic
        
        brightness_sentiment = 'positive' if avg_brightness > 128 else 'negative'
        contrast_level = 'high' if brightness_std > 50 else 'low'
        
        return {
            'brightness_sentiment': brightness_sentiment,
            'avg_brightness': avg_brightness,
            'contrast_level': contrast_level,
            'contrast_score': brightness_std,
            'energy_level': 'high' if brightness_std > 50 and avg_brightness > 100 else 'low'
        }

    def combine_visual_analyses(self, color_analysis, brightness_analysis):
        """
        Combine color and brightness analyses for overall visual sentiment
        
        Args:
            color_analysis (dict): Color analysis results
            brightness_analysis (dict): Brightness analysis results
            
        Returns:
            dict: Combined visual sentiment
        """
        # Simple combination logic
        positive_indicators = 0
        
        if color_analysis['dominant_sentiment'] == 'warm/energetic':
            positive_indicators += 1
        
        if brightness_analysis['brightness_sentiment'] == 'positive':
            positive_indicators += 1
        
        if brightness_analysis['energy_level'] == 'high':
            positive_indicators += 1
        
        # Determine overall sentiment
        if positive_indicators >= 2:
            overall_sentiment = 'positive'
            confidence = positive_indicators / 3
        elif positive_indicators == 1:
            overall_sentiment = 'neutral'
            confidence = 0.5
        else:
            overall_sentiment = 'negative'
            confidence = (3 - positive_indicators) / 3
        
        return {
            'sentiment': overall_sentiment,
            'confidence': confidence,
            'positive_indicators': positive_indicators
        }

    def create_sentiment_overlay(self, image_path, sentiment_data, output_path=None):
        """
        Create an image with sentiment analysis overlay
        
        Args:
            image_path (str): Path to original image
            sentiment_data (dict): Sentiment analysis results
            output_path (str): Path to save output image
            
        Returns:
            PIL.Image: Image with overlay
        """
        try:
            # Load original image
            image = Image.open(image_path)
            
            # Create a copy for overlay
            overlay_image = image.copy()
            draw = ImageDraw.Draw(overlay_image)
            
            # Try to load a font (fallback to default if not available)
            try:
                font_large = ImageFont.truetype("arial.ttf", 24)
                font_small = ImageFont.truetype("arial.ttf", 16)
            except:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Get image dimensions
            width, height = image.size
            
            # Create semi-transparent overlay
            overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            
            # Draw background for text
            text_bg_height = 120
            overlay_draw.rectangle(
                [(0, height - text_bg_height), (width, height)],
                fill=(0, 0, 0, 180)
            )
            
            # Combine overlay with image
            overlay_image = Image.alpha_composite(overlay_image.convert('RGBA'), overlay)
            draw = ImageDraw.Draw(overlay_image)
            
            # Add sentiment information
            y_offset = height - 110
            
            # Overall sentiment
            if 'overall_visual_sentiment' in sentiment_data:
                sentiment = sentiment_data['overall_visual_sentiment']['sentiment']
                confidence = sentiment_data['overall_visual_sentiment']['confidence']
                
                # Choose color based on sentiment
                color = {
                    'positive': (0, 255, 0),
                    'negative': (255, 0, 0),
                    'neutral': (255, 255, 0)
                }.get(sentiment, (255, 255, 255))
                
                draw.text((10, y_offset), f"Visual Sentiment: {sentiment.upper()}", 
                         fill=color, font=font_large)
                draw.text((10, y_offset + 30), f"Confidence: {confidence:.2%}", 
                         fill=(255, 255, 255), font=font_small)
            
            # Text sentiment (if available)
            if 'text_sentiment' in sentiment_data:
                text_sentiment = sentiment_data['text_sentiment']['sentiment']
                draw.text((10, y_offset + 60), f"Text Sentiment: {text_sentiment}", 
                         fill=(255, 255, 255), font=font_small)
            
            # K-Pop relevance (if available)
            if 'kpop_relevance' in sentiment_data:
                relevance = sentiment_data['kpop_relevance']['score']
                draw.text((10, y_offset + 80), f"K-Pop Relevance: {relevance:.2%}", 
                         fill=(255, 255, 255), font=font_small)
            
            # Save if output path provided
            if output_path:
                overlay_image.save(output_path)
            
            return overlay_image.convert('RGB')
            
        except Exception as e:
            print(f"Error creating overlay: {str(e)}")
            return image

    def process_thumbnail_grid(self, thumbnail_urls, grid_size=(3, 3)):
        """
        Process a grid of YouTube thumbnails for sentiment analysis
        
        Args:
            thumbnail_urls (list): List of thumbnail URLs
            grid_size (tuple): Grid dimensions (rows, cols)
            
        Returns:
            dict: Analysis results for all thumbnails
        """
        results = []
        
        for i, url in enumerate(thumbnail_urls[:grid_size[0] * grid_size[1]]):
            try:
                # Download thumbnail
                response = requests.get(url)
                thumbnail = Image.open(BytesIO(response.content))
                
                # Analyze thumbnail
                text_analysis = self.extract_text_from_image(thumbnail)
                visual_analysis = self.analyze_visual_sentiment(thumbnail)
                
                result = {
                    'thumbnail_index': i,
                    'url': url,
                    'text_analysis': text_analysis,
                    'visual_analysis': visual_analysis,
                    'timestamp': datetime.now().isoformat()
                }
                
                results.append(result)
                
            except Exception as e:
                results.append({
                    'thumbnail_index': i,
                    'url': url,
                    'error': str(e)
                })
        
        return {
            'total_processed': len(results),
            'grid_size': grid_size,
            'results': results,
            'summary': self.summarize_thumbnail_analysis(results)
        }

    def summarize_thumbnail_analysis(self, results):
        """
        Summarize analysis results from multiple thumbnails
        
        Args:
            results (list): List of analysis results
            
        Returns:
            dict: Summary statistics
        """
        valid_results = [r for r in results if 'error' not in r]
        
        if not valid_results:
            return {'error': 'No valid results to summarize'}
        
        # Count sentiments
        visual_sentiments = []
        text_sentiments = []
        kpop_relevance_scores = []
        
        for result in valid_results:
            if 'visual_analysis' in result and 'overall_visual_sentiment' in result['visual_analysis']:
                visual_sentiments.append(result['visual_analysis']['overall_visual_sentiment']['sentiment'])
            
            if 'text_analysis' in result and 'text_sentiment' in result['text_analysis']:
                text_sentiments.append(result['text_analysis']['text_sentiment']['sentiment'])
            
            if 'text_analysis' in result and 'kpop_relevance' in result['text_analysis']:
                kpop_relevance_scores.append(result['text_analysis']['kpop_relevance']['score'])
        
        # Calculate statistics
        summary = {
            'total_thumbnails': len(valid_results),
            'visual_sentiment_distribution': {
                sentiment: visual_sentiments.count(sentiment) 
                for sentiment in set(visual_sentiments)
            } if visual_sentiments else {},
            'text_sentiment_distribution': {
                sentiment: text_sentiments.count(sentiment) 
                for sentiment in set(text_sentiments)
            } if text_sentiments else {},
            'avg_kpop_relevance': sum(kpop_relevance_scores) / len(kpop_relevance_scores) 
                                 if kpop_relevance_scores else 0
        }
        
        return summary

# Example usage and testing
if __name__ == "__main__":
    analyzer = KPopImageSentimentAnalyzer()
    
    # Example 1: Create a sample image with text for testing
    def create_sample_image():
        """Create a sample image with K-Pop text for testing"""
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        text = "BTS LOVE YOURSELF\nAmazing Performance!\nBest K-Pop Group Ever"
        draw.text((50, 50), text, fill='black', font=font)
        
        img.save('sample_kpop_image.jpg')
        return 'sample_kpop_image.jpg'
    
    # Create and analyze sample image
    print("Creating sample K-Pop image...")
    sample_image_path = create_sample_image()
    
    print("Analyzing text extraction...")
    text_result = analyzer.extract_text_from_image(sample_image_path)
    print(f"Extracted text: {text_result.get('cleaned_text', 'None')}")
    print(f"K-Pop relevance: {text_result.get('kpop_relevance', {}).get('score', 0):.2%}")
    print(f"Found keywords: {text_result.get('detected_keywords', [])}")
    
    print("\nAnalyzing visual sentiment...")
    visual_result = analyzer.analyze_visual_sentiment(sample_image_path)
    if 'overall_visual_sentiment' in visual_result:
        sentiment = visual_result['overall_visual_sentiment']
        print(f"Visual sentiment: {sentiment['sentiment']} (confidence: {sentiment['confidence']:.2%})")
    
    print("\nCreating sentiment overlay...")
    combined_data = {**text_result, **visual_result}
    overlay_image = analyzer.create_sentiment_overlay(
        sample_image_path, 
        combined_data, 
        'sample_with_overlay.jpg'
    )
    print("Overlay image saved as 'sample_with_overlay.jpg'")
    
    # Clean up
    if os.path.exists(sample_image_path):
        os.remove(sample_image_path)
    
    print("\nImage processing example completed!")