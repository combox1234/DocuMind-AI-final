
import os
import sys
import threading
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def install_dependencies():
    """Ensure pyngrok is installed"""
    try:
        import pyngrok
    except ImportError:
        logger.info("Installing pyngrok...")
        os.system(f"{sys.executable} -m pip install pyngrok")

def start_server():
    """Start the Waitress Output (Blocking)"""
    logger.info("Starting Waitress Server on Port 5000...")
    # Import here to avoid issues if requirements aren't met yet
    from waitress import serve
    from app import app
    serve(app, host="0.0.0.0", port=5000, threads=6)

def start_tunnel():
    """Open ngrok tunnel"""
    from pyngrok import ngrok, conf
    
    logger.info("Opening ngrok Tunnel...")
    
    # 1. Ask for Authtoken (Required by ngrok now)
    print("\n" + "!"*60)
    print("NGROK AUTH REQUIRED")
    print("If you haven't set it yet, get it from: https://dashboard.ngrok.com/get-started/your-authtoken")
    print("!"*60 + "\n")
    
    token = input("Enter ngrok Authtoken (Leave empty if already configured): ").strip()
    if token:
        conf.get_default().auth_token = token

    try:
        # Create tunnel
        public_url = ngrok.connect(5000).public_url
        
        print("\n" + "="*60)
        print(f"🚀 YOUR APP IS LIVE AT: {public_url}")
        print("="*60 + "\n")
        
        logger.info(f"Tunnel established at: {public_url}")
        
        # Keep alive
        while True:
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"ngrok Error: {e}")
        os._exit(1)

if __name__ == "__main__":
    install_dependencies()
    
    # 1. Start Tunnel FIRST (So user sees the URL immediately)
    from pyngrok import ngrok, conf
    
    # Ask for Auth if needed (Simple check)
    print("\n" + "!"*60)
    print("CHECKING NGROK CONFIG...")
    print("If you get an auth error, run: ngrok config add-authtoken <TOKEN>")
    print("!"*60 + "\n")

    try:
        # Create tunnel (Force IPv4 "127.0.0.1" to avoid [::1] IPv6 errors on Windows)
        public_url = ngrok.connect("127.0.0.1:5000").public_url
        print("\n" + "🚀"*30)
        print(f" PUBLIC URL: {public_url}")
        print("🚀"*30 + "\n")
        
        # Flush to ensure it prints
        sys.stdout.flush()
        
    except Exception as e:
        logger.error(f"ngrok Error: {e}")
        print("Tip: Did you add your authtoken?")
        sys.exit(1)

    # 2. Start Server (Blocking)
    print("Starting Server... (Press Ctrl+C to stop)")
    start_server()
