import re


def normalize_text(text: str) -> str:
    """
    Step 1 – Normalize raw extracted text.
    Standardizes formatting without lowercasing (segmenter uses .lower() internally).
    """
    # Normalize bullet variants to "-"
    text = re.sub(r"[•▪▸►◦‣⁃●]", "-", text)

    # Normalize unicode dashes to plain hyphen
    text = re.sub(r"[\u2013\u2014\u2012]", "-", text)

    # Normalize smart quotes
    text = re.sub(r"[\u2018\u2019]", "'", text)
    text = re.sub(r"[\u201c\u201d]", '"', text)

    # Remove non-printable control characters (keep newlines/tabs)
    text = re.sub(r"[^\x09\x0A\x0D\x20-\x7E]", " ", text)

    # Collapse multiple spaces/tabs on a single line
    text = re.sub(r"[ \t]+", " ", text)

    # Strip trailing whitespace per line
    lines = [l.rstrip() for l in text.split("\n")]
    text = "\n".join(lines)

    # Collapse more than 2 consecutive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()
