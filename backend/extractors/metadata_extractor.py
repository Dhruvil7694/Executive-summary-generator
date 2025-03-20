import os
import pdfplumber
import logging
from typing import Dict, Optional
from datetime import datetime
import re
from dateutil import parser

class MetadataExtractor:
    def extract(self, pdf_path: str,  *args, **kwargs) -> Dict[str, str]:
        """Extract and normalize metadata from a PDF file."""
        metadata_info = {
            "title": "Untitled",
            "author": "Unknown",
            "producer": "Unknown",
            "subject": "",
            "creation_date": None,
            "modification_date": None,
            "keywords": [],
            "pages": 0,
            "file_size": 0 ,
            "version": "Unknown"
        }
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                raw_metadata = pdf.metadata or {}
                metadata_info.update(self._process_raw_metadata(raw_metadata))
                metadata_info["pages"] = len(pdf.pages)
                metadata_info["file_size"] = self._get_file_size(pdf_path)
                

                
        except Exception as e:
            logging.error(f"Error extracting metadata: {e}")
            
        return metadata_info

    def _extract_additional_metadata(self, pdf) -> Dict:
        """Extract additional metadata from PDF"""
        metadata = {}
        
        try:
            # Extract document properties
            metadata.update({
                'page_size': self._get_page_size(pdf.pages[0]),
                'language': self._detect_language(pdf),
                'has_forms': any(page.forms for page in pdf.pages),
                'has_images': any(page.images for page in pdf.pages),
                'has_tables': any(page.extract_tables() for page in pdf.pages),
                'total_words': sum(len(page.extract_text().split()) for page in pdf.pages),
                'encryption': pdf.doc.is_encrypted,
                'pdf_version': pdf.doc.pdf_version
            })
            
            # Extract font information
            fonts = set()
            for page in pdf.pages:
                for font in page.chars:
                    if 'fontname' in font:
                        fonts.add(font['fontname'])
            metadata['fonts'] = list(fonts)
            
        except Exception as e:
            logging.error(f"Error extracting additional metadata: {e}")
        
        return metadata

    def _detect_language(self, pdf) -> str:
        """Detect document language"""
        try:
            # Get text sample from first few pages
            text_sample = ""
            for page in pdf.pages[:3]:
                text_sample += page.extract_text() + "\n"
            
            if text_sample.strip():
                from langdetect import detect
                return detect(text_sample)
        except Exception:
            pass
        return "unknown"

    def _get_page_size(self, page) -> Dict:
        """Extract page size information"""
        try:
            return {
                'width': float(page.width),
                'height': float(page.height),
                'units': 'points'
            }
        except Exception:
            return None
    def _process_raw_metadata(self, raw_metadata: Dict) -> Dict:
        """Process and normalize raw metadata."""
        processed = {}
        
        # Basic fields
        processed["title"] = self._clean_text(raw_metadata.get("Title", "Untitled"))
        processed["author"] = self._clean_text(raw_metadata.get("Author", "Unknown"))
        processed["producer"] = self._clean_text(raw_metadata.get("Producer", "Unknown"))
        processed["subject"] = self._clean_text(raw_metadata.get("Subject", ""))
        processed["version"] = raw_metadata.get("PDFVersion", "Unknown")
        
        # Dates
        processed["creation_date"] = self._parse_date(raw_metadata.get("CreationDate"))
        processed["modification_date"] = self._parse_date(raw_metadata.get("ModDate"))
        
        # Keywords
        keywords = raw_metadata.get("Keywords", "")
        processed["keywords"] = [k.strip() for k in keywords.split(",") if k.strip()] if keywords else []
        
        return processed

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text fields."""
        if not text or not isinstance(text, str):
            return ""
        return re.sub(r'\s+', ' ', text).strip()

    def _parse_date(self, date_str: Optional[str]) -> Optional[str]:
        """Parse PDF date formats into ISO format."""
        if not date_str:
            return None
            
        try:
            # Handle PDF date format (D:YYYYMMDDHHmmSS)
            if date_str.startswith('D:'):
                date_str = date_str[2:]  # Remove 'D:'
                return datetime(
                    int(date_str[0:4]), int(date_str[4:6]), int(date_str[6:8]),
                    int(date_str[8:10]), int(date_str[10:12]), int(date_str[12:14])
                ).isoformat()
            
            # Try parsing with dateutil for other formats
            return parser.parse(date_str).isoformat()
        except Exception as e:
            logging.warning(f"Date parsing failed for {date_str}: {e}")
            return None

    def _get_file_size(self, file_path: str) -> str:
        """Get file size in MB and KB."""
        try:
            size_in_bytes = os.path.getsize(file_path)
            size_in_mb = size_in_bytes / (1024 * 1024)  # Convert bytes to MB
            size_in_kb = size_in_bytes / 1024  # Convert bytes to KB
            return f"{size_in_mb:.2f} MB ({size_in_kb:.0f} KB)"
        except Exception as e:
            logging.error(f"Error getting file size: {e}")
            return "0.00 MB (0 KB)"




def main():
    logging.basicConfig(level=logging.INFO)
    pdf_path = "../sample/sample.pdf"
    
    # Define a simple progress tracker
    class ProgressTracker:
        def update(self, progress):
            print(f"Progress: {progress:.1f}%")
    
    try:
        extractor = MetadataExtractor()
        metadata = extractor.extract(pdf_path, ProgressTracker())
        
        # Display metadata results
        print("\nMetadata Results:")
        for key, value in metadata.items():
            print(f"{key}: {value}")
            
    except Exception as e:
        logging.error(f"Metadata extraction failed: {e}")

if __name__ == "__main__":
    main()
