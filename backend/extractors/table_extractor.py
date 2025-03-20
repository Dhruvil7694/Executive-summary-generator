from dataclasses import dataclass, field
import os
from pathlib import Path
import re
import pytesseract
import pdfplumber
import pandas as pd
import logging
from typing import List, Dict, Any, Optional

@dataclass
class ExtractorConfig:
    MIN_WIDTH: int = 100
    MIN_HEIGHT: int = 100
    MAX_WIDTH: int = 4000
    MAX_HEIGHT: int = 4000
    FORMATS: List[str] = field(default_factory=lambda: ['jpg', 'png', 'jpeg'])
    DPI: int = 300
    DEFAULT_DPI: int = 300
    min_rows: int = 2  # Added missing configuration
    min_cols: int = 2  # Added missing configuration
    max_empty_ratio: float = 0.5  # Added missing configuration

class TableExtractor:
    def __init__(self, config: ExtractorConfig = None):
        self.config = config or ExtractorConfig()
        self._setup_logging()
        
    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
    def _ocr_table_extraction(self, page) -> List[Dict[str, Any]]:
        """Perform OCR on table regions."""
        ocr_tables = []
        try:
            # Use DPI from config
            image = page.to_image(resolution=self.config.DPI)
            text = pytesseract.image_to_string(
                image.original,
                config='--psm 6'
            )
            ocr_tables.extend(self._parse_ocr_text_into_tables(text))
        except Exception as e:
            logging.warning(f"OCR table extraction failed: {e}")
        return ocr_tables

    def _is_valid_table(self, table):
        """Validate table structure and content."""
        if not table or len(table) < self.config.min_rows:
            return False
            
        # Check if each row has at least min_cols columns
        if not all(row and len(row) >= self.config.min_cols for row in table):
            return False
            
        # Check for empty cell ratio
        total_cells = sum(len(row) for row in table)
        empty_cells = sum(1 for row in table for cell in row if not cell or str(cell).strip() == '')
        
        return (empty_cells / total_cells) < self.config.max_empty_ratio
        
    def _improve_table_detection(self, page) -> List[List[List[str]]]:
        """Enhanced table detection with multiple methods and settings."""
        tables = []
        
        # Try different table extraction settings
        extraction_settings = [
            {},  # Default settings
            {
                "vertical_strategy": "text",
                "horizontal_strategy": "text",
                "intersection_x_tolerance": 3,
                "intersection_y_tolerance": 3
            },
            {
                "vertical_strategy": "lines",
                "horizontal_strategy": "lines",
                "intersection_x_tolerance": 5,
                "intersection_y_tolerance": 5
            }
        ]
        
        for settings in extraction_settings:
            try:
                detected_tables = page.extract_tables(**settings)
                if detected_tables:
                    tables.extend(detected_tables)
            except Exception as e:
                logging.debug(f"Table detection failed with settings {settings}: {e}")
                continue
        
        # Deduplicate tables
        seen = set()
        unique_tables = []
        
        for table in tables:
            if table:  # Skip empty tables
                table_hash = str(table)  # Simple hashing method
                if table_hash not in seen:
                    seen.add(table_hash)
                    unique_tables.append(table)
        
        return unique_tables
    
    def validate_table(self, table: List[List]) -> bool:
        """Validate the table structure and content."""
        return self._validate_table_content(table)
    
    def _parse_ocr_text_into_tables(self, text: str) -> List[Dict[str, Any]]:
        """Parse OCR text into table-like structures."""
        tables = []
        lines = text.split('\n')
        current_table = []
        
        for line in lines:
            # Assuming columns are separated by spaces or tabs, adjust this as necessary
            row = line.split()  # Adjust this split logic based on your OCR output
            if row:  # Only add non-empty rows
                current_table.append(row)
            if len(current_table) > 1 and len(row) == 1:  # Heuristic: end of table
                tables.append(current_table)
                current_table = []
        if current_table:  # Append the last table if it exists
            tables.append(current_table)
        return tables


    def _validate_table_content(self, table: List[List]) -> bool:
        """Enhanced table validation"""
        if not table or len(table) < 1:  # Table should have at least one row
            return False
                
        # Check if the first row seems to be a header or if it is just data
        header = table[0] if len(table) > 1 and isinstance(table[0], list) else []  # No header handling

        # Handle the case where there is no header or invalid rows
        if not header:
            header = [f"Column {i+1}" for i in range(len(table[0]))]  # Default headers like Column 1, Column 2...
        
        rows = table[1:]  # Data rows after the header

        # Row consistency check
        row_lengths = set(len(row) for row in rows)
        if len(row_lengths) != 1:  # All rows should have the same number of columns
            return False
        
        return True
    
    def extract(self, pdf_path: Path, progress_tracker=None) -> List[Dict[str, Any]]:
        """Extract tables from PDF with progress tracking."""
        tables = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        # First try regular table extraction
                        extracted_tables = self._improve_table_detection(page)
                        
                        for table_idx, table in enumerate(extracted_tables):
                            if self._is_valid_table(table):
                                processed_table = self._process_table(table, page_num, table_idx)
                                if processed_table:
                                    tables.append(processed_table)
                        
                        # If no tables found, try OCR
                        if not extracted_tables:
                            ocr_tables = self._ocr_table_extraction(page)
                            for ocr_idx, ocr_table in enumerate(ocr_tables):
                                if self._is_valid_table(ocr_table):
                                    processed_table = self._process_table(
                                        ocr_table, 
                                        page_num, 
                                        len(tables) + ocr_idx
                                    )
                                    if processed_table:
                                        tables.append(processed_table)
                        
                        # Update progress if tracker provided
                        if progress_tracker:
                            progress = (page_num / total_pages) * 100
                            progress_tracker.update(progress)
                            
                    except Exception as e:
                        logging.error(f"Error processing page {page_num}: {str(e)}")
                        continue
                        
        except Exception as e:
            logging.error(f"Failed to process PDF: {str(e)}")
            raise
            
        return tables


    
    def _process_page_tables(self, page, page_num):
        page_tables = []
        
        try:
            raw_tables = page.extract_tables()  # Extract tables from the page
            
            for table_idx, raw_table in enumerate(raw_tables):
                if self._is_valid_table(raw_table):  # Validate table
                    processed_table = self._process_table(raw_table, page_num, table_idx)
                    if processed_table:
                        page_tables.append(processed_table)
                        
        except Exception as e:
            logging.error(f"Error processing tables on page {page_num}: {e}")
            
        return page_tables

    
    def _process_table(self, raw_table, page_num, table_idx):
        """Process and clean table data."""
        try:
            df = self._clean_table_data(raw_table)
            if df.empty:
                return None

            return {
                'page_number': page_num,
                'table_index': table_idx,
                'data': df.to_dict(orient='records'),
                'headers': df.columns.tolist(),
                'rows': len(df),
                'columns': len(df.columns),
                'description': self._generate_table_description(df)
            }

        except Exception as e:
            logging.error(f"Error processing table: {e}")
            return None


    def _clean_table_data(self, raw_table):
        """Clean and structure table data with improved error handling."""
        try:
            if not raw_table or not raw_table[0]:
                return pd.DataFrame()

            # Extract and clean headers
            headers = [
                str(h).strip() if h and str(h).strip() 
                else f"Column_{i}" for i, h in enumerate(raw_table[0])
            ]
            
            # Handle case where there's only a header row
            if len(raw_table) < 2:
                return pd.DataFrame(columns=headers)
            
            data = raw_table[1:]
            
            # Create DataFrame with proper error handling
            df = pd.DataFrame(data, columns=headers)
            
            # Clean column names
            df.columns = df.columns.map(lambda x: re.sub(r'[^\w\s-]', '', str(x)).strip().replace(' ', '_'))
            
            # Remove empty rows/columns
            df = df.dropna(how='all').dropna(axis=1, how='all')
            
            # Convert data types safely
            for col in df.columns:
                df[col] = self._convert_column_type(df[col])
            
            return df
            
        except Exception as e:
            logging.error(f"Table cleaning error: {e}")
            return pd.DataFrame()

    def _convert_column_type(self, series):
        """Convert column to appropriate data type with improved type inference."""
        try:
            # Remove leading/trailing whitespace
            series = series.str.strip() if hasattr(series, 'str') else series
            
            # Try numeric conversion first
            numeric_series = pd.to_numeric(series, errors='coerce')
            if numeric_series.notna().sum() / len(numeric_series) > 0.5:  # If more than 50% are numbers
                return numeric_series
            
            # Try datetime conversion
            datetime_series = pd.to_datetime(series, errors='coerce', format='mixed')
            if datetime_series.notna().sum() / len(datetime_series) > 0.5:  # If more than 50% are dates
                return datetime_series
            
            # Keep as string if other conversions fail
            return series.astype(str).replace('nan', '')
            
        except Exception as e:
            logging.debug(f"Column type conversion failed: {e}")
            return series

    def _generate_table_description(self, df: pd.DataFrame) -> str:
        """Generate a brief description of the table."""
        return f"Table with {df.shape[0]} rows and {df.shape[1]} columns"

        
def main():
    pdf_path = "../sample/sample.pdf"
    output_dir = "extracted_tables"
    os.makedirs(output_dir, exist_ok=True)
    
    class ProgressTracker:
        def update(self, progress):
            print(f"Progress: {progress:.1f}%")
    
    try:
        # Create config with default values
        config = ExtractorConfig()
        extractor = TableExtractor(config)
        tables = extractor.extract(pdf_path, ProgressTracker())
        
        print(f"\nExtracted {len(tables)} tables")
        for i, table in enumerate(tables, 1):
            print(f"\nTable {i} from page {table['page_number']}:") 
            print(f"Rows: {table['rows']}")
            print(f"Columns: {table['columns']}")
            print(f"Description: {table['description']}")
            
    except Exception as e:
        logging.error(f"Table extraction failed: {e}")

if __name__ == "__main__":
    main()
