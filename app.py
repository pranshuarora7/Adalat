from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os, json
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Import modules
from modules.document_processor import process_document
from modules.ragsys import get_similar_cases
from modules.llm_service import generate_legal_analysis
from modules.win_prediction import predict_win_probability
from modules.chat_history import save_chat_history, load_chat_history



# User data class
class UserData:
    def __init__(self):
        self.users_file = Path("data/users.json")
        self.users_file.parent.mkdir(parents=True, exist_ok=True)
        self.load_users()

    def load_users(self):
        if self.users_file.exists():
            with open(self.users_file, "r") as f:
                self.users = json.load(f)
        else:
            self.users = {}

    def save_users(self):
        with open(self.users_file, "w") as f:
            json.dump(self.users, f, indent=4)

    def add_user(self, email, username, password):
        if email in self.users:
            raise ValueError("User with this email already exists")
        self.users[email] = {"username": username, "password": password}
        self.save_users()

    def get_user(self, email):
        return self.users.get(email)


# Initialize user data
user_data = UserData()


@app.route('/api/process-document', methods=['POST'])
def process_document_route():
    try:
        file = request.files['document']
        text = process_document(file)
        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500











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


@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        if not all([email, username, password]):
            return jsonify({'error': 'Missing fields'}), 400
        
        user_data.add_user(email, username, password)
        return jsonify({'message': 'User registered successfully'}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = user_data.get_user(email)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if user['password'] != password:
        return jsonify({'error': 'Incorrect password'}), 401

    session['email'] = email 
    return jsonify({'message': 'Logged in successfully'}), 200

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