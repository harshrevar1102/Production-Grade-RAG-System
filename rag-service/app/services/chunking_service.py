import re


CHUNK_SIZE = 700
CHUNK_OVERLAP = 100


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text while preserving useful content.
    """

    text = text.replace("\x00", " ")

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def create_chunks(
    pages: list[dict],
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP
) -> list[dict]:
    """
    Create overlapping chunks from extracted PDF pages.

    Chunk size and overlap are currently measured in words.
    """

    if overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk size.")

    chunks = []

    for page in pages:

        page_number = page["page_number"]
        text = clean_text(page["text"])

        words = text.split()

        if not words:
            continue

        start = 0

        while start < len(words):

            end = min(start + chunk_size, len(words))

            chunk_words = words[start:end]

            chunk_text = " ".join(chunk_words).strip()

            if chunk_text:
                chunks.append({
                    "text": chunk_text,
                    "page_number": page_number,
                    "chunk_index": len(chunks)
                })

            if end >= len(words):
                break

            start = end - overlap

    return chunks