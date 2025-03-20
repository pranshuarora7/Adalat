# 2

# Store all configurations like file paths, database connections, and general settings here

# WHAT IT DOES :
# Configuration data related to the chatbot’s behavior (like paths to YAML files, API keys, etc.).
# Loading functions for the configurations (using yaml)

import yaml
import sys  # ✅ Import sys to exit on failure

def load_configs():
    try:
        with open("config/project_config.yml", "r") as f:
            config = yaml.safe_load(f)

        with open("config/llm_config.yml", "r") as f:
            llm_config = yaml.safe_load(f)

        with open("config/nemo_config.yml", "r") as f:
            guardrails_config = yaml.safe_load(f)

        return config, llm_config, guardrails_config

    except Exception as e:
        print(f"❌ Error loading configuration files: {e}")
        sys.exit(1)  # 🔥 Exit the script if config files can't be loaded
