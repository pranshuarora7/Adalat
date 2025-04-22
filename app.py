from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

from modules.ragsys import get_similar_cases  # Corrected import


@app.route("/api/retrieve-similar-cases", methods=["POST"])
def retrieve_cases():
    data = request.json
    user_input = data.get("query")

    if not user_input:
        return jsonify({"error": "Query not provided"}), 400

    results = get_similar_cases(user_input)
    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)
