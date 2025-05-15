# # llm_service.py

# import torch
# from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments, pipeline
# from datasets import load_dataset
# import numpy as np
# from sklearn.metrics import accuracy_score, precision_recall_fscore_support
# import os

# class LegalLLM:
#     def __init__(self, model_path=None):
#         """
#         Initialize the Legal LLM service

#         Args:
#             model_path: Path to load a pre-trained model from (if None, will train a new one)
#         """
#         print("✅ Loading base model...")
#         self.model_name = "bert-base-uncased"
#         self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
#         self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name, num_labels=8)

#         # Check for CUDA availability
#         self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#         print(f"Using device: {self.device}")

#         self.model.to(self.device)

#         # Always run fine-tuning for now to avoid dependency on saved model
#         print("Training new model...")
#         self.load_and_finetune_model()

#         # Load a more capable text generation model for the generation tasks
#         print("Loading text generation model...")
#         try:
#             # Try loading GPT-2 medium for better generation capabilities
#             self.text_gen_pipeline = pipeline(
#                 "text-generation",
#                 model="gpt2-medium",
#                 tokenizer="gpt2-medium",
#                 device=0 if torch.cuda.is_available() else -1
#             )
#         except Exception as e:
#             print(f"Failed to load gpt2-medium, falling back to gpt2: {e}")
#             self.text_gen_pipeline = pipeline(
#                 "text-generation",
#                 model="gpt2",
#                 tokenizer="gpt2",
#                 device=0 if torch.cuda.is_available() else -1
#             )

#         print("Model initialization complete")

#     def preprocess_data(self, dataset):
#         """
#         Preprocess dataset for training

#         Args:
#             dataset: Dataset to preprocess

#         Returns:
#             Processed train and validation datasets
#         """
#         print("Preprocessing dataset...")

#         def preprocess_example(example):
#             # Process text and labels safely
#             if not example.get("text") or not isinstance(example["text"], list) or len(example["text"]) == 0:
#                 return None

#             # Join text fields if there are multiple
#             input_text = " ".join(example["text"]) if isinstance(example["text"], list) else example["text"]

#             # Get labels - handling both single label and multi-label cases
#             labels = example.get("labels", [])
#             if not labels:
#                 return None

#             # Take the first label for single label classification
#             label = labels[0] if isinstance(labels, list) else labels

#             return {
#                 "input_text": input_text,
#                 "label": label
#             }

#         # Process the datasets
#         train_data = [preprocess_example(ex) for ex in dataset["train"]]
#         val_data = [preprocess_example(ex) for ex in dataset["validation"]]

#         # Filter out None values
#         train_data = [ex for ex in train_data if ex is not None]
#         val_data = [ex for ex in val_data if ex is not None]

#         print(f"Processed {len(train_data)} training examples and {len(val_data)} validation examples")

#         return train_data, val_data

#     def load_and_finetune_model(self):
#         """Load the dataset and fine-tune the model"""
#         print("📥 Loading legal dataset (lex_glue: ecthr_a)...")
#         dataset = load_dataset("lex_glue", "ecthr_a")

#         print("🧹 Preprocessing...")
#         train_data, val_data = self.preprocess_data(dataset)

#         # Extract text and labels
#         train_texts = [x["input_text"] for x in train_data]
#         train_labels = [x["label"] for x in train_data]

#         val_texts = [x["input_text"] for x in val_data]
#         val_labels = [x["label"] for x in val_data]

#         # Tokenize the data
#         print("Tokenizing data...")
#         train_encodings = self.tokenizer(
#             train_texts,
#             truncation=True,
#             padding="max_length",
#             max_length=512,
#             return_tensors="pt"
#         )

#         val_encodings = self.tokenizer(
#             val_texts,
#             truncation=True,
#             padding="max_length",
#             max_length=512,
#             return_tensors="pt"
#         )

#         # Create dataset class
#         class LegalDataset(torch.utils.data.Dataset):
#             def __init__(self, encodings, labels):
#                 self.encodings = encodings
#                 self.labels = labels

#             def __len__(self):
#                 return len(self.labels)

