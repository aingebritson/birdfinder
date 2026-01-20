"""
Species code generation utilities.

Generates 6-letter eBird-style species codes from common names.
Used by both the phenology pipeline and hotspot guide pipeline.
"""

import re


def generate_species_code(species_name: str, existing_codes: set = None) -> str:
    """
    Generate a unique 6-letter eBird-style species code.

    Takes first 3 letters of first word + first 3 letters of last word.
    If collision occurs, uses fallback strategies.

    Args:
        species_name: Common name of the species (e.g., "American Woodcock")
        existing_codes: Set of already-used codes to avoid collisions

    Returns:
        6-letter lowercase species code (e.g., "amewoo")
    """
    if existing_codes is None:
        existing_codes = set()

    # Remove parentheses and their contents
    clean_name = re.sub(r'\([^)]*\)', '', species_name).strip()

    # Split into words
    words = clean_name.split()

    # Generate base code
    if len(words) == 1:
        # Single word: take first 6 letters, pad with repeated letters if needed
        word = words[0].lower()
        if len(word) >= 6:
            base_code = word[:6]
        else:
            # Pad short words by repeating the word until we have 6 characters
            # e.g., "ruff" -> "ruffruff"[:6] -> "ruffru"
            base_code = (word * ((6 // len(word)) + 1))[:6]
    elif len(words) == 2:
        # Two words: 3 letters from each
        base_code = (words[0][:3] + words[1][:3]).lower()
    else:
        # Multiple words: first 3 of first word + first 3 of last word
        base_code = (words[0][:3] + words[-1][:3]).lower()

    # Check for collision
    if base_code not in existing_codes:
        return base_code

    # Collision detected - try alternatives
    # Strategy 1: Use more letters from last word (up to 4)
    if len(words) >= 2 and len(words[-1]) >= 4:
        alt_code = (words[0][:2] + words[-1][:4]).lower()
        if alt_code not in existing_codes:
            return alt_code

    # Strategy 2: For 3+ word names, use middle word
    if len(words) >= 3:
        alt_code = (words[0][:3] + words[1][:3]).lower()
        if alt_code not in existing_codes:
            return alt_code

    # Strategy 3: Use first 4 letters of first word + first 2 of last
    if len(words) >= 2:
        alt_code = (words[0][:4] + words[-1][:2]).lower()
        if alt_code not in existing_codes:
            return alt_code

    # Fallback: append number
    i = 2
    while f"{base_code[:5]}{i}" in existing_codes:
        i += 1
    return f"{base_code[:5]}{i}"
