from tracemalloc import BaseFilter
import pdfplumber
import io
from PIL import ImageEnhance, Image
import base64
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Optional
import numpy as np
from dataclasses import dataclass
from hashlib import md5
from dataclasses import dataclass, field

@dataclass
class ImageConfig:
    MIN_WIDTH: int = 100
    MIN_HEIGHT: int = 100
    MAX_SIZE: int = 8000
    SUPPORTED_FORMATS: set = field(default_factory=lambda: {'PNG', 'JPEG', 'JPG', 'TIFF', None})
    DEFAULT_DPI: int = 600
    ENHANCEMENT_FACTORS: dict = field(
        default_factory=lambda: {
            'contrast': 1.5,
            'brightness': 1.2,
            'sharpness': 1.8
        }
    )

class ImageExtractor:
    def __init__(self, config: ImageConfig = None):
        self.config = config or ImageConfig()
        self.processed_hashes = set()
        self._setup_logging()

    def _optimize_image_storage(self, image: Image.Image) -> bytes:
        """Optimize image storage while maintaining quality"""
        buffer = io.BytesIO()
        
        try:
            # Choose format based on image characteristics
            if image.mode == 'RGBA':
                image.save(buffer, format='PNG', optimize=True)
            else:
                image.save(buffer, format='JPEG', 
                        quality=85, 
                        optimize=True,
                        progressive=True)
            
            return buffer.getvalue()
        except Exception as e:
            logging.error(f"Image optimization failed: {e}")
            return None


    def _enhance_image_quality(self, image: Image.Image) -> Image.Image:
        """Enhanced image processing pipeline"""
        try:
            # Convert to RGB if needed
            if image.mode not in ('RGB', 'L'):
                image = image.convert('RGB')
            
            # Apply advanced enhancements
            enhancements = [
                (ImageEnhance.Contrast, 1.5),
                (ImageEnhance.Brightness, 1.2),
                (ImageEnhance.Sharpness, 1.8),
                (ImageEnhance.Color, 1.1)
            ]
            
            for enhancer_class, factor in enhancements:
                enhancer = enhancer_class(image)
                image = enhancer.enhance(factor)
            
            # Apply noise reduction
            image = image.filter(BaseFilter.MedianFilter(size=3))
            
            return image
        except Exception as e:
            logging.error(f"Image enhancement failed: {e}")
            return image
        
    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def extract(self, pdf_path: str,  *args, **kwargs) -> List[Dict]:
        """Extract and process images from PDF."""
        images_data = []
        total_processed = 0
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                
                with ThreadPoolExecutor() as executor:
                    futures = []
                    for page_num, page in enumerate(pdf.pages, 1):
                        future = executor.submit(self._process_page, page, page_num)
                        futures.append(future)
                    
                    for future in futures:
                        page_images = future.result()
                        if page_images:
                            images_data.extend(page_images)
                        total_processed += 1
                        
                
        except Exception as e:
            logging.error(f"PDF processing error: {str(e)}")
        
        return self._deduplicate_images(images_data)

    def _process_page(self, page, page_num: int) -> List[Dict]:
        """Process single page for image extraction."""
        page_images = []
        
        try:
            # Extract page image
            page_image = page.to_image(resolution=self.config.DEFAULT_DPI)
            pil_image = page_image.original
            
            # Convert to RGB if needed
            if pil_image.mode not in ('RGB', 'L'):
                pil_image = pil_image.convert('RGB')
            
            logging.info(f"Processing page {page_num} - Size: {pil_image.size}, Mode: {pil_image.mode}")
            
            if self._is_valid_image(pil_image):
                enhanced_image = self._enhance_image(pil_image)
                image_data = self._prepare_image_data(enhanced_image, page_num)
                
                if image_data:
                    page_images.append(image_data)
                    logging.info(f"Successfully processed image from page {page_num}")
            else:
                logging.warning(f"Invalid image on page {page_num}")
                    
        except Exception as e:
            logging.error(f"Error processing page {page_num}: {str(e)}")
            
        return page_images



    def _is_valid_image(self, image: Optional[Image.Image]) -> bool:
        """Validate image dimensions and format."""
        if not image:
            return False
        
        try:
            width, height = image.size
            logging.info(f"Validating image: {width}x{height}, Mode: {image.mode}")
            
            return (
                width >= self.config.MIN_WIDTH and
                height >= self.config.MIN_HEIGHT and
                width <= self.config.MAX_SIZE and
                height <= self.config.MAX_SIZE
            )
        except Exception as e:
            logging.error(f"Image validation error: {str(e)}")
            return False


    def _enhance_image(self, image: Image.Image) -> Image.Image:
        """Apply image enhancements."""
        try:
            if image.mode not in ('RGB', 'L'):
                image = image.convert('RGB')

            # Apply enhancements
            enhancers = [
                (ImageEnhance.Contrast, self.config.ENHANCEMENT_FACTORS['contrast']),
                (ImageEnhance.Brightness, self.config.ENHANCEMENT_FACTORS['brightness']),
                (ImageEnhance.Sharpness, self.config.ENHANCEMENT_FACTORS['sharpness'])
            ]
            
            for enhancer_class, factor in enhancers:
                image = enhancer_class(image).enhance(factor)
            
            return image
            
        except Exception as e:
            logging.error(f"Image enhancement failed: {str(e)}")
            return image

    def _prepare_image_data(self, image: Image.Image, page_num: int) -> Optional[Dict]:
        try:
            img_hash = self._calculate_image_hash(image)
            
            if img_hash in self.processed_hashes:
                return None
            
            self.processed_hashes.add(img_hash)
            
            buffer = io.BytesIO()
            image.save(buffer, format='PNG', optimize=False, quality=100)  # Disabled optimization, max quality
            
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return {
                'page_number': page_num,
                'base64_image': img_base64,
                'width': image.size[0],
                'height': image.size[1],
                'content_type': self._identify_content_type(image),
                'format': 'PNG',
                'hash': img_hash,
                'dpi': self.config.DEFAULT_DPI
            }
            
        except Exception as e:
            logging.error(f"Error preparing image data: {str(e)}")
            return None
            
    def _calculate_image_hash(self, image: Image.Image) -> str:
        """Calculate unique hash for image."""
        try:
            img_array = np.array(image)
            return md5(img_array.tobytes()).hexdigest()
        except Exception:
            return ''

    def _identify_content_type(self, image: Image.Image) -> str:
        """Identify content type based on image properties."""
        try:
            width, height = image.size
            aspect_ratio = width / height
            
            if 0.7 <= aspect_ratio <= 0.75:
                return "document"
            elif 1.3 <= aspect_ratio <= 1.5:
                return "figure"
            elif aspect_ratio > 1.5:
                return "table"
            else:
                return "image"
                
        except Exception:
            return "unknown"

    def _deduplicate_images(self, images: List[Dict]) -> List[Dict]:
        """Remove duplicate images based on content."""
        seen_hashes = set()
        unique_images = []
        
        for image in images:
            if image['hash'] not in seen_hashes:
                seen_hashes.add(image['hash'])
                unique_images.append(image)
        
        return unique_images

def main():
    logging.basicConfig(level=logging.INFO)
    pdf_path = "../sample/sample.pdf"
    output_dir = "extracted_images"
    os.makedirs(output_dir, exist_ok=True)
    
    class ProgressTracker:
        def update(self, progress):
            print(f"Progress: {progress:.1f}%")
    
    try:
        extractor = ImageExtractor()
        images = extractor.extract(pdf_path, ProgressTracker())
        
        print(f"\nExtracted {len(images)} unique images")
        
    except Exception as e:
        logging.error(f"Image extraction failed: {str(e)}")

if __name__ == "__main__":
    main()