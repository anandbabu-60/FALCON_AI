# ResearchPilot AI — Member 3 AI/ML Documentation

## 1. Overview

Member 3 is responsible for the AI/ML layer of ResearchPilot AI.

The AI layer provides:

- Research paper analysis
- Research theme analysis
- Research gap analysis
- Research planning
- Multi-agent research workflow
- Retrieval-Augmented Generation (RAG)
- Evidence-grounded question answering
- Source and page citations
- Standalone AI APIs

---

## 2. AI Architecture

The AI pipeline follows this architecture:

User Research Question
        |
        v
Query Embedding
        |
        v
ChromaDB Vector Search
        |
        v
Relevant Research Evidence
        |
        v
RAG Context Builder
        |
        v
Gemini
        |
        v
Evidence-Grounded Answer
        |
        v
Citation Validation


The research workflow extends this architecture:

Research Topic
        |
        v
RAG Evidence Retrieval
        |
        v
Literature Agent
        |
        v
Analysis Agent
        |
        v
Gap Agent
        |
        v
Planning Agent
        |
        v
Final Research Plan

---

## 3. RAG Pipeline

The document pipeline is:

PDF
 |
 v
PDF Page Extraction
 |
 v
Text Chunking
 |
 v
Embedding Generation
 |
 v
ChromaDB Storage
 |
 v
Semantic Retrieval
 |
 v
Evidence Selection
 |
 v
Gemini Answer Generation

Each stored chunk contains research metadata including:

- source
- page

This metadata is used for citation generation.

---

## 4. Retrieval

The retriever converts the user's question into an embedding and performs vector similarity search against ChromaDB.

The retriever supports:

- top_k result selection
- similarity distance filtering
- source-specific filtering
- empty-query protection
- empty-result handling

Weakly related evidence can be discarded using the distance threshold.

---

## 5. Citation System

The RAG system numbers retrieved evidence:

[Evidence 1]
[Evidence 2]
[Evidence 3]

The Gemini prompt requires factual claims to be supported by evidence.

After generation, citation references are validated.

The system records:

- cited evidence IDs
- invalid evidence IDs
- source
- page
- retrieval distance

This prevents unsupported evidence identifiers from being silently accepted.

---

## 6. Multi-Agent Architecture

The ResearchManager orchestrates four agents:

### LiteratureAgent

Processes research papers and produces paper-level analysis and theme analysis.

### AnalysisAgent

Uses the research topic, paper analyses, theme analysis and retrieved evidence to identify research gaps.

### GapAgent

Uses identified research gaps and evidence to generate dataset and tool recommendations.

### PlanningAgent

Uses the research topic, gaps, datasets and tools to produce:

- methodology recommendations
- experiment plan
- research roadmap

The ResearchManager combines the results into a final research plan.

---

## 7. Gemini Integration

Gemini is used as the generative AI layer.

The integration supports:

- normal text generation
- structured JSON generation
- API error handling
- quota/rate-limit handling
- server error handling
- unexpected AI-service errors

Gemini quota errors are returned as HTTP 429 responses.

---

## 8. ChromaDB

ChromaDB is used as the vector database.

Research chunks are stored together with their embeddings and metadata.

The metadata allows the system to identify the original:

- research source
- page number

for retrieved evidence.

---

## 9. Standalone AI API

The standalone AI API exposes the AI functionality through:

POST /ai/ask

POST /ai/analyze-paper

POST /ai/analyze-themes

POST /ai/analyze-gaps

POST /ai/workflow

These endpoints allow the frontend or another service to consume the AI layer independently.

---

## 10. Testing

The AI layer contains automated tests using pytest.

Current test coverage includes:

### Retrieval Tests

3/3 passed.

Tests verify:

- retrieval returns results
- retrieval result structure
- top_k enforcement

### Citation Tests

3/3 passed.

Tests verify:

- RAG response structure
- citation validation structure
- citation source/page metadata

### Agent Tests

3/3 passed.

Tests verify:

- ResearchManager initialization
- agent initialization
- RAG evidence retrieval
- evidence structure

### AI API Tests

3/3 passed.

Tests verify:

- AI routes exist
- invalid requests return validation errors
- valid AI requests reach the AI layer

### Final Test Result

12/12 tests passed.

---

## 11. Technologies

The AI layer uses:

- Python
- FastAPI
- Gemini
- ChromaDB
- Sentence embeddings
- PyMuPDF
- SQLAlchemy
- pytest

---

## 12. Member 3 Contribution

Member 3 implemented the AI/ML functionality of ResearchPilot AI, including:

1. RAG document processing
2. PDF text extraction
3. Text chunking
4. Embedding generation
5. ChromaDB vector storage
6. Semantic retrieval
7. Source-specific retrieval
8. Evidence filtering
9. Evidence-grounded Gemini generation
10. Citation validation
11. Research paper analysis
12. Research theme analysis
13. Research gap analysis
14. Dataset recommendations
15. Tool recommendations
16. Methodology planning
17. Experiment planning
18. Research roadmap generation
19. Multi-agent research orchestration
20. Standalone AI APIs
21. Automated AI evaluation tests

---

## 13. Current Validation

The complete AI test suite currently passes:

12/12 tests.

Command:

python -m pytest .\app\tests -v

Result:

12 passed

This confirms that the current retrieval, citation, agent and standalone AI API test cases are functioning successfully.