from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

from modules.ragsys import get_similar_cases
from modules.win_prediction import predict_win_probability


@app.route("/api/retrieve-similar-cases", methods=["POST"])
def retrieve_cases():
    data = request.json
    user_input = data.get("query")

    if not user_input:
        return jsonify({"error": "Query not provided"}), 400

    results = get_similar_cases(user_input)
    return jsonify(results)


@app.route("/api/predict-win-probability", methods=["POST"])
def predict_win():
    data = request.json
    case_text = data.get("case_details", "")

    if not case_text:
        return jsonify({"error": "Case details not provided"}), 400

    probability = predict_win_probability(case_text)
    return jsonify({"probability": probability})


if __name__ == "__main__":
    app.run(debug=True)
