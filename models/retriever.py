# Handles the retrieval of relevant documents based on the user’s query

# fetch relevant documents based on the category determined by coLang.py
# It interacts with the knowledge base to return the right context for the chatbot

# retriever.py, which will:
        # Connect to ChromaDB and retrieve documents based on similarity.
        # Use OpenAI embeddings to find the most relevant document for the query.
        # Work with main.py, coLang.py, and document_indexer.py

# What This Does:
        #  Connects to ChromaDB and retrieves the most relevant documents.
        #  Uses OpenAI embeddings for similarity search.
        #  Works with main.py & coLang.py for category-based retrieval.
        #  Returns the best-matching document (or default doc if nothing is found).

# retriever.py

# This module handles document retrieval from ChromaDB
# based on user queries, ensuring accurate context for response generation.

import chromadb
from chromadb.utils import embedding_functions
import yaml
import openai

# Load API key from config file
with open("config/project_config.yml", "r") as f:
    config = yaml.safe_load(f)

OPENAI_API_KEY = config["models"][0]["api_key"]

# Initialize OpenAI embedding function
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=OPENAI_API_KEY,
    model_name="text-embedding-ada-002"
)

# Connect to ChromaDB
chroma_client = chromadb.PersistentClient(path="data/chroma_db")
collection = chroma_client.get_or_create_collection(name="knowledge_base", embedding_function=openai_ef)


client = openai.OpenAI(api_key=OPENAI_API_KEY)  # Use the new OpenAI client

def generate_embedding(query):
    response = client.embeddings.create(
        input=query,
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding


def retrieve_documents(query: str, category: str, top_k=3):
    """
    Retrieves relevant documents from ChromaDB based on the query.

    :param query: The user query string.
    :param category: The category determined by CoLang.
    :param top_k: Number of top results to retrieve.
    :return: List of retrieved document texts.
    """

    query_embedding = generate_embedding(query)  # Generate query embedding

    # Perform similarity search in ChromaDB within the given category
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={"category": category}  # Filter by category
    )

    documents = results.get("documents", [[]])[0]  # Extract document texts

    if not documents:
        print(f"⚠️ No relevant documents found in '{category}'. Using default response.")
        return retrieve_default_documents(query)  # Fallback to default docs

    return documents  # Return retrieved documents


def retrieve_product_documents(query: str):
    """Retrieves relevant product-related documents."""
    return retrieve_documents(query, category="product")


def retrieve_order_documents(query: str):
    """Retrieves relevant order-related documents."""
    return retrieve_documents(query, category="order")


def retrieve_customer_documents(query: str):
    """Retrieves relevant customer-related documents."""
    return retrieve_documents(query, category="customer")


def retrieve_default_documents(query: str):
    """Retrieves default/general documents if no category matches."""
    return retrieve_documents(query, category="default", top_k=1)
