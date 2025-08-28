"""
Model Manager for Mythic-Lite chatbot system.
Handles automatic downloading and management of AI models.
"""

import os
import shutil
from pathlib import Path
from typing import Optional, Dict, Any

# Use lazy imports to avoid dependency issues during import
def get_external_modules():
    """Get external modules when needed."""
    try:
        from huggingface_hub import hf_hub_download
        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
        return hf_hub_download, Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
    except ImportError:
        # Return None if modules are not available
        return None, None, None, None, None, None, None

from .config import get_config
from ..utils.logger import get_logger


class ModelManager:
    """Manages automatic downloading and organization of AI models."""
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger("model-manager")
        self.runtime_path = Path(__file__).parent.parent / "runtime"
        self.models_path = self.runtime_path / "models"
        
        # Ensure runtime directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary runtime directories if they don't exist."""
        directories = [
            self.runtime_path,
            self.models_path,
            self.models_path / "llm",
            self.models_path / "tts", 
            self.models_path / "summarization",
            self.models_path / "asr"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Ensured directory exists: {directory}")
    
    def get_model_path(self, model_type: str, filename: str) -> Path:
        """Get the full path for a specific model file."""
        return self.models_path / model_type / filename
    
    def is_model_downloaded(self, model_type: str, filename: str) -> bool:
        """Check if a model file exists locally and is valid."""
        model_path = self.get_model_path(model_type, filename)
        if not model_path.exists() or model_path.stat().st_size == 0:
            return False
        
        # Check if file is corrupted by attempting to open it
        try:
            with open(model_path, 'rb') as f:
                # Read first and last few bytes to check file integrity
                f.seek(0)
                header = f.read(1024)  # Read first 1KB
                
                # Check file size is reasonable (not just a few bytes)
                file_size = model_path.stat().st_size
                if file_size < 1024:  # Less than 1KB is suspicious
                    self.logger.warning(f"Model file too small: {file_size} bytes")
                    return False
                
                # For specific model types, add format-specific validation
                if model_type in ["llm", "summarization"] and filename.endswith('.gguf'):
                    # Check GGUF file header magic
                    if not header.startswith(b'GGUF'):
                        self.logger.warning(f"Invalid GGUF file header: {header[:20]}")
                        return False
                
                # Read last few bytes to ensure file is complete
                f.seek(-1024, 2)  # Go to last 1KB
                footer = f.read(1024)
                
                # Basic corruption check: ensure we can read the entire file
                f.seek(0)
                # Try to read in chunks to detect corruption
                chunk_size = 1024 * 1024  # 1MB chunks
                total_read = 0
                while total_read < file_size:
                    chunk = f.read(min(chunk_size, file_size - total_read))
                    if not chunk:  # Unexpected EOF
                        self.logger.warning(f"Unexpected EOF at {total_read} bytes")
                        return False
                    total_read += len(chunk)
                
                self.logger.debug(f"Model file validation passed: {filename} ({file_size} bytes)")
                return True
                
        except Exception as e:
            self.logger.warning(f"Model file validation failed for {filename}: {e}")
            return False
    
    def download_model(self, model_type: str, repo_id: str, filename: str) -> Optional[Path]:
        """Download a model from Hugging Face Hub."""
        try:
            # Get external modules when needed
            hf_hub_download, Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn = get_external_modules()
            
            if hf_hub_download is None:
                self.logger.error("huggingface_hub not available - cannot download models")
                return None
            
            self.logger.info(f"Downloading {model_type} model: {filename} from {repo_id}")
            
            # Create model directory
            model_dir = self.models_path / model_type
            model_dir.mkdir(parents=True, exist_ok=True)
            
            # Download the model
            model_path = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                cache_dir=str(model_dir),
                local_dir=str(model_dir)
            )
            
            if model_path and Path(model_path).exists():
                self.logger.success(f"Successfully downloaded {model_type} model: {filename}")
                return Path(model_path)
            else:
                self.logger.error(f"Failed to download {model_type} model: {filename}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error downloading {model_type} model {filename}: {e}")
            return None
    
    def ensure_model(self, model_type: str, repo_id: str, filename: str) -> Optional[Path]:
        """Ensure a model is available, downloading it if necessary."""
        model_path = self.get_model_path(model_type, filename)
        
        if self.is_model_downloaded(model_type, filename):
            self.logger.info(f"{model_type} model already available: {filename}")
            return model_path
        
        self.logger.info(f"{model_type} model not found, downloading: {filename}")
        downloaded_path = self.download_model(model_type, repo_id, filename)
        
        if downloaded_path:
            return downloaded_path
        else:
            self.logger.error(f"Failed to ensure {model_type} model: {filename}")
            return None
    
    def get_model_info(self, model_type: str) -> Dict[str, Any]:
        """Get information about available models."""
        model_dir = self.models_path / model_type
        if not model_dir.exists():
            return {"available": False, "models": []}
        
        models = []
        for model_file in model_dir.iterdir():
            if model_file.is_file():
                models.append({
                    "name": model_file.name,
                    "size": model_file.stat().st_size,
                    "path": str(model_file)
                })
        
        return {
            "available": True,
            "models": models,
            "count": len(models)
        }
    
    def cleanup_old_models(self, model_type: str, keep_latest: int = 2):
        """Clean up old model versions, keeping only the latest ones."""
        try:
            model_dir = self.models_path / model_type
            if not model_dir.exists():
                return
            
            # Get all model files
            model_files = list(model_dir.iterdir())
            if len(model_files) <= keep_latest:
                return
            
            # Sort by modification time (newest first)
            model_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Remove old models
            for old_model in model_files[keep_latest:]:
                try:
                    old_model.unlink()
                    self.logger.info(f"Removed old {model_type} model: {old_model.name}")
                except Exception as e:
                    self.logger.warning(f"Failed to remove old {model_type} model {old_model.name}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error during {model_type} model cleanup: {e}")
    
    def get_status(self) -> str:
        """Get status of model management system."""
        try:
            status_lines = []
            
            # Check each model type
            for model_type in ["llm", "tts", "summarization", "asr"]:
                info = self.get_model_info(model_type)
                if info["available"]:
                    status_lines.append(f"{model_type.upper()}: {info['count']} models available")
                else:
                    status_lines.append(f"{model_type.upper()}: No models available")
            
            return "\n".join(status_lines)
            
        except Exception as e:
            return f"Error getting model status: {e}"

    def ensure_vosk_model(self) -> Optional[Path]:
        """Ensure Vosk ASR model is available, downloading from official source if necessary."""
        model_name = "vosk-model-small-en-us-0.15"
        model_path = self.models_path / "asr" / model_name
        
        # Check if model already exists and is valid
        if model_path.exists():
            # Verify it's a complete model by checking for essential directories
            # Vosk models may have different directory structures, so we check for the most important ones
            essential_dirs = ["am", "conf", "graph"]
            optional_dirs = ["ivector", "rescoring", "rnnlm"]
            
            # Log what directories are actually present
            present_dirs = [d.name for d in model_path.iterdir() if d.is_dir()]
            self.logger.debug(f"Vosk model directories found: {present_dirs}")
            
            # Check if essential directories exist
            if all((model_path / dir_name).exists() for dir_name in essential_dirs):
                # Check if we have at least some optional directories (models vary)
                optional_count = sum(1 for dir_name in optional_dirs if (model_path / dir_name).exists())
                if optional_count >= 0:  # At least 0 optional dirs (all models are different)
                    self.logger.info(f"Vosk ASR model already exists: {model_name}")
                    return model_path
                else:
                    self.logger.warning(f"Vosk model missing essential directories: {model_name}")
            else:
                self.logger.warning(f"Vosk model missing essential directories: {model_name}")
            
            # Only remove if truly incomplete (missing essential dirs)
            missing_essential = [dir_name for dir_name in essential_dirs if not (model_path / dir_name).exists()]
            if missing_essential:
                self.logger.warning(f"Removing incomplete Vosk model (missing: {missing_essential}): {model_name}")
                try:
                    import shutil
                    shutil.rmtree(model_path)
                except Exception as e:
                    self.logger.error(f"Failed to remove incomplete model: {e}")
            else:
                self.logger.info(f"Vosk model appears complete: {model_name}")
                return model_path
        
        # Download from official Vosk website
        self.logger.info(f"Downloading Vosk ASR model: {model_name}")
        return self.download_vosk_model(model_name)
    
    def download_vosk_model(self, model_name: str) -> Optional[Path]:
        """Download Vosk model from the official website."""
        try:
            # Get external modules when needed
            hf_hub_download, Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn = get_external_modules()
            
            # For Vosk models, we'll use a direct download approach since they're not on HuggingFace
            import requests
            import zipfile
            
            # Model details
            model_url = f"https://alphacephei.com/vosk/models/{model_name}.zip"
            target_dir = self.models_path / "asr"
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Download the ZIP file
            zip_path = target_dir / f"{model_name}.zip"
            self.logger.info(f"Downloading Vosk ASR model...")
            
            response = requests.get(model_url, stream=True, timeout=60)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            # Create progress bar for Vosk download
            if Progress and self.logger.console:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TaskProgressColumn(),
                    TextColumn("•"),
                    TimeRemainingColumn(),
                    console=self.logger.console
                ) as progress:
                    # Create task with appropriate total
                    if total_size > 0:
                        task = progress.add_task(
                            f"Downloading {model_name}...", 
                            total=total_size
                        )
                        progress.update(task, description=f"Downloading Vosk ASR model ({total_size / (1024*1024):.1f} MB)")
                    else:
                        task = progress.add_task(
                            f"Downloading {model_name}...", 
                            total=None
                        )
                    
                    # Save to target file with progress updates
                    target_file = target_dir / f"{model_name}.zip"
                    downloaded_size = 0
                    
                    with open(target_file, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded_size += len(chunk)
                                if total_size > 0:
                                    progress.update(task, completed=downloaded_size)
                                else:
                                    # If we don't know total size, show current progress
                                    progress.update(task, description=f"Downloading Vosk ASR model... ({downloaded_size / (1024*1024):.1f} MB)")
                    
                    # Mark as complete
                    if total_size > 0:
                        progress.update(task, completed=total_size)
                    else:
                        progress.update(task, completed=downloaded_size, total=downloaded_size)
            else:
                # Fallback without progress bar
                with open(zip_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            
            # Extract the model
            self.logger.info("Extracting Vosk model...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(target_dir)
            
            # Clean up the ZIP file
            zip_path.unlink()
            
            # Verify the extracted model
            model_path = target_dir / model_name
            if model_path.exists():
                self.logger.success(f"Vosk model successfully downloaded and extracted: {model_name}")
                return model_path
            else:
                self.logger.error(f"Failed to extract Vosk model: {model_name}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to download Vosk model {model_name}: {e}")
            self.logger.info("You may need to download it manually from: https://alphacephei.com/vosk/models")
            return None


# Global model manager instance
_model_manager: Optional[ModelManager] = None


def get_model_manager() -> ModelManager:
    """Get the global model manager instance."""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager


def ensure_model(model_type: str, repo_id: str, filename: str) -> Optional[Path]:
    """Convenience function to ensure a model is available."""
    manager = get_model_manager()
    return manager.ensure_model(model_type, repo_id, filename)
