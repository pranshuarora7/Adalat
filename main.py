# 1

# This file will be the entry point of your chatbot application.
# It will integrate all parts together and initiate the chatbot flow

# step-by-step breakdown:
#
# 1. Handle User Input:
        # We'll accept user input for querying.

# 2. Invoke CoLang Process:
        # Based on the input,
        # we will pass it to the CoLang process for determining the appropriate RAG logic.

# 3. Use the RAG Pipeline:
        # Based on the decision made by CoLang,
        # the query will either retrieve documents or call the generator to create a response.

# Imports:
        # We import all necessary modules, including the configuration, RAG processing, CoLang logic, and utility functions.
# handle_user_input():
        # This is the main function that ties everything together.
        # It preprocesses the input (like removing extra spaces or handling punctuation).
        # It then uses CoLang to decide the process (either retrieve or generate).
        # Based on the decision, it calls the RAG pipeline for document retrieval or generation.
        # Finally, it post-processes the output (e.g., formatting) before returning it.

# main.py

import openai

import os
import chromadb


from models.retriever import (  # ✅ Fixed import path (was "retreiver", now "retriever")
    retrieve_product_documents,
    retrieve_order_documents,
    retrieve_customer_documents,
    retrieve_default_documents
)

# Import functions for RAG and CoLang processing
from chatbot.process_input import process_user_input
from chatbot.coLang import handle_co_lang_logic

from models.generator import generate_response
from bot_config import load_configs
from data.document_indexer import index_documents  # Import the indexing function

import yaml
from nemoguardrails import RailsConfig, LLMRails  # ✅ Import RailsConfig


def setup_openai_api(config):
    openai.api_key = config["models"][0]["api_key"]
    os.environ["OPENAI_API_KEY"] = config["models"][0]["api_key"]



def setup_guardrails():
    with open("config/nemo_config.yml", "r") as f:
        guardrails_config_dict = yaml.safe_load(f)  # ✅ Load YAML as dict

    guardrails_config = RailsConfig(**guardrails_config_dict)  # ✅ Unpack dict

    rail = LLMRails(config=guardrails_config)  # ✅ Pass the correct object
    return rail



# ✅ Initialize ChromaDB and ensure documents are indexed before chatbot starts
def setup_chroma():
    chroma_client = chromadb.PersistentClient(path="data/chroma_db")
    collection = chroma_client.get_or_create_collection(name="knowledge_base")

    # Run indexing logic before starting chatbot
    index_documents("content_files")  # Pass the collection so it updates dynamically

    return collection  # Return updated collection for retrieval


def handle_user_input(user_input):
    """Processes user input and decides retrieval logic using CoLang."""
    preprocessed_input = process_user_input(user_input)
    decision = handle_co_lang_logic(preprocessed_input)
    return preprocessed_input, decision


def chatbot():
    # Load configurations and initialize components
    config, llm_config, guardrails_config = load_configs()
    setup_openai_api(config)
    rail = setup_guardrails()

    # ✅ Ensure documents are indexed before retrieval
    setup_chroma()

    print("Chatbot: Hi! How can I help you today?")

    while True:
        user_input = input("You: ")  # Take input from the user
        if user_input.lower() == "exit":  # Exit condition
            print("Chatbot: Take care, toodles!")
            break

        # Handle user input (Preprocess input and decide RAG logic)
        preprocessed_input, decision = handle_user_input(user_input)

        # Branching logic based on decision (✅ Removed unnecessary "collection" parameter)
        if decision == "product":
            context = retrieve_product_documents(preprocessed_input)
        elif decision == "order":
            context = retrieve_order_documents(preprocessed_input)
        elif decision == "customer":
            context = retrieve_customer_documents(preprocessed_input)
        else:
            context = retrieve_default_documents(preprocessed_input)

        # Generate a response using NeMo Guardrails with the retrieved context
        response = generate_response(preprocessed_input, context, rail)

        # Output the response
        print("Chatbot:", response)


# Start the chatbot when this script is executed
if __name__ == "__main__":
    chatbot()
