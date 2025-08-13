import difflib

def get_character_diffs(text1, text2):
    """
    Performs a character-level diff between two strings.

    Args:
        text1: The first string.
        text2: The second string.

    Returns:
        A list of opcodes from difflib.SequenceMatcher.
    """
    s = difflib.SequenceMatcher(None, text1, text2)
    return s.get_opcodes()
