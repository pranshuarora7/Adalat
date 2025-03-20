# 3


# Preprocesses the user input by cleaning extra spaces, handling punctuation,
#     and normalizing text for better processing.
#
#     Args:
#         user_input (str): The raw user input from the chatbot.
#
#     Returns:
#         str: The cleaned and processed user input.


# re is Python’s Regular Expressions (RegEx) module!
# It's used for pattern matching, searching, and modifying text using regex patterns.
import re

# only keep :
# \w → Word characters (A-Z, a-z, 0-9, and _)
# \s → Spaces
# ,.!? → Basic punctuation

# remove anything else

def process_user_input(user_input: str) -> str:
    cleaned_input = " ".join(user_input.split())
    # re.sub --> substitution function
    # searches for a pattern in a string and replaces it with something
    #
    # The r before a string makes it a raw string literal in Python.
    #
    # Normally, Python treats \ as an escape character (e.g., \n for new lines).
    # Using r"" means Python treats the string as-is and doesn’t escape special characters.
    cleaned_input = re.sub(r"[^\w\s,.!?]", "", cleaned_input)
    cleaned_input = cleaned_input.lower()

    return cleaned_input



