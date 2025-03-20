# Holds your CoLang logic, handling any branching or conditions based on user input.

# handle logic for determining which RAG retrieval process to use based on user input (branching)


import chromadb

# Initialize ChromaDB client and collection
chroma_client = chromadb.PersistentClient(path="data/chroma_db")
collection = chroma_client.get_collection(name="knowledge_base")


def get_existing_categories() -> list:
    """Fetches all available document categories from ChromaDB."""
    metadata = collection.get(include=["metadatas"])
    return [meta["category"] for meta in metadata.get("metadatas", [])]  # Handle empty case

# Instead of hardcoding, we’ll:
        # Extract keywords from the actual indexed .md files
        # Dynamically match user input based on those categories


CATEGORY_KEYWORDS = {
    "order": ["order", "purchase", "track", "shipment"],
    "product": ["product", "item", "details", "specs"],
    "customer": ["customer", "account", "profile", "support"]
}

def handle_co_lang_logic(preprocessed_input: str) -> str:
    """Determines category based on user input and existing document categories."""
    existing_categories = get_existing_categories()

    # Check for exact category match first
    for category in existing_categories:
        if category in preprocessed_input.lower():
            return category

    # Check for keyword-based matching
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in preprocessed_input.lower() for keyword in keywords):
            if category in existing_categories:
                return category  # Only return if it's actually indexed

    return "default"


