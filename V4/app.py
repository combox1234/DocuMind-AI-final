"""
Universal RAG System - Flask Application
"""

from flask import Flask, render_template, request, jsonify, send_file
from pathlib import Path
import logging
import os

from core import DatabaseManager, LLMService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = DATA_DIR / "database"
SORTED_DIR = DATA_DIR / "sorted"

# Initialize services
db_manager = DatabaseManager(DB_DIR)
llm_service = LLMService(model='llama3.2')

logger.info(f"✅ Database initialized with {db_manager.get_count()} documents")


@app.route('/')
def index():
    """Render main chat interface"""
    return render_template('index.html')


@app.route('/test', methods=['GET', 'POST'])
def test():
    """Test endpoint"""
    return jsonify({'status': 'OK', 'message': 'Server is running'})


@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat queries"""
    try:
        data = request.get_json(silent=True)
        
        if not data:
            return jsonify({'error': 'Invalid request'}), 400
        
        query = str(data.get('query', '')).strip()
        
        if not query:
            return jsonify({'error': 'Empty query'}), 400
        
        chunks = db_manager.query(query, n_results=5)
        
        if not chunks:
            return jsonify({
                'answer': 'No relevant documents found.',
                'cited_files': [],
                'confidence_score': 0,
                'source_snippets': []
            })
        
        answer, cited_files, confidence_score, source_snippets = llm_service.generate_response(query, chunks)
        
        return jsonify({
            'answer': answer,
            'cited_files': cited_files,
            'confidence_score': confidence_score,
            'source_snippets': source_snippets
        })
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/download/<path:filename>')
def download_file(filename):
    """Download cited file"""
    try:
        # Search for file in sorted directory
        for root, dirs, files in os.walk(SORTED_DIR):
            if filename in files:
                filepath = os.path.join(root, filename)
                return send_file(filepath, as_attachment=True)
        
        return jsonify({'error': 'File not found'}), 404
        
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/export-chat', methods=['POST'])
def export_chat():
    """Export chat history as JSON or TXT"""
    try:
        data = request.get_json()
        format_type = data.get('format', 'json')
        chat_history = data.get('chat_history', [])
        
        if format_type == 'json':
            response_data = {
                'export_date': __import__('datetime').datetime.now().isoformat(),
                'total_messages': len(chat_history),
                'chat_history': chat_history
            }
            return jsonify(response_data)
        
        elif format_type == 'txt':
            txt_content = "DocuMind AI - Chat History\n"
            txt_content += f"Exported: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            txt_content += "=" * 60 + "\n\n"
            
            for msg in chat_history:
                txt_content += f"[{msg.get('timestamp', 'N/A')}] {msg.get('sender', 'Unknown')}\n"
                txt_content += f"{msg.get('text', '')}\n"
                if msg.get('confidence_score') is not None:
                    txt_content += f"Confidence: {msg.get('confidence_score', 0)}%\n"
                txt_content += "-" * 60 + "\n\n"
            
            return {'content': txt_content, 'format': 'txt'}
        
        return jsonify({'error': 'Unsupported format'}), 400
        
    except Exception as e:
        logger.error(f"Error exporting chat: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/status')
def status():
    """Get system status"""
    try:
        doc_count = db_manager.get_count()
        
        # Count files in sorted directory
        sorted_files = 0
        categories = []
        for category_dir in SORTED_DIR.iterdir():
            if category_dir.is_dir():
                categories.append(category_dir.name)
                sorted_files += len(list(category_dir.glob('*')))
        
        return jsonify({
            'database_count': doc_count,
            'sorted_files': sorted_files,
            'categories': categories,
            'ollama_available': llm_service.check_availability()
        })
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'error': str(e)}), 500


def check_ollama():
    """Check if Ollama is available"""
    try:
        ollama.list()
        return True
    except:
        return False


if __name__ == '__main__':
    logger.info("🚀 Starting DocuMind AI...")
    logger.info(f"📁 Database: {DB_DIR}")
    logger.info(f"📚 Documents: {db_manager.get_count()}")
    
    app.run(
        debug=False,  # Disable debug for stability
        host='0.0.0.0', 
        port=5000,
        threaded=True
    )
