import httpx


OPENALEX_URL = "https://api.openalex.org/works"


async def search_literature(query: str, limit: int = 10):

    params = {
        "search": query,
        "per-page": limit,
        "select": (
            "id,title,publication_year,doi,"
            "authorships,primary_location,abstract_inverted_index"
        )
    }

    async with httpx.AsyncClient(timeout=30.0) as client:

        response = await client.get(
            OPENALEX_URL,
            params=params
        )

        response.raise_for_status()

        data = response.json()

    papers = []

    for work in data.get("results", []):

        authors = []

        for author in work.get("authorships", []):
            author_info = author.get("author")

            if author_info:
                authors.append(
                    author_info.get("display_name")
                )

        papers.append({
            "id": work.get("id"),
            "title": work.get("title"),
            "year": work.get("publication_year"),
            "doi": work.get("doi"),
            "authors": authors,
            "url": get_paper_url(work),
            "abstract": reconstruct_abstract(
                work.get("abstract_inverted_index")
            )
        })

    return papers


def get_paper_url(work):

    location = work.get("primary_location")

    if location:
        return location.get("landing_page_url")

    return None


def reconstruct_abstract(inverted_index):

    if not inverted_index:
        return None

    words = []

    for word, positions in inverted_index.items():

        for position in positions:

            words.append(
                (position, word)
            )

    words.sort()

    return " ".join(
        word for _, word in words
    )