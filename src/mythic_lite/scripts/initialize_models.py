#!/usr/bin/env python3
"""
Model initialization script for Mythic-Lite.
Downloads and sets up all required AI models automatically.
"""

import sys
from pathlib import Path
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn

# Add package to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mythic_lite.core.model_manager import get_model_manager
from mythic_lite.utils.logger import get_logger
from mythic_lite.core.config import get_config


def main():
    """Initialize all required models."""
    logger = get_logger("model-initializer")
    config = get_config()
    model_manager = get_model_manager()
    
    logger.info("🚀 Starting Mythic-Lite model initialization...")
    logger.info(f"Runtime path: {config.runtime_path}")
    logger.info(f"Models path: {config.models_path}")
    
    try:
        # First verify existing models for corruption with progress bar
        logger.info("🔍 Verifying existing models for corruption...")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=logger.console if hasattr(logger, 'console') else None
        ) as progress:
            verify_task = progress.add_task("Verifying models...", total=3)
            verification_results = model_manager.verify_all_models()
            progress.update(verify_task, advance=1, description="Verification complete")
            
            # Clean up any corrupted models
            progress.update(verify_task, advance=1, description="Cleaning up corrupted models...")
            cleaned_count = model_manager.cleanup_corrupted_models()
            total_cleaned = sum(cleaned_count.values())
            if total_cleaned > 0:
                logger.warning(f"Removed {total_cleaned} corrupted model files")
                for model_type, count in cleaned_count.items():
                    if count > 0:
                        logger.warning(f"  {model_type}: {count} files removed")
            
            progress.update(verify_task, advance=1, description="Cleanup complete")
        
        # Initialize/download all required models with progress bar
        logger.info("🚀 Starting model initialization...")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TextColumn("•"),
            TimeRemainingColumn(),
            console=logger.console if hasattr(logger, 'console') else None
        ) as progress:
            task = progress.add_task("Initializing models...", total=3)  # 3 model types
            
            # Initialize/download all required models
            results = model_manager.initialize_all_models()
            
            # Update progress as each model type completes
            for i, (model_type, success) in enumerate(results.items()):
                progress.update(task, advance=1, description=f"Completed {model_type} model")
                if success:
                    logger.info(f"✅ {model_type.upper()} model ready")
                else:
                    logger.warning(f"❌ {model_type.upper()} model failed")
        
        # Report results
        logger.info("📊 Model initialization results:")
        for model_type, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            logger.info(f"  {model_type.upper()}: {status}")
        
        # Final verification of all models
        logger.info("🔍 Final model verification...")
        final_verification = model_manager.verify_all_models()
        
        # Show model info
        model_info = model_manager.get_model_info()
        logger.info("📁 Model directory structure:")
        for model_type, info in model_info["models"].items():
            if info["files"]:
                logger.info(f"  {model_type}: {len(info['files'])} files, {info['total_size'] / (1024*1024):.1f} MB")
            else:
                logger.info(f"  {model_type}: No files")
        
        # Show verification status
        logger.info("🔍 Model verification status:")
        for model_type, status_info in final_verification.items():
            if status_info["status"] == "present":
                valid_files = sum(1 for f in status_info["files"] if f["valid"])
                total_files = len(status_info["files"])
                logger.info(f"  {model_type}: {valid_files}/{total_files} files valid")
            else:
                logger.info(f"  {model_type}: {status_info['status']}")
        
        # Check if all models succeeded
        all_success = all(results.values())
        if all_success:
            logger.success("🎉 All models initialized successfully!")
            logger.info("You can now run the chatbot with: python -m src.cli")
        else:
            logger.warning("⚠️  Some models failed to initialize. Check the logs above.")
            logger.info("The system will fall back to available models where possible.")
        
        return all_success
        
    except Exception as e:
        logger.error(f"❌ Model initialization failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
