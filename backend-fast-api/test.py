import re

def no_xml_tags(text: str) -> bool:
    """
    Check if a given string contains no XML-like tags.

    Args:
        text (str): The input string to check.

    Returns:
        bool: True if there are no XML-like tags, False otherwise.
    """
    # Define the regex pattern to match XML-like tags
    pattern = r'<[^>]+>'
    
    # Search for any matches of the pattern in the text
    match = re.search(pattern, text)
    
    # Return True if no tags are found, False otherwise
    return match is None

# Example usage
example_text_with_tags = "<doc>This is a test.</doc>"
example_text_without_tags = "This is a test."

print(no_xml_tags(example_text_with_tags))  # Output: False
print(no_xml_tags(example_text_without_tags))  # Output: True
