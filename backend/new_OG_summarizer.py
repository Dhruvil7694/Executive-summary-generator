import pdfplumber
import io
import base64
import pandas as pd
import numpy as np
import json
import os
import re
import spacy
import logging
import math
from tqdm import tqdm
from PIL import Image
from langdetect import detect
import pytesseract
from concurrent.futures import ThreadPoolExecutor
from transformers import T5ForConditionalGeneration, T5Tokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer
import networkx as nx

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class IntegratedSummarizer:
    def __init__(self, model_name="t5-base", local_path="./models/t5_model"):
        self.local_path = local_path
        self.model_name = model_name

        # Initialize T5 model and tokenizer
        logging.info("Initializing T5 model and tokenizer...")
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)
        
        # Save locally
        self.tokenizer.save_pretrained(local_path)
        self.model.save_pretrained(local_path)

        # Initialize spaCy and BERT models
        logging.info("Loading NLP models...")
        self.nlp = spacy.load("en_core_web_trf")
        self.sentence_model = SentenceTransformer('multi-qa-mpnet-base-dot-v1')

    def initialize_progress(self, callback, start=0):
        if callback:
            callback(start)

    def update_progress(self, callback, progress):
        if callback:
            callback(progress)

    def extract_images_from_pdf(self, pdf_path, progress_callback=None):
        """Extract images from PDF with progress tracking."""
        images_data = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                for page_num, page in tqdm(enumerate(pdf.pages, 1), total=total_pages):
                    try:
                        page_image = page.to_image(resolution=300)
                        buffered = io.BytesIO()
                        page_image.original.save(buffered, format="PNG")
                        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                        images_data.append({
                            'page_number': page_num,
                            'base64_image': img_base64,
                            'description': f"Image from page {page_num}"
                        })
                        self.update_progress(progress_callback, page_num / total_pages * 10)
                    except Exception as e:
                        logging.error(f"Error processing image on page {page_num}: {e}")
        except Exception as e:
            logging.error(f"Error in image extraction: {e}")
        return images_data

    def extract_tables_from_pdf(self, pdf_path, progress_callback=None):
        """Extract tables from PDF with progress tracking."""
        tables = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                for page_num, page in tqdm(enumerate(pdf.pages, 1), total=total_pages):
                    try:
                        page_tables = page.extract_tables()
                        if page_tables:
                            for table_index, raw_table in enumerate(page_tables):
                                if raw_table and len(raw_table) > 1:
                                    df = pd.DataFrame(raw_table[1:], columns=raw_table[0])
                                    tables.append({
                                        'page_number': page_num,
                                        'table_index': table_index,
                                        'data': df.to_dict(orient='records'),
                                        'description': f"Table from page {page_num}"
                                    })
                        self.update_progress(progress_callback, 10 + (page_num / total_pages * 10))
                    except Exception as e:
                        logging.error(f"Error processing table on page {page_num}: {e}")
        except Exception as e:
            logging.error(f"Error in table extraction: {e}")
        return tables

    def extract_text_with_ocr(self, pdf_path, progress_callback=None):
        """Extract text using OCR when needed."""
        ocr_text = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                for page_num, page in tqdm(enumerate(pdf.pages, 1), total=total_pages):
                    try:
                        text = page.extract_text() or ""
                        if not text.strip():
                            image = page.to_image()
                            text = pytesseract.image_to_string(image.original.convert('L'))
                        if text.strip():
                            ocr_text.append(text.strip())
                        self.update_progress(progress_callback, 20 + (page_num / total_pages * 20))
                    except Exception as e:
                        logging.error(f"Error in OCR on page {page_num}: {e}")
        except Exception as e:
            logging.error(f"Error in text extraction: {e}")
        return "\n".join(ocr_text)

    def extract_main_idea(self, text, title=None):
        """Extract the main idea from text or title."""
        if title:
            return title.strip()
        
        doc = self.nlp(text[:5000])  # Process first 5000 chars for efficiency
        keywords = [chunk.text for chunk in doc.noun_chunks]
        return ' '.join(set(keywords))[:100]

    def extract_key_sentences(self, text, num_sentences=5):
        """Extract key sentences using BERT embeddings and TextRank."""
        sentences = sent_tokenize(text)
        unique_sentences = list(set(sentences))

        if len(unique_sentences) < num_sentences:
            return unique_sentences

        embeddings = self.sentence_model.encode(unique_sentences, show_progress_bar=False)
        similarity_matrix = np.inner(embeddings, embeddings)
        nx_graph = nx.from_numpy_array(similarity_matrix)
        scores = nx.pagerank(nx_graph)

        top_indices = sorted(scores, key=scores.get, reverse=True)[:num_sentences]
        return [unique_sentences[i] for i in sorted(top_indices)]

    def split_text_into_chunks(self, text, chunk_size=2000):
        """Split text into chunks preserving sentence boundaries."""
        sentences = sent_tokenize(text)
        chunks, current_chunk = [], []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence) + 1
            if current_length + sentence_length > chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
                
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        return chunks

    def summarize_chunk(self, chunk, max_length=200, min_length=50):
        """Summarize a single chunk of text."""
        inputs = self.tokenizer.encode(
            "summarize: " + chunk,
            return_tensors="pt",
            max_length=1024,
            truncation=True
        )

        summary_ids = self.model.generate(
            inputs,
            max_length=max_length,
            min_length=min_length,
            length_penalty=2.0,
            num_beams=4,
            early_stopping=True
        )

        return self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    def process_pdf(self, pdf_path, user_feedback=None, progress_callback=None):
        """Main function to process and summarize PDF content."""
        try:
            self.initialize_progress(progress_callback, 0)
            
            # Extract metadata
            metadata = self.get_pdf_metadata(pdf_path)
            
            # Extract content
            text = self.extract_text_with_ocr(pdf_path, progress_callback)
            images = self.extract_images_from_pdf(pdf_path, progress_callback)
            tables = self.extract_tables_from_pdf(pdf_path, progress_callback)
            
            if not text.strip():
                raise ValueError("No readable text found in the PDF")

            # Process text
            word_count = len(text.split())
            reading_time = max(1, math.ceil(word_count / 200))
            language = detect(text)
            
            # Generate summary
            chunks = self.split_text_into_chunks(text)
            summaries = []
            
            for i, chunk in enumerate(chunks):
                summary = self.summarize_chunk(chunk)
                summaries.append(summary)
                self.update_progress(progress_callback, 50 + (i / len(chunks) * 40))

            text_summary = self.format_summary(
                self.extract_main_idea(text, metadata.get('title')),
                "\n".join(summaries)
            )

            self.update_progress(progress_callback, 100)
            
            # Handle feedback if provided
            if user_feedback:
                self.process_feedback(user_feedback)

            return {
                "summary": {
                    "text": text_summary,
                    "language": language,
                    "word_count": word_count,
                    "reading_time_minutes": reading_time
                },
                "metadata": metadata,
                "images": images,
                "tables": tables
            }

        except Exception as e:
            logging.error(f"Error processing PDF: {e}")
            raise

    def get_pdf_metadata(self, pdf_path):
        """Extract metadata from PDF."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                metadata = pdf.metadata or {}
                return {
                    "title": metadata.get("Title", "Untitled"),
                    "author": metadata.get("Author", "Unknown"),
                    "producer": metadata.get("Producer", "Unknown"),
                    "subject": metadata.get("Subject", "")
                }
        except Exception as e:
            logging.error(f"Error extracting metadata: {e}")
            return {}

    def format_summary(self, main_idea, summary):
        """Format the summary with structure and coherence."""
        if not summary:
            return ""

        summary_points = summary.split('. ')
        formatted_summary = f"Main Idea: {main_idea}\n\nKey Points:\n"
        
        for point in summary_points:
            if point.strip():
                formatted_summary += f"• {point.strip()}.\n"
        
        return formatted_summary.strip()

    def process_feedback(self, feedback):
        """Process and store user feedback."""
        feedback_file = "feedback_data.json"
        try:
            if os.path.exists(feedback_file):
                with open(feedback_file, 'r') as f:
                    feedback_data = json.load(f)
            else:
                feedback_data = []
                
            feedback_data.append(feedback)
            
            with open(feedback_file, 'w') as f:
                json.dump(feedback_data, f, indent=4)
                
            self.analyze_feedback(feedback_data)
            
        except Exception as e:
            logging.error(f"Error processing feedback: {e}")

    def analyze_feedback(self, feedback_data):
        """Analyze collected feedback data."""
        if not feedback_data:
            return
            
        try:
            total_rating = sum(entry.get('rating', 0) for entry in feedback_data)
            avg_rating = total_rating / len(feedback_data)
            logging.info(f"Average feedback rating: {avg_rating:.2f} ({len(feedback_data)} entries)")
        except Exception as e:
            logging.error(f"Error analyzing feedback: {e}")

# Usage example:
if __name__ == "__main__":
    summarizer = IntegratedSummarizer()
    pdf_path = "example.pdf"
    
    try:
        result = summarizer.process_pdf(pdf_path)
        print("Summary:", result["summary"]["text"])
        print(f"Word count: {result['summary']['word_count']}")
        print(f"Reading time: {result['summary']['reading_time_minutes']} minutes")
    except Exception as e:
        print(f"Error processing PDF: {e}")