from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from datasets import load_dataset
import numpy as np
import joblib
from pathlib import Path
from collections import Counter

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
        print("✅ Model loaded.")

    def save_model(self):
        """Save trained model"""
        self.model_path.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, self.model_path / 'model.joblib')
        joblib.dump(self.vectorizer, self.model_path / 'vectorizer.joblib')
        print("✅ Model saved.")

    def train_model(self):
        """Train model on IL-TUR cjpe dataset"""
        print("📦 Loading IL-TUR cjpe dataset...")
        dataset = load_dataset("Exploration-Lab/IL-TUR", "cjpe")

        texts = []
        labels = []

        # Use all available splits with label
        for split in ['multi_train', 'multi_dev', 'test']:
            if split not in dataset:
                continue

            for item in dataset[split]:
                text = item.get('text')
                label = item.get('label')

                if not text or label is None:
                    continue

                label_int = int(label)
                if label_int not in [0, 1]:
                    continue

                texts.append(text.strip())
                labels.append(label_int)

        print(f"🧾 Collected {len(texts)} samples.")
        print("📊 Label distribution:", Counter(labels))

        if len(set(labels)) < 2:
            raise ValueError("❌ Dataset does not contain both labels (0 and 1). Cannot train classifier.")

        self.vectorizer = TfidfVectorizer(max_features=5000)
        X = self.vectorizer.fit_transform(texts)

        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X, labels)
        print("✅ Model training complete.")

    def predict_win_probability(self, case_text):
        """Predict probability of winning the case"""
        X = self.vectorizer.transform([case_text])
        proba = self.model.predict_proba(X)[0]
        class_indices = self.model.classes_

        if 1 in class_indices:
            return float(proba[list(class_indices).index(1)])
        else:
            return 0.0  # Return 0 probability if model never saw class 1

# Global instance
win_predictor = WinPredictor()

def predict_win_probability(case_text):
    """Wrapper function to predict win probability"""
    return win_predictor.predict_win_probability(case_text)

# Optional: Test prediction
if __name__ == "__main__":
    sample_text = "The appellants are seeking relief under the Rent Control Act..."
    probability = predict_win_probability(sample_text)
    print(f"🔮 Predicted win probability: {probability:.2f}")
