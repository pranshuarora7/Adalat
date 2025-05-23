from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from datasets import load_dataset
from collections import Counter
import joblib
import numpy as np
import re
from pathlib import Path


def preprocess(text):
    """Clean and preprocess case text"""
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


class WinPredictor:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.model_path = Path("models/win_predictor")
        self.load_or_train_model()

    def load_model(self):
        """Load trained model"""
        self.model = joblib.load(self.model_path / "model.joblib")
        self.vectorizer = joblib.load(self.model_path / "vectorizer.joblib")
        print("✅ Loaded saved model and vectorizer.")

    def save_model(self):
        """Save trained model"""
        self.model_path.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, self.model_path / "model.joblib")
        joblib.dump(self.vectorizer, self.model_path / "vectorizer.joblib")
        print("✅ Model and vectorizer saved.")

    def load_or_train_model(self):
        """Check if model exists, otherwise train"""
        if (self.model_path / "model.joblib").exists() and (self.model_path / "vectorizer.joblib").exists():
            self.load_model()
        else:
            self.train_model()
            self.save_model()

    def train_model(self):
        """Train model from IL-TUR cjpe dataset"""
        print("📦 Loading IL-TUR cjpe dataset...")
        dataset = load_dataset("Exploration-Lab/IL-TUR", "cjpe")

        texts, labels = [], []

        for split in ["multi_train", "multi_dev", "test"]:
            if split not in dataset:
                continue
            for item in dataset[split]:
                text = item.get("text")
                label = item.get("label")
                if not text or label is None:
                    continue
                label = int(label)
                if label not in [0, 1]:
                    continue
                cleaned = preprocess(text)
                if len(cleaned.split()) < 10:
                    continue
                texts.append(cleaned)
                labels.append(label)

        print(f"🧾 Total samples used: {len(texts)}")
        print("📊 Label distribution:", Counter(labels))

        if len(set(labels)) < 2:
            raise ValueError("❌ Dataset does not have both win/loss classes.")

        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=0.2, random_state=42, stratify=labels
        )

        self.vectorizer = TfidfVectorizer(max_features=5000)
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)

        self.model = RandomForestClassifier(
            n_estimators=200, class_weight="balanced", random_state=42
        )
        self.model.fit(X_train_vec, y_train)

        y_pred = self.model.predict(X_test_vec)
        print("📈 Model Evaluation:")
        print(classification_report(y_test, y_pred))

    def predict_win_probability(self, case_text):
        """Predict probability of winning a case"""
        if not self.model or not self.vectorizer:
            raise ValueError("❌ Model not loaded.")
        cleaned = preprocess(case_text)
        vec = self.vectorizer.transform([cleaned])
        proba = self.model.predict_proba(vec)[0]
        class_indices = self.model.classes_

        if 1 in class_indices:
            return float(proba[list(class_indices).index(1)])
        else:
            return 0.0


# Global instance
win_predictor = WinPredictor()


def predict_win_probability(case_text):
    return win_predictor.predict_win_probability(case_text)


# Optional: Run test
if __name__ == "__main__":
    test_text = "The plaintiff is seeking relief against unfair eviction under the tenancy act and has supporting documentation of tenancy and rent payments."
    probability = predict_win_probability(test_text)
    print(f"🔮 Predicted win probability: {probability:.2f}")
