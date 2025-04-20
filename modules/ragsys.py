# ragsys.py
from datasets import load_dataset
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import os
import pickle
from pathlib import Path


class RAGSystem:
    def __init__(self, datasets_to_load):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.case_texts = []
        self.case_metadata = []

        base_path = Path(__file__).resolve().parent.parent
        self.index_path = base_path / 'data' / 'rag_index'

        self.load_or_create_index(datasets_to_load)

    def load_or_create_index(self, datasets_to_load):
        if self.index_path.exists():
            self.load_index()
        else:
            self.create_index(datasets_to_load)
            self.save_index()

    def create_index(self, datasets_to_load):
        for dataset_path, config_name, splits in datasets_to_load:
            dataset = load_dataset(dataset_path, config_name)
            for split in splits:
                if split not in dataset:
                    continue
                for case in dataset[split]:
                    text = case.get("text") or case.get("document")
                    if isinstance(text, list):
                        text = " ".join(text)
                    if not isinstance(text, str):
                        continue
                    text = text.strip()
                    if not text:
                        continue

                    self.case_texts.append(text)
                    self.case_metadata.append({
                        'id': case.get('id', 'NA'),
                        'relevant_candidates': case.get('relevant_candidates', [])
                    })

        embeddings = self.model.encode(self.case_texts, show_progress_bar=True)
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype('float32'))

    def save_index(self):
        self.index_path.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.index_path / 'index.faiss'))
        with open(self.index_path / 'metadata.pkl', 'wb') as f:
            pickle.dump({
                'case_texts': self.case_texts,
                'case_metadata': self.case_metadata
            }, f)

    def load_index(self):
        self.index = faiss.read_index(str(self.index_path / 'index.faiss'))
        with open(self.index_path / 'metadata.pkl', 'rb') as f:
            data = pickle.load(f)
            self.case_texts = data['case_texts']
            self.case_metadata = data['case_metadata']

    def retrieve_similar_cases(self, query_text, k=5):
        query_embedding = self.model.encode([query_text])[0]
        distances, indices = self.index.search(query_embedding.reshape(1, -1).astype('float32'), k)

        results = []
        for idx, distance in zip(indices[0], distances[0]):
            results.append({
                'id': self.case_metadata[idx]['id'],
                'text': self.case_texts[idx],
                'similarity_score': float(1 / (1 + distance)),
                'relevant_cases': self.case_metadata[idx]['relevant_candidates']
            })
        return results


# Singleton instance to avoid reloading for every call
datasets_to_load = [
    ("Exploration-Lab/IL-TUR", "bail", ["train_all"]),
    ("Exploration-Lab/IL-TUR", "cjpe", ["multi_train"]),
    ("Exploration-Lab/IL-TUR", "lmt", ["acts"]),
    ("Exploration-Lab/IL-TUR", "lsi", ["train", "test", "dev", "statutes"]),
    ("Exploration-Lab/IL-TUR", "pcr", ["train_candidates", "train_queries"]),
    ("Exploration-Lab/IL-TUR", "summ", ["train", "test"]),
]
rag_system = RAGSystem(datasets_to_load)


def get_similar_cases(user_input: str, k=5):
    """Used by app.py to get RAG results"""
    return rag_system.retrieve_similar_cases(user_input, k)
