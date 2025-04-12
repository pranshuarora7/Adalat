from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments, Dataset, default_data_collator
import torch
import os
import random
from datasets import load_dataset
from pathlib import Path


class LegalLLM:
    def __init__(self):
        self.model_name = "microsoft/phi-2"
        self.model = None
        self.tokenizer = None
        
        self.model_path = Path('models/legal_llm')
        self.load_or_finetune_model()

    def load_or_finetune_model(self):
        """Load existing model or finetune on legal data"""
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.finetune_model()
        self.save_model()

    def load_model(self):
        """Load the finetuned model"""
        self.model = AutoModelForCausalLM.from_pretrained(str(self.model_path))
        self.tokenizer = AutoTokenizer.from_pretrained(str(self.model_path))

    def save_model(self):
        """Save the finetuned model"""
        self.model_path.mkdir(parents=True, exist_ok=True)
        self.model.save_pretrained(str(self.model_path))
        self.tokenizer.save_pretrained(str(self.model_path))

    def finetune_model(self):
        """Finetune the model on legal data"""
        print("Loading IL-TUR dataset...")
        dataset = load_dataset("Exploration-Lab/IL-TUR", "IL-PCR")

        # Prepare training data
        train_data = []
        for split in ['train_queries']:
            for case in dataset[split]:
                if 'text' in case:
                    text = " ".join(case['text'])
                else:
                    text = " ".join(case['document'])

                relevant_candidates = case['relevant_candidates']
                if relevant_candidates:
                    for candidate in relevant_candidates:
                        prompt = f"Given the legal case: {text} what are the relevant cases: {candidate}"
                        train_data.append(prompt)

        # Create dataset
        train_dataset = Dataset.from_dict({"text": train_data})
        tokenized_dataset = train_dataset.map(lambda examples: self.tokenizer(examples["text"]), batched=True)
        print("Training model...")
        training_args = TrainingArguments(
            output_dir="models/training_output",
            num_train_epochs=3,
            per_device_train_batch_size=1,
            logging_dir="logs"
        )
        trainer = Trainer(
            model=self.model, args=training_args, train_dataset=tokenized_dataset, data_collator=default_data_collator
        )
        trainer.train()

    def generate_response(self, prompt, system_prompts=None, max_length=500):
        """Generate response from the model"""
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(
            inputs.input_ids,
            max_length=max_length,
            num_return_sequences=1,
            temperature=0.7,
            top_p=0.9,
            do_sample=True
        )
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response

# Global instance
legal_llm = LegalLLM()


def generate_legal_analysis(user_message, chat_history):
    """Generate legal analysis using the LLM"""
    # Construct prompt with chat history and user message
    prompt = "You are a legal research assistant. Analyze the following case and provide insights:\n\n"

    # Add chat history if available
    if chat_history:
        prompt += "Previous conversation:\n"
        for msg in chat_history:
            role = "User" if msg['role'] == 'user' else "Assistant"
            prompt += f"{role}: {msg['content']}\n"
        prompt += "\n"

    prompt += f"User: {user_message}\nAssistant:"

    # Generate response
    response = legal_llm.generate_response(prompt)

    return response