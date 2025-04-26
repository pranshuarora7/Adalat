from transformers import AutoModelForCausalLM, AutoTokenizer
from pathlib import Path
import torch

class LegalLLM:
    def __init__(self):
        self.model_name = "microsoft/phi-2"
        self.model = None
        self.tokenizer = None
        
        self.model_path = Path('models/legal_llm')
        if self.model_path.exists():
            self.load_model()
        else:
            self.load_base_model()

    def load_base_model(self):
        """Load the base Phi-2 model from Hugging Face"""
        print("Loading base model from Hugging Face...")
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name, torch_dtype=torch.float32)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

        # Set padding token manually
        self.tokenizer.pad_token = self.tokenizer.eos_token

        print("Base model loaded successfully.")

    def load_model(self):
        """Load a saved model if exists"""
        print("Loading saved model from disk...")
        self.model = AutoModelForCausalLM.from_pretrained(str(self.model_path))
        self.tokenizer = AutoTokenizer.from_pretrained(str(self.model_path))

        self.tokenizer.pad_token = self.tokenizer.eos_token
        print("Saved model loaded successfully.")

    def generate_response(self, prompt, max_length=200):
        """Generate a response for the given prompt"""
        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True)
        outputs = self.model.generate(
            input_ids=inputs.input_ids,
            attention_mask=inputs.attention_mask,
            max_length=max_length,
            num_return_sequences=1,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response


# Instantiate the global LegalLLM object
legal_llm = LegalLLM()


# 🎯 Function 1: Create Case Roadmap
def create_case_roadmap(case_details: str) -> str:
    """Create a detailed roadmap on how to approach the case."""
    prompt = f"You are a senior legal strategist. Based on the following case details, create a full step-by-step roadmap for winning or defending the case, covering investigation, filing, arguments, and possible appeals:\n\nCase Details:\n{case_details}\n\nRoadmap:"
    roadmap = legal_llm.generate_response(prompt)
    return roadmap


# 🎯 Function 2: Generate Strong Court Arguments
def generate_strong_arguments(case_details: str) -> str:
    """Suggest strong, attention-catching court arguments for the case."""
    prompt = f"You are an experienced trial lawyer. Given the case details below, list powerful and persuasive court arguments that can significantly improve the chance of winning:\n\nCase Details:\n{case_details}\n\nArguments:"
    arguments = legal_llm.generate_response(prompt)
    return arguments


# 🎯 Function 3: Detailed Case Analysis
def analyze_case_evidence(case_details: str) -> str:
    """Analyze the case and how different evidences could affect the chances."""
    prompt = f"You are a legal analyst. Analyze the case given below. Mention the impact of different types of evidence, risks involved, and how the case can be strengthened:\n\nCase Details:\n{case_details}\n\nAnalysis:"
    analysis = legal_llm.generate_response(prompt)
    return analysis

if __name__ == "__main__":
    case_text = "A company is being sued for breach of contract regarding a missed delivery deadline for essential goods."
    print("\n=== Case Roadmap ===")
    print(create_case_roadmap(case_text))
    
    print("\n=== Strong Court Arguments ===")
    print(generate_strong_arguments(case_text))
    
    print("\n=== Case Evidence Analysis ===")
    print(analyze_case_evidence(case_text))
