import pdfplumber
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TextExtractor:
    def __init__(self):
        """Initialize TextExtractor."""
        self.logger = logging.getLogger(__name__)

    def extract_text_with_plumber(self, pdf_path):
        """Extract text using pdfplumber."""
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            self.logger.info("Text extraction with pdfplumber completed.")
        except Exception as e:
            self.logger.error(f"Error with pdfplumber: {e}")
        return text

    def extract_text_with_pymupdf(self, pdf_path):
        """Extract text using PyMuPDF."""
        text = ""
        try:
            doc = fitz.open(pdf_path)
            for page in doc:
                text += page.get_text()
            self.logger.info("Text extraction with PyMuPDF completed.")
        except Exception as e:
            self.logger.error(f"Error with PyMuPDF: {e}")
        return text

    def extract_text_with_ocr(self, pdf_path):
        """Extract text using OCR for scanned PDFs."""
        text = ""
        try:
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                pix = doc[page_num].get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                text += pytesseract.image_to_string(img, config='--psm 6', lang='eng')
            self.logger.info("Text extraction with OCR completed.")
        except Exception as e:
            self.logger.error(f"Error with OCR: {e}")
        return text


    def extract(self, pdf_path):
        """
        Extract text from PDF using multiple methods if needed
        
        Args:
            pdf_path (str): Path to the PDF file
        
        Returns:
            str: Extracted text
        """
        self.logger.info(f"Extracting text from: {pdf_path}")

        # Try different extraction methods in order
        text = self.extract_text_with_plumber(pdf_path)
        if not text.strip():
            text = self.extract_text_with_pymupdf(pdf_path)
        if not text.strip():
            text = self.extract_text_with_ocr(pdf_path)

        return text

if __name__ == "__main__":
    pdf_path = "../sample/sample.pdf"  # Replace with your PDF file path
    extractor = TextExtractor()
    extracted_text = extractor.extract(pdf_path)
    print("Extracted Text:")
    print(extracted_text)