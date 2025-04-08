from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from datasets import load_dataset
import numpy as np
import joblib
from pathlib import Path

class WinPredictor:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.model_path = Path('models/win_predictor')
        self.load_or_train_model()

    def load_or_train_model(self):
        """Load existing model or train new one"""
        if self.model_path.exists():
            self.load_model()
        else:
            self.train_model()
            self.save_model()

    def load_model(self):
        """Load trained model"""
        self.model = joblib.load(self.model_path / 'model.joblib')
        self.vectorizer = joblib.load(self.model_path / 'vectorizer.joblib')

    def save_model(self):
        """Save trained model"""
        self.model_path.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, self.model_path / 'model.joblib')
        joblib.dump(self.vectorizer, self.model_path / 'vectorizer.joblib')

    def train_model(self):
        """Train model on IL-TUR dataset"""
        print("Loading IL-TUR dataset...")
        dataset = load_dataset("Exploration-Lab/IL-TUR", "ILDC")
        
        # Prepare training data
        texts = []
        labels = []
        
        for split in ['train', 'dev', 'test']:
            for case in dataset[split]:
                text = " ".join(case['document'])
                texts.append(text)
                # Assuming binary classification (win/lose)
                # You might need to adjust this based on actual label format
                labels.append(1 if case['label'] == 1 else 0)
        
        print("Vectorizing texts...")
        self.vectorizer = TfidfVectorizer(max_features=5000)
        X = self.vectorizer.fit_transform(texts)
        
        print("Training model...")
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X, labels)

    def predict_win_probability(self, case_text):
        """Predict probability of winning the case"""
        # Vectorize input text
        X = self.vectorizer.transform([case_text])
        
        # Get probability predictions
        proba = self.model.predict_proba(X)[0]
        
        # Return probability of winning (class 1)
        return float(proba[1])

# Global instance
win_predictor = WinPredictor()

def predict_win_probability(case_text):
    """Wrapper function to predict win probability"""
    return win_predictor.predict_win_probability(case_text) 