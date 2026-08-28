def chunk_pages(
    pages: list[dict],
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[dict]:

    chunks = []

    for page in pages:

        text = page["text"]
        metadata = page["metadata"]

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(
                    {
                        "text": chunk,
                        "metadata": metadata.copy(),
                    }
                )

            start += chunk_size - overlap

    return chunks

