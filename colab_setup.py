"""
Google Colab Setup Script for HealthAssist AI with IBM Granite Model
Run this script first in Google Colab to install dependencies and setup the environment
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages for the application"""
    requirements = [
        "streamlit>=1.45.1",
        "transformers>=4.40.0",
        "torch>=2.0.0",
        "accelerate>=0.20.0",
        "bitsandbytes>=0.41.0",
        "pyngrok>=7.0.0",
        "plotly>=5.0.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "Pillow>=9.0.0",
        "huggingface_hub>=0.16.0"
    ]
    
    print("Installing required packages...")
    for package in requirements:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    print("All packages installed successfully!")

def setup_ngrok():
    """Setup ngrok for public URL access"""
    try:
        from pyngrok import ngrok
        print("Setting up ngrok tunnel...")
        
        # Get ngrok auth token from environment or prompt user
        auth_token = os.getenv("NGROK_AUTH_TOKEN")
        if not auth_token:
            print("\nTo use ngrok, you need to:")
            print("1. Sign up at https://ngrok.com/")
            print("2. Get your auth token from the dashboard")
            print("3. Set it as environment variable: os.environ['NGROK_AUTH_TOKEN'] = 'your_token'")
            print("4. Or paste it when prompted")
            
            auth_token = input("\nEnter your ngrok auth token (or press Enter to skip): ").strip()
        
        if auth_token:
            ngrok.set_auth_token(auth_token)
            print("Ngrok configured successfully!")
        else:
            print("Skipping ngrok setup. You can configure it later.")
            
    except ImportError:
        print("Pyngrok not available. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyngrok"])

def check_gpu():
    """Check if GPU is available"""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"GPU Available: {gpu_name}")
            print(f"GPU Memory: {gpu_memory:.1f} GB")
            return True
        else:
            print("No GPU available. The application will run on CPU (slower).")
            return False
    except ImportError:
        print("PyTorch not installed. Please install it first.")
        return False

def main():
    """Main setup function"""
    print("=== HealthAssist AI with IBM Granite - Google Colab Setup ===")
    print()
    
    # Install requirements
    install_requirements()
    print()
    
    # Check GPU
    gpu_available = check_gpu()
    print()
    
    # Setup ngrok
    setup_ngrok()
    print()
    
    print("=== Setup Complete! ===")
    print()
    print("Next steps:")
    print("1. Run the following command to start the application:")
    print("   !python -m streamlit run app.py --server.port 5000")
    print()
    print("2. Or use the integrated launcher:")
    print("   import subprocess")
    print("   subprocess.Popen(['python', '-m', 'streamlit', 'run', 'app.py', '--server.port', '5000'])")
    print()
    
    if gpu_available:
        print("3. The IBM Granite model will use GPU acceleration for faster inference.")
    else:
        print("3. The IBM Granite model will run on CPU (slower but functional).")

if __name__ == "__main__":
    main()
