from transformers import AutoModelForCausalLM, AutoTokenizer
from pathlib import Path
import torch


class LegalLLM:
    def __init__(self):
        self.model_name = "microsoft/phi-2"
        self.model = None
        self.tokenizer = None

        self.model_path = Path("models/legal_llm")
        if self.model_path.exists():
            self.load_model()
        else:
            self.load_base_model()

    def load_base_model(self):
        """Load the base Phi-2 model from Hugging Face"""
        print("Loading base model from Hugging Face...")
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,  # Use float16 for faster inference
        )
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

        # Set padding token manually
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model.eval()  # Disable gradients for inference

        print("Base model loaded successfully.")

    def load_model(self):
        """Load a saved model if exists"""
        print("Loading saved model from disk...")
        self.model = AutoModelForCausalLM.from_pretrained(
            str(self.model_path), torch_dtype=torch.float16
        )
        self.tokenizer = AutoTokenizer.from_pretrained(str(self.model_path))

        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model.eval()  # Disable gradients for inference
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
            pad_token_id=self.tokenizer.eos_token_id,
        )
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response


# Instantiate the global LegalLLM object
legal_llm = LegalLLM()


# Example: Updated function to clean and return the model's response
def generate_case_roadmap(case_details: str) -> str:
    """Generate the legal case roadmap and return a cleaned version for display."""
    prompt = f"""
    You are a senior legal strategist. Based on the following case details, create a full step-by-step roadmap for winning or defending the case, covering investigation, filing, arguments, and possible appeals:

    Case Details:
    {case_details}

    Roadmap:
    """
    raw_response = legal_llm.generate_response(prompt)
    clean_output = clean_response(raw_response)
    return clean_output


def generate_strong_arguments(case_details: str) -> str:
    """Generate strong court arguments for the case and return a cleaned version."""
    prompt = f"""
    You are an experienced trial lawyer. Based on the case details below, list powerful and persuasive court arguments that could help win the case. Make sure to focus on the legal aspects and facts, with no code or additional exercises. Format the arguments as a simple list, with each argument on a new line:

    Case Details:
    {case_details}

    Arguments:
    """
    raw_response = legal_llm.generate_response(prompt)
    clean_output = clean_response(raw_response)
    return clean_output


def generate_case_evidence_analysis(case_details: str) -> str:
    """Analyze the case and provide a cleaned legal analysis."""
    prompt = f"""
    You are a seasoned lawyer. Analyze the case provided below, highlighting the potential impact of key evidence on the case outcome, any risks the client might face, and suggestions for strengthening the case. The analysis should be direct, legal in nature, and include:

    1. Key evidence and its potential impact on the case.
    2. Any risks posed by the case or the client's situation.
    3. Suggestions for strengthening the case.

    Please provide the analysis in a clear, legal format with no extra code examples or unrelated explanations. Do not include code in your response.

    Case Details:
    {case_details}

    Legal Analysis:
    """
    raw_response = legal_llm.generate_response(prompt)
    clean_output = clean_response(raw_response)
    return clean_output


import re


def clean_response(response: str) -> str:
    """
    Clean the model's output to strip out unwanted parts like 'Solution', 'Roadmap', etc.
    and return only the relevant legal information in a proper format.
    """
    # Remove any sections that are not useful, e.g., "Solution", "Roadmap", "Arguments", etc.
    response = re.sub(
        r"^(Solution:|Arguments:|Legal Analysis:|Roadmap:|Case Details:|Examples?[\n\s]*|)",
        "",
        response,
    )

    # Clean up excessive whitespace, multiple newlines, and redundant phrases
    response = re.sub(
        r"\n+", "\n", response
    )  # Replace multiple newlines with a single one
    response = response.strip()  # Remove leading/trailing whitespaces

    # If there are specific patterns that the model still includes, we can clean those too
    response = re.sub(
        r"\bYou are.*\b", "", response
    )  # Remove 'You are' instructions (if present)

    return response


if __name__ == "__main__":
    case_text = "my wife got divorce and took my son away. I want to get my son back. I have a good job and can provide for him. My wife is not a good mother and has a history of mental illness."

    print("\n=== Case Roadmap ===")
    print(generate_case_roadmap(case_text))

    print("\n=== Strong Court Arguments ===")
    print(generate_strong_arguments(case_text))

    print("\n=== Case Evidence Analysis ===")
    print(generate_case_evidence_analysis(case_text))