#             def __getitem__(self, idx):
#                 item = {key: val[idx] for key, val in self.encodings.items()}
#                 item["labels"] = torch.tensor(self.labels[idx])
#                 return item

#         train_dataset = LegalDataset(train_encodings, train_labels)
#         val_dataset = LegalDataset(val_encodings, val_labels)

#         print("🛠️ Fine-tuning model...")

#         # Set up training arguments - compatible with older Transformers versions
#         training_args = TrainingArguments(
#             output_dir="./results",
#             num_train_epochs=3,  # Increased from 1 to 3 for better convergence
#             per_device_train_batch_size=16,
#             per_device_eval_batch_size=16,
#             warmup_steps=500,
#             weight_decay=0.01,
#             logging_dir="./logs",
#             logging_steps=100,
#             save_total_limit=2,
#             # Removed parameters that might not be compatible with older versions
#         )

#         def compute_metrics(p):
#             preds = np.argmax(p.predictions, axis=1)
#             precision, recall, f1, _ = precision_recall_fscore_support(p.label_ids, preds, average="weighted")
#             acc = accuracy_score(p.label_ids, preds)
#             return {"accuracy": acc, "f1": f1, "precision": precision, "recall": recall}

#         trainer = Trainer(
#             model=self.model,
#             args=training_args,
#             train_dataset=train_dataset,
#             eval_dataset=val_dataset,
#             compute_metrics=compute_metrics,
#         )

#         trainer.train()

#         # Save the best model
#         self.model = trainer.model
#         torch.save(self.model.state_dict(), "./best_legal_model.pt")
#         print("✅ Fine-tuning complete. Model saved to ./best_legal_model.pt")

#     def predict(self, text):
#         """
#         Predict the legal category of the input text

#         Args:
#             text: Input text to classify

#         Returns:
#             Predicted class as an integer
#         """
#         inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
#         inputs = {k: v.to(self.device) for k, v in inputs.items()}

#         self.model.eval()
#         with torch.no_grad():
#             outputs = self.model(**inputs)
#             logits = outputs.logits
#             predicted_class = torch.argmax(logits, dim=1).item()

#         return predicted_class

#     def generate_roadmap(self, text: str) -> str:
#         """
#         Generate a legal case roadmap from the input text

#         Args:
#             text: Case description

#         Returns:
#             Roadmap text with process steps and flow chart
#         """
#         # Improved prompt with more detail on what we want
#         prompt = (
#             f"As an expert legal assistant, create a detailed roadmap for winning this case. "
#             f"Include specific steps from beginning to end, procedural requirements, and key milestones. "
#             f"Then create a flow chart representation using bullet points and dashes. "
#             f"Case description: {text}\n\n"
#             f"ROADMAP FOR CASE:\n"
#             f"1. Initial steps:\n"
#         )

#         outputs = self.text_gen_pipeline(
#             prompt,
#             max_length=500,  # Increased for more detailed output
#             num_return_sequences=1,
#             temperature=0.7,  # Lower temperature for more focused output
#             do_sample=True
#         )

#         output_text = outputs[0]["generated_text"]
#         # Extract only the generated part (remove the prompt)
#         roadmap = output_text[len(prompt):].strip()

#         # Add flow chart header if missing
#         if "FLOW CHART:" not in roadmap:
#             roadmap += "\n\nFLOW CHART:\n• Case initiation\n  ↓\n• Evidence gathering\n  ↓\n• Legal research\n  ↓\n• Filing motions\n  ↓\n• Court proceedings\n  ↓\n• Resolution"

#         return roadmap

#     def extract_arguments(self, text: str) -> list:
#         """
#         Extract key legal arguments from the case text

#         Args:
#             text: Case description

#         Returns:
#             List of key arguments
#         """
#         prompt = (
#             f"As an expert legal assistant, extract the strongest legal arguments that would help win this case. "
#             f"Focus on constitutional principles, precedents, and statutory interpretations. For each argument, "
#             f"provide the legal basis and potential impact. "
#             f"Case description: {text}\n\n"
#             f"KEY LEGAL ARGUMENTS:\n"
#             f"1. "
#         )

