from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pathlib import Path
from modules.llm_service import process_llm_query

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

from modules.ragsys import get_similar_cases
from modules.win_prediction import predict_win_probability

# from modules.llm_service import (
#     generate_case_roadmap,
#     generate_strong_arguments,
#     generate_case_evidence_analysis,
# )
from modules.llm_service import (
    generate_roadmap,
    generate_arguments,
    analyze_case,
)  # ensure these functions exist


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


# 🎯 New API: Create Case Roadmap
@app.route("/api/create-case-roadmap", methods=["POST"])
def case_roadmap():
    data = request.json
    case_text = data.get("case_details", "")

    if not case_text:
        return jsonify({"error": "Case details not provided"}), 400

    roadmap = generate_roadmap(case_text)
    return jsonify({"roadmap": roadmap})


# 🎯 New API: Generate Strong Court Arguments
@app.route("/api/generate-arguments", methods=["POST"])
def court_arguments():
    data = request.json
    case_text = data.get("case_details", "")

    if not case_text:
        return jsonify({"error": "Case details not provided"}), 400

    arguments = generate_arguments(case_text)
    return jsonify({"arguments": arguments})


# 🎯 New API: Analyze Case Evidence
@app.route("/api/analyze-evidence", methods=["POST"])
def evidence_analysis():
    data = request.json
    case_text = data.get("case_details", "")

    if not case_text:
        return jsonify({"error": "Case details not provided"}), 400

    analysis = analyze_case(case_text)
    return jsonify({"analysis": analysis})


@app.route("/api/legal-assistant", methods=["POST"])
def legal_assistant():
    data = request.json
    case_text = data.get("case_details", "")

    if not case_text:
        return jsonify({"error": "Case details not provided"}), 400

    result = process_llm_query(case_text)
    return jsonify(result)


@app.route("/generate_roadmap", methods=["POST"])
def roadmap():
    data = request.get_json()
    user_input = data.get("user_input", "")
    output = generate_roadmap(user_input)
    return jsonify({"response": output})


@app.route("/generate_arguments", methods=["POST"])
def arguments():
    data = request.get_json()
    user_input = data.get("user_input", "")
    output = generate_arguments(user_input)
    return jsonify({"response": output})


@app.route("/generate_analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    user_input = data.get("user_input", "")
    output = analyze_case(user_input)
    return jsonify({"response": output})


if __name__ == "__main__":
    app.run(debug=True)
