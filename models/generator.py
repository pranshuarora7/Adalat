# Contains the logic to generate responses based on retrieved documents

# Take user_input and retrieved context
# Generate a response using OpenAI LLM
# Apply NeMo Guardrails to refine the response
# Return the final chatbot response

import os
from dotenv import load_dotenv  # ✅ Load environment variables
from rsa import key

# ✅ Load .env file
load_dotenv()

# ✅ Get OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("❌ OpenAI API key is missing! Set OPENAI_API_KEY in .env file.")

# ✅ Initialize OpenAI client
import openai
client = openai.OpenAI(api_key=OPENAI_API_KEY)


from nemoguardrails import RailsConfig, LLMRails

# ✅ Load NeMo Guardrails config correctly
config_path = "config/llm_config.yml"  # Make sure this is the correct folder with guardrails YAML files
print("Config Read Start")
rails_config = RailsConfig.from_path(config_path)
print("Config Read")
print(rails_config.models)
nemo_rails = LLMRails(config =rails_config)  # ✅ Pass the correct config



def generate_response(user_input, context, rail_instance: LLMRails):
    """
    Generates a response using OpenAI's LLM and refines it with NeMo Guardrails.

    Args:
        user_input (str): The user's input query.
        context (list): Retrieved documents providing relevant context.
        rail_instance (LLMRails): Initialized NeMo Guardrails instance.

    Returns:
        str: The final chatbot response.
    """

    # ✅ Step 1: Format context properly
    context_text = "\n".join(context) if context else "No relevant documents found."

    # ✅ Step 2: Construct LLM prompt
    prompt = f"User Query: {user_input}\n\nRelevant Context:\n{context_text}\n\nChatbot Response:"

    try:
        # ✅ Step 3: Generate response from OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": prompt}]
        )

        # ✅ Extract LLM response
        print("Generating Response")
        print("THIS IS RESPONSE : " , response)
        print("end of response.")
        print("\n\n")

        response_text = response.choices[0].message.content
        print(response_text, "\n\n")


        # ✅ Step 4: Ensure NeMo Guardrails has a valid config
        if not rail_instance.config:
            print("yes here is the error1")
            return "Error: No valid NeMo Guardrails config found."
        if not rail_instance.config.models:
            print("yes here is the error")
            return f"(⚠️ NeMo Guardrails is missing models! Responding with raw OpenAI output.)\n\n{response_text}"


        # ✅ Step 5: Pass OpenAI response to NeMo Guardrails for refinement
        final_response = rail_instance.generate(messages=[
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": response_text}
        ])

        return final_response

    except Exception as e:
        return f"Error generating response: {str(e)}"