#         outputs = self.text_gen_pipeline(
#             prompt,
#             max_length=500,
#             num_return_sequences=1,
#             temperature=0.7,
#             do_sample=True
#         )

#         output_text = outputs[0]["generated_text"]
#         arguments_section = output_text[len(prompt)-3:].strip()  # Keep the "1. " part

#         # Process the arguments into a clean list
#         raw_arguments = arguments_section.split('\n')
#         arguments = []

#         current_arg = ""
#         for line in raw_arguments:
#             # If this is a new argument (starts with number or bullet point)
#             if line.strip() and (line.strip()[0].isdigit() or line.strip()[0] in ['•', '-', '*']):
#                 if current_arg:  # Save previous argument if exists
#                     arguments.append(current_arg.strip())
#                 current_arg = line.strip()
#             else:
#                 current_arg += " " + line.strip()

#         # Add the last argument
#         if current_arg:
#             arguments.append(current_arg.strip())

#         # Clean up formatting
#         arguments = [arg.strip().lstrip('1234567890.-*• ') for arg in arguments if arg.strip()]

#         return arguments

#     def generate_analysis(self, text: str) -> str:
#         """
#         Generate a comprehensive legal analysis of the case

#         Args:
#             text: Case description

#         Returns:
#             Detailed legal analysis
#         """
#         prompt = (
#             f"As an expert legal assistant, provide a thorough legal analysis of this case. "
#             f"Include: 1) Relevant legal principles and precedents, 2) Strengths and weaknesses of the case, "
#             f"3) Probability of success based on similar past cases, 4) Potential counterarguments, and "
#             f"5) Strategic recommendations. "
#             f"Case description: {text}\n\n"
#             f"LEGAL ANALYSIS:\n"
#         )

#         outputs = self.text_gen_pipeline(
#             prompt,
#             max_length=800,  # Longer for comprehensive analysis
#             num_return_sequences=1,
#             temperature=0.7,
#             do_sample=True
#         )

#         output_text = outputs[0]["generated_text"]
#         analysis = output_text[len(prompt):].strip()

#         # Structure the analysis with headers if missing
#         if "LEGAL PRINCIPLES:" not in analysis:
#             sections = [
#                 "LEGAL PRINCIPLES AND PRECEDENTS:",
#                 "CASE STRENGTHS AND WEAKNESSES:",
#                 "PROBABILITY OF SUCCESS:",
#                 "POTENTIAL COUNTERARGUMENTS:",
#                 "STRATEGIC RECOMMENDATIONS:"
#             ]

#             structured_analysis = ""
#             remaining_text = analysis

#             for section in sections:
#                 structured_analysis += f"\n\n{section}\n"
#                 # Take approx 1/5 of remaining text for each section
#                 section_length = max(50, len(remaining_text) // (5 - sections.index(section)))
#                 structured_analysis += remaining_text[:section_length]
#                 remaining_text = remaining_text[section_length:]

#             analysis = structured_analysis

#         return analysis

#     def get_case_label(self, class_id):
#         """
#         Convert numerical class ID to human-readable label

#         Args:
#             class_id: Numerical class ID from prediction

#         Returns:
#             Human-readable label
#         """
#         labels = {
#             0: "Right to life (Article 2)",
#             1: "Prohibition of torture (Article 3)",
#             2: "Right to liberty and security (Article 5)",
#             3: "Right to a fair trial (Article 6)",
#             4: "Right to respect for private and family life (Article 8)",
#             5: "Freedom of thought, conscience and religion (Article 9)",
#             6: "Freedom of expression (Article 10)",
#             7: "Other articles of the European Convention on Human Rights"
#         }

#         return labels.get(class_id, "Unknown article")


# # For testing
# if __name__ == "__main__":
#     legal_llm = LegalLLM()  # No longer trying to load a saved model

#     test_text = "The applicant argued that her freedom of expression was violated by the national authorities when they prevented her from publishing her critical analysis of government policies."

