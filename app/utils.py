"""
Utils Module - Helper functions and utilities
"""

import os
import time
import functools
import logging
from typing import Dict, Any, Optional, Callable
from pathlib import Path
import hashlib
import json

logger = logging.getLogger(__name__)


class Timer:
    """Timer class"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
    
    @property
    def elapsed(self) -> float:
        """Get elapsed time"""
        if self.start_time is None:
            return 0
        end = self.end_time if self.end_time else time.time()
        return end - self.start_time
    
    def format_time(self) -> str:
        """Format time display"""
        elapsed = self.elapsed
        if elapsed < 1:
            return f"{elapsed*1000:.0f}ms"
        elif elapsed < 60:
            return f"{elapsed:.1f}s"
        else:
            minutes = int(elapsed // 60)
            seconds = elapsed % 60
            return f"{minutes}m {seconds:.1f}s"


class RateLimiter:
    """Rate limiter"""
    
    def __init__(self, max_calls: int = 10, time_window: int = 60):
        """Initialize rate limiter
        
        Args:
            max_calls: Max calls in time window
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    def is_allowed(self) -> bool:
        """Check if call is allowed"""
        now = time.time()
        
        # Clean expired call records
        self.calls = [call_time for call_time in self.calls 
                     if now - call_time < self.time_window]
        
        # Check if limit exceeded
        if len(self.calls) >= self.max_calls:
            return False
        
        # Record new call
        self.calls.append(now)
        return True
    
    def time_until_reset(self) -> float:
        """Get time until reset"""
        if not self.calls:
            return 0
        
        oldest_call = min(self.calls)
        return max(0, self.time_window - (time.time() - oldest_call))


def rate_limit(max_calls: int = 10, time_window: int = 60):
    """Rate limiting decorator"""
    limiter = RateLimiter(max_calls, time_window)
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not limiter.is_allowed():
                wait_time = limiter.time_until_reset()
                raise Exception(f"Rate limited: wait {wait_time:.1f} seconds")
            return func(*args, **kwargs)
        return wrapper
    return decorator


def calculate_file_hash(file_content: bytes) -> str:
    """Calculate file hash"""
    return hashlib.md5(file_content).hexdigest()


def format_file_size(size_bytes: int) -> str:
    """Format file size"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"


def safe_filename(filename: str) -> str:
    """Create safe filename"""
    # Remove or replace unsafe characters
    safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_"
    safe_name = "".join(c if c in safe_chars else "_" for c in filename)
    
    # Limit length
    if len(safe_name) > 100:
        name, ext = os.path.splitext(safe_name)
        safe_name = name[:90] + ext
    
    return safe_name


def load_config(config_path: str = ".env") -> Dict[str, Any]:
    """Load configuration file"""
    config = {}
    
    try:
        from dotenv import load_dotenv
        load_dotenv(config_path)
        
        config = {
            # OpenAI configuration
            'openai_api_key': os.getenv('OPENAI_API_KEY', ''),
            'model_name': os.getenv('MODEL_NAME', 'gpt-4o'),
            'temperature': float(os.getenv('TEMPERATURE', '0')),
            'max_tokens': int(os.getenv('MAX_TOKENS', '2000')),
            
            # RAG configuration
            'strict_mode': os.getenv('STRICT_MODE', 'True').lower() == 'true',
            'chunk_size': int(os.getenv('CHUNK_SIZE', '1000')),
            'chunk_overlap': int(os.getenv('CHUNK_OVERLAP', '200')),
            'top_k_results': int(os.getenv('TOP_K_RESULTS', '5')),
            
            # Database configuration
            'vector_db_path': os.getenv('VECTOR_DB_PATH', './vector_db'),
            
            # UI configuration
            'page_title': os.getenv('PAGE_TITLE', 'Document Q&A RAG Demo'),
            'page_icon': os.getenv('PAGE_ICON', '📄🔍')
        }
        
        logger.info("Configuration loaded successfully")
        
    except Exception as e:
        logger.warning(f"Failed to load config, using defaults: {e}")
        
        # Default configuration
        config = {
            'openai_api_key': '',
            'model_name': 'gpt-4o',
            'temperature': 0,
            'max_tokens': 2000,
            'strict_mode': True,
            'chunk_size': 1000,
            'chunk_overlap': 200,
            'top_k_results': 5,
            'vector_db_path': './vector_db',
            'page_title': 'Document Q&A RAG Demo',
            'page_icon': '📄🔍'
        }
    
    return config


def validate_config(config: Dict[str, Any]) -> Dict[str, str]:
    """Validate configuration"""
    errors = []
    
    # Check required configuration
    if not config.get('openai_api_key'):
        errors.append("OpenAI API key not set")
    
    # Check value ranges
    if config.get('temperature', 0) < 0 or config.get('temperature', 0) > 2:
        errors.append("Temperature should be between 0-2")
    
    if config.get('chunk_size', 1000) < 100:
        errors.append("Chunk size should be greater than 100")
    
    if config.get('top_k_results', 5) < 1:
        errors.append("Top K results should be greater than 0")
    
    return errors


def create_session_state_key(prefix: str, suffix: str = "") -> str:
    """Create session state key"""
    timestamp = str(int(time.time()))
    if suffix:
        return f"{prefix}_{suffix}_{timestamp}"
    return f"{prefix}_{timestamp}"


def log_user_interaction(action: str, details: Dict[str, Any]):
    """Log user interaction"""
    log_data = {
        'timestamp': time.time(),
        'action': action,
        'details': details
    }
    
    logger.info(f"User interaction: {action}")
    logger.debug(f"Interaction details: {json.dumps(log_data, indent=2)}")


class ProgressTracker:
    """Progress tracker"""
    
    def __init__(self, total_steps: int, description: str = "Processing"):
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.start_time = time.time()
    
    def update(self, step: int = 1, description: Optional[str] = None):
        """Update progress"""
        self.current_step += step
        if description:
            self.description = description
        
        progress = self.current_step / self.total_steps
        elapsed = time.time() - self.start_time
        
        if progress > 0:
            eta = elapsed / progress - elapsed
            logger.info(f"{self.description}: {progress:.1%} - ETA: {eta:.1f}s")
    
    def complete(self):
        """Complete progress"""
        elapsed = time.time() - self.start_time
        logger.info(f"{self.description}: Completed in {elapsed:.1f}s")


def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """Setup logging system"""
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    logger.info("Logging system setup completed")


def get_system_info() -> Dict[str, Any]:
    """Get system information"""
    import platform
    import psutil
    
    return {
        'platform': platform.platform(),
        'python_version': platform.python_version(),
        'cpu_count': psutil.cpu_count(),
        'memory_total': psutil.virtual_memory().total,
        'memory_available': psutil.virtual_memory().available,
        'disk_usage': psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent
    } 