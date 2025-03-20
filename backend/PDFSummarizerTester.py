import asyncio
import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from main import PDFSummarizer, ProcessingConfig, ExtractorConfig, ImageConfig

class PDFSummarizerTester:
    def __init__(self, test_pdf_path: str):
        self.test_pdf_path = Path(test_pdf_path)
        self.results: Dict[str, Any] = {}
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def progress_callback(self, progress):
        self.logger.info(f"Progress - Stage: {progress.stage}, Message: {progress.message}, "
                        f"Progress: {progress.progress}%, Status: {progress.status}")
        if progress.error:
            self.logger.error(f"Error in {progress.stage}: {progress.error}")

    async def run_tests(self) -> Dict[str, bool]:
        test_results = {}
        
        try:
            # Initialize with default config
            config = ProcessingConfig(
                extract_images=True,
                extract_tables=True,
                extract_metadata=True,
                max_workers=4,
                gpu_enabled=True
            )
            
            summarizer = PDFSummarizer(config)
            
            # Test file existence
            test_results['file_exists'] = self.test_pdf_path.exists()
            if not test_results['file_exists']:
                self.logger.error(f"Test PDF not found at {self.test_pdf_path}")
                return test_results
            
            # Process PDF
            try:
                self.results = await summarizer.process_pdf(
                    str(self.test_pdf_path),
                    progress_callback=self.progress_callback
                )
                test_results['processing_completed'] = True
            except Exception as e:
                self.logger.error(f"PDF processing failed: {str(e)}")
                test_results['processing_completed'] = False
                return test_results
            
            # Test individual components
            test_results.update({
                'text_extraction': self._test_text_extraction(),
                'image_extraction': self._test_image_extraction(),
                'table_extraction': self._test_table_extraction(),
                'metadata_extraction': self._test_metadata_extraction(),
                'summary_generation': self._test_summary_generation(),
                'document_structure': self._test_document_structure()
            })
            
            # Cleanup
            summarizer.cleanup()
            
        except Exception as e:
            self.logger.error(f"Test execution failed: {str(e)}")
            test_results['test_execution'] = False
            
        return test_results
    
    def _test_text_extraction(self) -> bool:
        if 'text' not in self.results:
            self.logger.error("No text content in results")
            return False
        
        text_content = self.results['text']
        if not isinstance(text_content, str) or not text_content.strip():
            self.logger.error("Text content is empty or invalid")
            return False
            
        self.logger.info(f"Text extraction successful: {len(text_content)} characters")
        return True
    
    def _test_image_extraction(self) -> bool:
        if 'images' not in self.results:
            self.logger.error("No image content in results")
            return False
            
        images = self.results['images']
        if not isinstance(images, (list, dict)):
            self.logger.error("Images result is not in expected format")
            return False
            
        self.logger.info(f"Image extraction successful: {len(images)} images found")
        return True
    
    def _test_table_extraction(self) -> bool:
        if 'tables' not in self.results:
            self.logger.error("No table content in results")
            return False
            
        tables = self.results['tables']
        if not isinstance(tables, (list, dict)):
            self.logger.error("Tables result is not in expected format")
            return False
            
        self.logger.info(f"Table extraction successful: {len(tables)} tables found")
        return True
    
    def _test_metadata_extraction(self) -> bool:
        if 'metadata' not in self.results:
            self.logger.error("No metadata in results")
            return False
            
        metadata = self.results['metadata']
        if not isinstance(metadata, dict):
            self.logger.error("Metadata is not in expected format")
            return False
            
        self.logger.info(f"Metadata extraction successful: {len(metadata)} fields found")
        return True
    
    def _test_summary_generation(self) -> bool:
        if 'summary' not in self.results:
            self.logger.error("No summary in results")
            return False
            
        summary = self.results['summary']
        if not isinstance(summary, str) or not summary.strip():
            self.logger.error("Summary is empty or invalid")
            return False
            
        self.logger.info(f"Summary generation successful: {len(summary)} characters")
        return True
    
    def _test_document_structure(self) -> bool:
        if 'document_structure' not in self.results:
            self.logger.error("No document structure in results")
            return False
            
        structure = self.results['document_structure']
        required_fields = ['introduction', 'main_content', 'conclusions', 'key_concepts', 'topics']
        
        if not all(field in structure for field in required_fields):
            self.logger.error("Document structure missing required fields")
            return False
            
        self.logger.info("Document structure analysis successful")
        return True

async def main():
    # Specify the path to your test PDF
    test_pdf_path = "sample/sample.pdf"
    
    # Create and run tester
    tester = PDFSummarizerTester(test_pdf_path)
    test_results = await tester.run_tests()
    
    # Print results
    print("\nTest Results:")
    print("-" * 50)
    for test_name, result in test_results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:.<40} {status}")
    print("-" * 50)
    
    # Calculate overall success
    success_rate = sum(1 for result in test_results.values() if result) / len(test_results) * 100
    print(f"\nOverall Success Rate: {success_rate:.1f}%")

if __name__ == "__main__":
    asyncio.run(main())