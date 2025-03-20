# This will handle the logic for indexing documents,
# ensuring that they are ready to be used in your RAG pipeline

import os
import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI
import yaml

# Load API key from config file
with open("config/project_config.yml", "r") as f:
    config = yaml.safe_load(f)

OPENAI_API_KEY = config["models"][0]["api_key"]

# Initialize OpenAI embedding function
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=OPENAI_API_KEY,
    model_name="text-embedding-ada-002"
)

# Initialize ChromaDB client
# 1. First, ChromaDB checks if the data/chroma_db directory exists.
        # If it doesn’t, it creates the directory to store embeddings.
        # If it already exists, it loads previous data.
# 2. Then, ChromaDB looks for a collection named "knowledge_base".
        # If the collection already exists, it retrieves it.
        # If it doesn't exist, it creates a new one.
# 3. Finally, when we add documents to this collection, ChromaDB:
        # Sends the text to OpenAI for embedding generation.
        # Stores the text + embeddings in the "knowledge_base" collection.
        # Allows fast retrieval later using similarity search.
chroma_client = chromadb.PersistentClient(path="data/chroma_db")  # Store the vector DB in /data folder
collection = chroma_client.get_or_create_collection(name="knowledge_base", embedding_function=openai_ef)


def index_documents(content_folder="content_files"):
    """Reads .md files, updates modified documents, and indexes new ones in ChromaDB."""

    # How Does This Work? LOGIC :
    # First, we fetch all indexed documents and store their categories in existing_docs.
    # For each .md file, we check:
    # If it's already indexed, we compare the stored vs. new content.
    # If the content is unchanged, we skip re-indexing.
    # If the content has changed, we delete the old index and re-index it.
    # New files are indexed normally.

    existing_docs_data = collection.get(include=["metadatas"])
    existing_docs = {metadata["category"] for metadata in existing_docs_data.get("metadatas", [])}

    for file_name in os.listdir(content_folder):
        if file_name.endswith(".md"):
            file_path = os.path.join(content_folder, file_name)
            category = file_name.replace(".md", "")  # Extract category name

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check if the document is already indexed
            if category in existing_docs:
                # Fetch existing content from the vector store (metadata lookup)
                stored_content = collection.get(where={"category": category}, include=["documents"])["documents"][0]

                if stored_content == content:
                    print(f"🔹 No changes detected in: {file_name}. Skipping indexing.")
                    continue  # Skip re-indexing unchanged files
                else:
                    print(f"🔄 Changes detected in: {file_name}. Updating indexing...")
                    collection.delete(where={"category": category})  # Remove old entry

            # Add new or updated document to ChromaDB
            collection.add(
                ids=[file_name],  # Unique ID for retrieval
                documents=[content],  # Full document text
                metadatas=[{"category": category}]  # Metadata for filtering
            )

            print(f"✅ Indexed: {file_name}")

    print("\n🎉 All new/modified documents indexed successfully!")



if __name__ == "__main__":
    if collection.count() == 0:  # collection.count() returns the number of indexed docs
        print("No indexed documents found. Running indexing process...")
        index_documents()
    else:
        print("Documents are already indexed. Skipping indexing.")
