import os
import asyncio
import httpx

from dotenv import load_dotenv


load_dotenv()


OPENALEX_URL = "https://api.openalex.org/works"
OPENALEX_API_KEY = os.getenv("OPENALEX_API_KEY")


async def search_literature(
    query: str,
    limit: int = 10
):

    if not OPENALEX_API_KEY:
        raise RuntimeError(
            "OPENALEX_API_KEY is not set"
        )

    params = {
        "search": query,
        "per-page": limit,
        "select": (
            "id,title,publication_year,doi,"
            "authorships,primary_location,"
            "abstract_inverted_index"
        ),
        "api_key": OPENALEX_API_KEY,
    }

    max_retries = 3

    async with httpx.AsyncClient(
        timeout=30.0
    ) as client:

        for attempt in range(max_retries):

            response = await client.get(
                OPENALEX_URL,
                params=params
            )

            # --------------------------------------------
            # Success
            # --------------------------------------------

            if response.status_code == 200:
                data = response.json()
                break

            # --------------------------------------------
            # Rate limited
            # --------------------------------------------

            if response.status_code == 429:

                if attempt == max_retries - 1:
                    raise RuntimeError(
                        "OpenAlex rate limit exceeded after "
                        f"{max_retries} attempts."
                    )

                wait_seconds = 2 ** attempt

                await asyncio.sleep(
                    wait_seconds
                )

                continue

            # --------------------------------------------
            # Other API error
            # --------------------------------------------

            response.raise_for_status()

        else:
            raise RuntimeError(
                "OpenAlex request failed."
            )

    papers = []

    for work in data.get(
        "results",
        []
    ):

        authors = []

        for author in work.get(
            "authorships",
            []
        ):

            author_info = author.get(
                "author"
            )

            if author_info:
                authors.append(
                    author_info.get(
                        "display_name"
                    )
                )

        papers.append(
            {
                "id": work.get("id"),

                "title": work.get("title"),

                "year": work.get(
                    "publication_year"
                ),

                "doi": work.get("doi"),

                "authors": authors,

                "url": get_paper_url(
                    work
                ),

                "abstract": reconstruct_abstract(
                    work.get(
                        "abstract_inverted_index"
                    )
                )
            }
        )

    return papers


def get_paper_url(
    work
):

    location = work.get(
        "primary_location"
    )

    if location:
        return location.get(
            "landing_page_url"
        )

    return None


def reconstruct_abstract(
    inverted_index
):

    if not inverted_index:
        return None

    words = []

    for word, positions in (
        inverted_index.items()
    ):

        for position in positions:

            words.append(
                (
                    position,
                    word
                )
            )

    words.sort()

    return " ".join(
        word
        for _, word in words
    )