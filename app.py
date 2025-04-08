from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Import modules
# from modules.document_processor import process_document
from modules.rag_system import retrieve_similar_cases
from modules.llm_service import generate_legal_analysis
from modules.win_prediction import predict_win_probability
from modules.chat_history import save_chat_history, load_chat_history

# @app.route('/api/process-document', methods=['POST'])
# def process_document_route():
#     try:
#         file = request.files['document']
#         text = process_document(file)
#         return jsonify({'text': text})
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-case', methods=['POST'])
def analyze_case():
    try:
        case_text = request.json.get('case_text')
        similar_cases = retrieve_similar_cases(case_text)
        win_probability = predict_win_probability(case_text)
        return jsonify({
            'similar_cases': similar_cases,
            'win_probability': win_probability
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message')
        chat_history = request.json.get('chat_history', [])
        response = generate_legal_analysis(user_message, chat_history)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/save-chat', methods=['POST'])
def save_chat():
    try:
        chat_data = request.json
        save_chat_history(chat_data)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/load-chat', methods=['GET'])
def load_chat():
    try:
        chat_id = request.args.get('chat_id')
        chat_history = load_chat_history(chat_id)
        return jsonify({'chat_history': chat_history})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 