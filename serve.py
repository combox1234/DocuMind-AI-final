from waitress import serve
from app import app
import logging

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("waitress")
    logger.setLevel(logging.INFO)
    
    print("\n" + "="*60)
    print("🚀 DocuMind AI - Production Server (Waitress)")
    print("   Running on http://0.0.0.0:5000")
    print("   Threads: 6 | URL Scheme: http")
    print("="*60 + "\n")
    
    serve(app, host='0.0.0.0', port=5000, threads=6)
