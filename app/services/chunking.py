import re
from typing import Literal


ChunkingStrategy = Literal["fixed", "sentence"]




def fixed_size_chunks(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[str]:
    """Split text into chunks at word boundaries with overlap."""

    if not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "Overlap must be non-negative and smaller than chunk size."
        )

    words = text.split()
    chunks = []
    current_words = []
    current_length = 0

    for word in words:
        added_length = len(word) + (1 if current_words else 0)

        if current_words and current_length + added_length > chunk_size:
            chunks.append(" ".join(current_words))

            # Keep the last words for context in the next chunk.
            overlap_words = []
            overlap_length = 0

            for previous_word in reversed(current_words):
                extra_length = len(previous_word) + (
                    1 if overlap_words else 0
                )

                if overlap_length + extra_length > overlap:
                    break

                overlap_words.insert(0, previous_word)
                overlap_length += extra_length

            current_words = overlap_words
            current_length = overlap_length

        added_length = len(word) + (1 if current_words else 0)
        current_words.append(word)
        current_length += added_length

    if current_words:
        chunks.append(" ".join(current_words))

    return chunks



def sentence_chunks(
    text: str,
    max_chars: int = 500,
) -> list[str]:
    """Group sentences together until the maximum size is reached."""

    if not text.strip():
        return []

    sentences = re.split(r"(?<=[.!?])\s+", text.strip())

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if not sentence.strip():
            continue

        if not current_chunk:
            current_chunk = sentence
        elif len(current_chunk) + len(sentence) + 1 <= max_chars:
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk)
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def chunk_text(
    text: str,
    strategy: ChunkingStrategy,
) -> list[str]:
    """Select the requested chunking strategy."""

    if strategy == "fixed":
        return fixed_size_chunks(text)

    if strategy == "sentence":
        return sentence_chunks(text)

    raise ValueError(f"Unsupported chunking strategy: {strategy}")
