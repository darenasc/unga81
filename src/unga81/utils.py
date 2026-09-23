import re


def wordcount(text):
    """This function counts the number of words in a given text.

    Args:
        text (str): The input text.

    Returns:
        int: The number of words in the text.
    """
    # Remove leading and trailing whitespace
    text = text.strip()

    # Remove punctuation
    text = re.sub(r"[^\w\s]", "", text)

    # Split the text into words
    words = text.split()

    # Count the number of words with characters
    return sum(len(word) for word in words if word.isalpha())
