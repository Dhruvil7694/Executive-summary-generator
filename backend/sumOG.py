import pdfplumber
import io
import base64
import pandas as pd
from langdetect import detect
import pytesseract
from PIL import Image
import math
import logging
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from models.summarization_model import SummarizationModel
from models.audio import generate_audio

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize summarization model
summarizer = SummarizationModel(local_path="./backend/models/bart_model")

def initialize_progress(callback, start=0):
    if callback:
        callback(start)

def update_progress(callback, progress):
    if callback:
        callback(progress)

def extract_images_from_pdf(pdf_path, progress_callback=None):
    """Extract high-quality images from PDF with progress tracking."""
    images_data = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            for page_num, page in tqdm(enumerate(pdf.pages, 1), total=total_pages, desc="Extracting Images", unit="page"):
                try:
                    page_image = page.to_image(resolution=300)
                    buffered = io.BytesIO()
                    page_image.original.save(buffered, format="PNG")
                    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                    image_description = f"Image extracted from page {page_num}"
                    images_data.append({
                        'page_number': page_num,
                        'base64_image': img_base64,
                        'description': image_description
                    })
                    update_progress(progress_callback, page_num / total_pages * 10)
                except Exception as e:
                    logging.error(f"Error processing image on page {page_num}: {e}")
    except Exception as e:
        logging.error(f"Error opening PDF for image extraction: {e}")
    return images_data

def extract_tables_from_pdf(pdf_path, progress_callback=None):
    """Extract tables from PDF with progress tracking."""
    tables = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            for page_num, page in tqdm(enumerate(pdf.pages, 1), total=total_pages, desc="Extracting Tables", unit="page"):
                try:
                    page_tables = page.extract_tables()
                    if page_tables:
                        for table_index, raw_table in enumerate(page_tables):
                            if raw_table and len(raw_table) > 1:
                                df = pd.DataFrame(raw_table[1:], columns=raw_table[0])
                                table_records = df.to_dict(orient='records')
                                table_description = f"Table extracted from page {page_num}, index {table_index}"
                                tables.append({
                                    'page_number': page_num,
                                    'table_index': table_index,
                                    'data': table_records,
                                    'description': table_description
                                })
                    update_progress(progress_callback, 10 + (page_num / total_pages * 10))
                except Exception as e:
                    logging.error(f"Error processing table on page {page_num}: {e}")
    except Exception as e:
        logging.error(f"Error opening PDF for table extraction: {e}")
    return tables

def count_words(text):
    """Count words in text."""
    return len(text.split()) if text else 0

def estimate_reading_time(word_count, words_per_minute=200):
    """Estimate reading time based on word count."""
    return max(1, math.ceil(word_count / words_per_minute))

def get_pdf_metadata(pdf_path):
    """Extract metadata from the PDF file."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            metadata = pdf.metadata or {}
            return {
                "title": metadata.get("Title", "Untitled Document"),
                "producer": metadata.get("Producer", "Unknown"),
                "author": metadata.get("Author", "Unknown"),
                "subject": metadata.get("Subject", "No Subject")
            }
    except Exception as e:
        logging.error(f"Error extracting metadata: {e}")
        return {}

def extract_text_with_ocr(pdf_path, progress_callback=None):
    """Use OCR to extract text from non-readable PDFs."""
    ocr_text = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            for page_num, page in tqdm(enumerate(pdf.pages, 1), total=total_pages, desc="OCR Text Extraction", unit="page"):
                try:
                    text = page.extract_text() or ""
                    if not text.strip():
                        image = page.to_image()
                        text = pytesseract.image_to_string(image.original.convert('L'), lang="eng")
                    if text.strip():
                        ocr_text.append(text.strip())
                    update_progress(progress_callback, 20 + (page_num / total_pages * 20))
                except Exception as e:
                    logging.error(f"Error performing OCR on page {page_num}: {e}")
    except Exception as e:
        logging.error(f"Error opening PDF for OCR: {e}")
    return "\n".join(ocr_text)

def split_text_into_chunks(text, chunk_size=2000):
    """Split text into chunks without breaking sentences."""
    sentences = text.split('.')
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

def summarize_text_in_chunks(text, progress_callback=None, chunk_size=2000):
    """Summarize text in chunks to handle large documents efficiently."""
    if not text or not text.strip():
        logging.warning("No valid text available for summarization.")
        return ""

    chunks = split_text_into_chunks(text, chunk_size)
    summaries = []

    for i, chunk in tqdm(enumerate(chunks), total=len(chunks), desc="Text Summarization", unit="chunk"):
        try:
            summary = summarizer.summarize(chunk, max_length=200, min_length=50)
            summaries.append(summary)
            update_progress(progress_callback, 50 + (i / len(chunks) * 30))
        except Exception as e:
            logging.error(f"Error summarizing chunk {i + 1}: {e}")

    return "\n\n".join(summaries)

def summarize_pdf(pdf_path, user_feedback=None, progress_callback=None):
    """Main function to summarize the PDF document with robust handling of content."""
    try:
        initialize_progress(progress_callback, 0)

        text = extract_text_with_ocr(pdf_path, progress_callback)
        if not text or not text.strip():
            raise ValueError("No readable text found in the PDF.")

        images = extract_images_from_pdf(pdf_path, progress_callback)
        tables = extract_tables_from_pdf(pdf_path, progress_callback)

        word_count = count_words(text)
        reading_time = estimate_reading_time(word_count)
        language = detect(text) if text else "unknown"

        summary_text = summarize_text_in_chunks(text, progress_callback)
        audio_path = generate_audio(summary_text)

        metadata = get_pdf_metadata(pdf_path)

        if user_feedback:
            summarizer.feedback_loop(user_feedback)

        update_progress(progress_callback, 100)

        return {
            "summary": {
                "text_summary": summary_text,
                "language": language,
                "word_count": word_count,
                "reading_time": reading_time
            },
            "metadata": metadata,
            "images": images,
            "tables": tables,
            "audio_path": audio_path
        }

    except Exception as e:
        logging.error(f"Error processing PDF: {e}")
        raise
