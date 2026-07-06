

def replace_with(element: str):
    """
    Replace special characters in a string with specified alternatives.
    Args:
        element (str): The input string to be processed.
    Returns:
        str: The processed string.
    """
    chars_a = [":", "+", "-", "<", ">", "(", ")", "[", "]"]
    chars_b = ["/", ".", ",", "-", "  ", " "]
    chars_c = ["ñ"]
    # first set of replace
    for char in chars_a:
        if char in element:
            element = element.replace(char, "")
    # second set of replace
    for char in chars_b:
        if char in element:
            element = element.replace(char, "_")
    # third set of replace
    for char in chars_c:
        if char in element:
            element = element.replace(char, "nn")
    return element



def remove_under_score(name):
    """
    Remove underscores from a string, replacing them with spaces.
    Useful for improving readability in graphics or tables where underscores may be present.
    Args:
        name (str): The input string from which to remove underscores.
    Returns:
        str: The processed string with underscores replaced by spaces.
    """
    if isinstance(name, str):
        name = name.replace("_", " ")
        return str(name)
    else:
        return name
