from datasets import load_dataset
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import os
import pickle
from pathlib import Path

class RAGSystem:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.case_texts = []
        self.case_metadata = []
        self.index_path = Path('data/rag_index')
        self.load_or_create_index()

    def load_or_create_index(self):
        """Load existing index or create new one from IL-TUR dataset"""
        if self.index_path.exists():
            self.load_index()
        else:
            self.create_index()
            self.save_index()

    def create_index(self):
        """Create FAISS index from IL-TUR dataset"""
        print("Loading IL-TUR dataset...")
        dataset = load_dataset("Exploration-Lab/IL-TUR", "IL-PCR")
        
        print("Processing cases...")
        for split in ['train_queries', 'dev_queries', 'test_queries']:
            for case in dataset[split]:
                text = " ".join(case['text'])
                self.case_texts.append(text)
                self.case_metadata.append({
                    'id': case['id'],
                    'relevant_candidates': case['relevant_candidates']
                })

        print("Creating embeddings...")
        embeddings = self.model.encode(self.case_texts)
        
        print("Building FAISS index...")
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype('float32'))

    def save_index(self):
        """Save FAISS index and metadata"""
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, str(self.index_path / 'index.faiss'))
        
        # Save metadata
        with open(self.index_path / 'metadata.pkl', 'wb') as f:
            pickle.dump({
                'case_texts': self.case_texts,
                'case_metadata': self.case_metadata
            }, f)

    def load_index(self):
        """Load FAISS index and metadata"""
        self.index = faiss.read_index(str(self.index_path / 'index.faiss'))
        
        with open(self.index_path / 'metadata.pkl', 'rb') as f:
            data = pickle.load(f)
            self.case_texts = data['case_texts']
            self.case_metadata = data['case_metadata']

    def retrieve_similar_cases(self, query_text, k=5):
        """Retrieve k most similar cases to the query"""
        query_embedding = self.model.encode([query_text])[0]
        distances, indices = self.index.search(
            query_embedding.reshape(1, -1).astype('float32'), 
            k
        )
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            results.append({
                'id': self.case_metadata[idx]['id'],
                'text': self.case_texts[idx],
                'similarity_score': float(1 / (1 + distance)),
                'relevant_cases': self.case_metadata[idx]['relevant_candidates']
            })
        
        return results

# Global instance
rag_system = RAGSystem()

def retrieve_similar_cases(query_text):
    """Wrapper function to retrieve similar cases"""
    return rag_system.retrieve_similar_cases(query_text) 