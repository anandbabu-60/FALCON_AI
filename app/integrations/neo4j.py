from typing import Any

from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError, ServiceUnavailable

from app.core.config import get_settings


_driver = None


def is_configured() -> bool:
    settings = get_settings()
    return all(
        [
            settings.neo4j_uri,
            settings.neo4j_username,
            settings.neo4j_password,
        ]
    )


def get_driver():
    global _driver

    if not is_configured():
        raise RuntimeError(
            "Neo4j is not configured. "
            "Set NEO4J_URI, NEO4J_USERNAME and "
            "NEO4J_PASSWORD in the environment."
        )

    settings = get_settings()
    if _driver is None:
        _driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(
                settings.neo4j_username,
                settings.neo4j_password,
            ),
            # Neo4j is optional; an unavailable graph service must not block
            # project creation or the relational research workflow.
            connection_timeout=5.0,
            connection_acquisition_timeout=5.0,
            max_transaction_retry_time=5.0,
        )

    return _driver


def verify_connection() -> dict[str, Any]:
    driver = get_driver()

    try:
        driver.verify_connectivity()

        return {
            "connected": True,
            "database": get_settings().neo4j_database,
        }

    except ServiceUnavailable as exc:
        return {
            "connected": False,
            "database": get_settings().neo4j_database,
            "error": str(exc),
        }


def close_driver():
    global _driver

    if _driver is not None:
        _driver.close()
        _driver = None


def initialize_schema():
    driver = get_driver()

    queries = [
        """
        CREATE INDEX research_project_id IF NOT EXISTS
        FOR (p:ResearchProject)
        ON (p.id)
        """,
        """
        CREATE INDEX paper_id IF NOT EXISTS
        FOR (p:Paper)
        ON (p.id)
        """,
        """
        CREATE INDEX author_name IF NOT EXISTS
        FOR (a:Author)
        ON (a.name)
        """,
        """
        CREATE INDEX theme_name IF NOT EXISTS
        FOR (t:Theme)
        ON (t.name)
        """,
        """
        CREATE INDEX research_gap_title IF NOT EXISTS
        FOR (g:ResearchGap)
        ON (g.title)
        """,
    ]

    for query in queries:
        driver.execute_query(
            query,
            database_=get_settings().neo4j_database,
        )

    return {
        "initialized": True,
        "database": get_settings().neo4j_database,
    }


def upsert_project(
    project_id: str,
    title: str,
    description: str | None = None,
):
    driver = get_driver()

    records, summary, _ = driver.execute_query(
        """
        MERGE (p:ResearchProject {id: $project_id})
        SET
            p.title = $title,
            p.description = $description

        RETURN
            p.id AS id,
            p.title AS title,
            p.description AS description
        """,
        project_id=project_id,
        title=title,
        description=description,
        database_=get_settings().neo4j_database,
    )

    return records[0].data()


def upsert_paper(
    project_id: str,
    paper_id: str,
    title: str,
    authors: str | None = None,
    abstract: str | None = None,
):
    driver = get_driver()

    author_list = []

    if authors:
        author_list = [
            author.strip()
            for author in authors.split(",")
            if author.strip()
        ]

    records, summary, _ = driver.execute_query(
        """
        MERGE (project:ResearchProject {id: $project_id})

        MERGE (paper:Paper {id: $paper_id})
        SET
            paper.title = $title,
            paper.abstract = $abstract

        MERGE (project)-[:HAS_PAPER]->(paper)

        WITH paper

        UNWIND $authors AS author_name

        MERGE (author:Author {name: author_name})
        MERGE (paper)-[:AUTHORED_BY]->(author)

        RETURN
            paper.id AS id,
            paper.title AS title
        """,
        project_id=project_id,
        paper_id=paper_id,
        title=title,
        abstract=abstract,
        authors=author_list,
        database_=get_settings().neo4j_database,
    )

    return {
        "paper": records[0].data() if records else {
            "id": paper_id,
            "title": title,
        },
        "created": summary.counters.contains_updates,
    }


def add_theme(
    paper_id: str,
    theme: str,
):
    driver = get_driver()

    records, _, _ = driver.execute_query(
        """
        MATCH (paper:Paper {id: $paper_id})

        MERGE (theme:Theme {name: $theme})

        MERGE (paper)-[:HAS_THEME]->(theme)

        RETURN
            paper.id AS paper_id,
            theme.name AS theme
        """,
        paper_id=paper_id,
        theme=theme,
        database_=get_settings().neo4j_database,
    )

    return records[0].data() if records else None


def add_research_gap(
    project_id: str,
    gap_title: str,
):
    driver = get_driver()

    records, _, _ = driver.execute_query(
        """
        MATCH (project:ResearchProject {id: $project_id})

        MERGE (gap:ResearchGap {title: $gap_title})

        MERGE (project)-[:HAS_GAP]->(gap)

        RETURN
            project.id AS project_id,
            gap.title AS gap
        """,
        project_id=project_id,
        gap_title=gap_title,
        database_=get_settings().neo4j_database,
    )

    return records[0].data() if records else None


def get_project_graph(project_id: str):
    driver = get_driver()

    records, _, _ = driver.execute_query(
        """
        MATCH (project:ResearchProject {id: $project_id})

        OPTIONAL MATCH (project)-[:HAS_PAPER]->(paper:Paper)
        OPTIONAL MATCH (paper)-[:AUTHORED_BY]->(author:Author)
        OPTIONAL MATCH (paper)-[:HAS_THEME]->(theme:Theme)
        OPTIONAL MATCH (project)-[:HAS_GAP]->(gap:ResearchGap)

        RETURN
            project,
            collect(DISTINCT paper) AS papers,
            collect(DISTINCT author) AS authors,
            collect(DISTINCT theme) AS themes,
            collect(DISTINCT gap) AS gaps
        """,
        project_id=project_id,
        database_=get_settings().neo4j_database,
    )

    if not records:
        return None

    record = records[0]

    def node_to_dict(node):
        if node is None:
            return None

        return dict(node)

    return {
        "project": node_to_dict(record["project"]),
        "papers": [
            node_to_dict(node)
            for node in record["papers"]
            if node is not None
        ],
        "authors": [
            node_to_dict(node)
            for node in record["authors"]
            if node is not None
        ],
        "themes": [
            node_to_dict(node)
            for node in record["themes"]
            if node is not None
        ],
        "gaps": [
            node_to_dict(node)
            for node in record["gaps"]
            if node is not None
        ],
    }