#     # Get predictions
#     class_id = legal_llm.predict(test_text)
#     class_label = legal_llm.get_case_label(class_id)

#     print(f"\n🔍 Predicted class: {class_id} - {class_label}\n")

#     print(f"🗺️ Roadmap:\n{legal_llm.generate_roadmap(test_text)}\n")

#     arguments = legal_llm.extract_arguments(test_text)
#     print(f"⚖️ Arguments:")
#     for i, arg in enumerate(arguments, 1):
#         print(f"{i}. {arg}")
#     print()

#     print(f"📚 Analysis:\n{legal_llm.generate_analysis(test_text)}\n")
# llm_service.py

# llm_service.py
import google.generativeai as genai
import os

# ✅ Configure Gemini API Key
genai.configure(
    api_key=os.getenv("GEMINI_API_KEY") or "AIzaSyAVL1hfzDmgoQNeN-MaE6_mKJM_56vRhgQ"
)

# ✅ Create the model
model = genai.GenerativeModel(
    model_name="models/gemini-1.5-flash",
    system_instruction=(
        "You are Adalat, an expert legal assistant and lawyer. "
        "You only answer legal queries in a formal, professional tone. "
        "For each case, you can summarize, provide a legal roadmap, and suggest next steps."
    ),
)


# 🧠 Query classification
def classify_query(text):
    text_lower = text.lower()
    if any(
        word in text_lower
        for word in ["next step", "should i do", "what now", "next action"]
    ):
        return "next"
    elif any(word in text_lower for word in ["summary", "summarize", "explain"]):
        return "summary"
    elif any(
        word in text_lower
        for word in ["roadmap", "legal process", "procedure", "stages"]
    ):
        return "roadmap"
    elif len(text.split()) > 50:
        return "full_case"
    else:
        return "general"


def analyze_case(text):
    return model.generate_content(
        f"""
You are an expert legal analyst. Analyze the following case and identify:
- The key pieces of evidence or testimony mentioned
- Which parts of the case are weak or vulnerable
- Which aspects are strong or favorable
- Any critical points that require further clarification

Structure your analysis clearly with bullet points or short sections.
Give short answer, no more than 1-2 sentences per point.
Case details:
{text}
"""
    ).text.strip()


def generate_roadmap(text):
    return model.generate_content(
        f"""
You are a highly experienced legal expert known for creating step-by-step legal roadmaps.
Given the following legal case, provide a clear, detailed, and logical roadmap that outlines the key steps a lawyer should take to win or strengthen the case.

Be specific about:
- Filing or documentation steps
- Evidence collection or witness preparation
- Legal arguments to be prepared
- Important legal procedures or deadlines

Present the roadmap in bullet points or numbered steps. and keep it short not very detailed
Give short answer, no more than 1-2 sentences per point.

Case details:
{text}
"""
    ).text.strip()


def generate_arguments(text):
    return model.generate_content(
        f"""
You are a senior legal strategist. Given the following legal case, generate powerful and well-reasoned legal arguments that a lawyer could use in court to support their client.

Focus on:
- How existing facts support the client’s position
Give arguements in small points by using earlier similar cases and tell in plain english you can speak these in court:-
Structure your response as bullet points for each argument in short
Give short answer, no more than 1-2 sentences per point.

Case details:
{text}
"""
    ).text.strip()


# 🔄 Unified handler
def process_llm_query(user_input):
    query_type = classify_query(user_input)

    try:
        if query_type == "roadmap":
            return {"type": "roadmap", "response": generate_roadmap(user_input)}
        elif query_type == "summary":
            return {"type": "summary", "response": analyze_case(user_input)}
        elif query_type == "next":
            return {"type": "next_steps", "response": generate_arguments(user_input)}
        elif query_type == "full_case":
            return {
                "type": "full_case",
                "summary": analyze_case(user_input),
                "roadmap": generate_roadmap(user_input),
                "next_steps": generate_arguments(user_input),
            }
        else:
            return {
                "type": "general",
                "response": model.generate_content(user_input).text,
            }
    except Exception as e:
        return {"error": str(e)}
