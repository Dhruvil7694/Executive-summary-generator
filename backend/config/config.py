import os

class Config:
    # Model settings
    # TROCR_MODEL_NAME = "microsoft/trocr-base-handwritten"
    T5_MODEL_NAME = "t5-base"
    T5_LOCAL_PATH = "./models/t5_model"
    BERT_MODEL_NAME = "multi-qa-mpnet-base-dot-v1"
    SPACY_MODEL = "en_core_web_trf"
    
    # Processing settings
    CHUNK_SIZE = 1000
    MAX_SUMMARY_LENGTH = 300
    MIN_SUMMARY_LENGTH = 50
    OCR_RESOLUTION = 300
    
    # File paths
    FEEDBACK_FILE = "feedback_data.json"
    UPLOAD_FOLDER = 'uploads/'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Logging configuration
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_LEVEL = "INFO"
    LOG_FILE = "pdf_summarizer.log"
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    # Debug settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    @classmethod
    def get_log_config(cls):
        """Get logging configuration dictionary."""
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': cls.LOG_FORMAT,
                    'datefmt': cls.LOG_DATE_FORMAT,
                },
            },
            'handlers': {
                'console': {
                    'level': cls.LOG_LEVEL,
                    'formatter': 'standard',
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://sys.stdout',
                },
                'file': {
                    'level': 'DEBUG',
                    'formatter': 'standard',
                    'class': 'logging.FileHandler',
                    'filename': cls.LOG_FILE,
                    'mode': 'a',
                },
            },
            'loggers': {
                '': {  # root logger
                    'handlers': ['console', 'file'],
                    'level': cls.LOG_LEVEL,
                    'propagate': True
                },
            }
        }