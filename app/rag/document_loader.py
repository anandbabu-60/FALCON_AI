import fitz


def load_pdf(file_path: str) -> list[dict]:
    document = fitz.open(file_path)

    pages = []

    for page_number, page in enumerate(document, start=1):
        text = page.get_text().strip()

        if not text:
            continue

        pages.append(
            {
                "text": text,
                "metadata": {
                    "source": file_path,
                    "page": page_number,
                },
            }
        )

    document.close()

    return pages