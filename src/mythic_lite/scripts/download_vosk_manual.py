#!/usr/bin/env python3
"""
Manual Vosk model download helper script.
Since Vosk models aren't available on HuggingFace, this script provides
clear instructions for manual download.
"""

import os
import sys
import zipfile
import requests
from pathlib import Path

def download_vosk_manual():
    """Provide instructions and attempt to download Vosk model manually."""
    
    print("🎤 Vosk ASR Model Download Helper")
    print("=" * 50)
    print()
    print("Vosk models are not available on HuggingFace, so we need to download")
    print("them manually from the official Vosk website.")
    print()
    
    # Model details
    model_name = "vosk-model-small-en-us-0.15"
    model_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    target_dir = Path("runtime/models/asr")
    
    print(f"📁 Target directory: {target_dir}")
    print(f"🔗 Download URL: {model_url}")
    print()
    
    # Create target directory
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if model already exists
    model_path = target_dir / model_name
    if model_path.exists():
        print(f"✅ Model already exists at: {model_path}")
        print("You can now use speech recognition!")
        return True
    
    print("📥 Attempting to download Vosk model automatically...")
    print("(This may fail due to website restrictions)")
    print()
    
    try:
        # Try to download
        zip_path = target_dir / f"{model_name}.zip"
        print(f"⬇️  Downloading from: {model_url}")
        
        response = requests.get(model_url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r📥 Downloading... {percent:.1f}%", end='', flush=True)
        
        print(f"\n✅ Download completed: {zip_path}")
        
        # Extract model
        print("📦 Extracting model...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir)
        
        # Clean up zip file
        zip_path.unlink()
        
        print(f"✅ Model extracted to: {model_path}")
        print("🎉 Vosk model setup complete! You can now use speech recognition.")
        return True
        
    except Exception as e:
        print(f"❌ Automatic download failed: {e}")
        print()
        print("🔧 Manual Download Instructions:")
        print("1. Open your web browser and go to: https://alphacephei.com/vosk/models")
        print("2. Find and download: 'vosk-model-small-en-us-0.15.zip'")
        print("3. Extract the ZIP file")
        print("4. Copy the extracted 'vosk-model-small-en-us-0.15' folder to:")
        print(f"   {target_dir}")
        print("5. Ensure the final path is:")
        print(f"   {target_dir / model_name}")
        print()
        print("📋 Alternative: Use the direct download link:")
        print(f"   {model_url}")
        print()
        print("After manual download, run this script again to verify the setup.")
        return False

def verify_model():
    """Verify if the Vosk model is properly installed."""
    model_path = Path("runtime/models/asr/vosk-model-small-en-us-0.15")
    
    if model_path.exists():
        print("✅ Vosk model found!")
        print(f"📁 Location: {model_path}")
        
        # Check for key files
        key_files = ["am", "conf", "graph", "ivector", "rescoring", "rnnlm"]
        missing_files = []
        
        for key_file in key_files:
            if not (model_path / key_file).exists():
                missing_files.append(key_file)
        
        if missing_files:
            print(f"⚠️  Missing key files: {', '.join(missing_files)}")
            print("The model may be incomplete. Please re-download.")
            return False
        else:
            print("✅ All key files present - model appears complete!")
            return True
    else:
        print("❌ Vosk model not found!")
        return False

if __name__ == "__main__":
    print("🎤 Vosk ASR Model Setup")
    print("=" * 30)
    print()
    
    # First verify if model exists
    if verify_model():
        print("\n🎉 Vosk model is ready! You can now use speech recognition.")
        sys.exit(0)
    
    print("\n📥 Model not found. Starting download process...")
    print()
    
    success = download_vosk_manual()
    
    if success:
        print("\n🎉 Setup complete! Running verification...")
        verify_model()
    else:
        print("\n📋 Please follow the manual download instructions above.")
        print("After downloading, run this script again to verify the setup.")
        sys.exit(1)
