import os
from typing import Any

from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError, ServiceUnavailable


load_dotenv()


NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")


_driver = None


def is_configured() -> bool:
    return all(
        [
            NEO4J_URI,
            NEO4J_USERNAME,
            NEO4J_PASSWORD,
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

    if _driver is None:
        _driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(
                NEO4J_USERNAME,
                NEO4J_PASSWORD,
            ),
        )

    return _driver


def verify_connection() -> dict[str, Any]:
    driver = get_driver()

    try:
        driver.verify_connectivity()

        return {
            "connected": True,
            "database": NEO4J_DATABASE,
        }

    except ServiceUnavailable as exc:
        return {
            "connected": False,
            "database": NEO4J_DATABASE,
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
            database_=NEO4J_DATABASE,
        )

    return {
        "initialized": True,
        "database": NEO4J_DATABASE,
    }


def upsert_project(
    project_id: int,
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
        database_=NEO4J_DATABASE,
    )

    return records[0].data()


def upsert_paper(
    project_id: int,
    paper_id: int,
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
        database_=NEO4J_DATABASE,
    )

    return {
        "paper": records[0].data() if records else {
            "id": paper_id,
            "title": title,
        },
        "created": summary.counters.contains_updates,
    }


def add_theme(
    paper_id: int,
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
        database_=NEO4J_DATABASE,
    )

    return records[0].data() if records else None


def add_research_gap(
    project_id: int,
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
        database_=NEO4J_DATABASE,
    )

    return records[0].data() if records else None


def get_project_graph(project_id: int):
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
        database_=NEO4J_DATABASE,
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