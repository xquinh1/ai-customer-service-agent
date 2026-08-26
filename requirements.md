# Shopify AI Customer Support Agent

## 1. Project Overview

Build a production-oriented **AI Customer Support Agent** using Shopify's official public documentation as the primary knowledge source.

The project is designed as a flagship **AI Engineer / Applied AI / LLM Engineer** portfolio project.

The project must demonstrate practical understanding of:

* Python
* FastAPI
* LLM APIs
* Embeddings
* RAG
* Vector search
* Hybrid search
* Reranking
* Query rewriting
* Agentic workflows
* Tool calling
* Structured outputs
* Conversation memory
* Grounding
* Hallucination prevention
* Prompt injection defense
* AI evaluation
* AI observability
* Token/cost optimization

The developer is also using this project to **relearn Python through implementation**.

Therefore, avoid unnecessarily abstract Python frameworks and overly complex abstractions.

The implementation should prioritize learning the underlying concepts.

---

# 2. Primary Objective

Build an AI support agent capable of answering Shopify-related questions using Shopify's official documentation.

Example questions:

* How do I create a discount code?
* How do I refund an order?
* How can I change my store currency?
* How do I configure shipping?
* How do Shopify Payments work?
* How do I add a product?
* How do I manage customer accounts?
* How do I install an app?
* Why is my product not appearing?
* How do I configure taxes?

The system must prioritize factual accuracy and grounding.

If the knowledge base does not contain enough evidence, the agent must explicitly communicate uncertainty instead of hallucinating.

---

# 3. Official Knowledge Source

Primary source:

Shopify Help Center

https://help.shopify.com/

Use official Shopify documentation as the initial knowledge source.

Do not use random blogs, Reddit, Stack Overflow, or third-party tutorials as the primary knowledge base.

Every document must preserve its original source URL.

---

# 4. Technology Stack

## Backend

* Python 3.12+
* FastAPI
* Pydantic
* Uvicorn

## AI

* OpenAI API
* OpenAI Python SDK
* Embeddings
* Chat/LLM models
* Tool/function calling
* Structured outputs

The application must not be tightly coupled to one specific model.

Model configuration should be controlled through environment variables.

---

# 5. Database

Use:

* PostgreSQL
* pgvector

Use PostgreSQL for:

* application data
* conversations
* messages
* documents
* chunks
* embeddings
* evaluation results

Do not introduce a dedicated vector database initially.

The reason for using pgvector must be documented in the README.

---

# 6. Validation

Use:

* Pydantic
* Pydantic Settings

Use Pydantic for:

* API request validation
* API response schemas
* configuration
* tool arguments
* LLM structured outputs
* internal domain models where appropriate

Never blindly trust LLM-generated structured data.

---

# 7. Frontend

Use:

* Next.js
* TypeScript

The frontend is only a demonstration interface.

Prioritize:

* chat
* streaming responses
* citations
* conversation history
* tool activity where useful

Do not spend significant development time on visual polish.

---

# 8. Streaming

Use:

* Server-Sent Events (SSE)

The backend should stream AI responses to the frontend.

Possible event types:

```text
response_start
token
citation
tool_start
tool_result
response_complete
error
```

Create a reusable SSE implementation.

Do not scatter raw streaming logic throughout route handlers.

---

# 9. High-Level Architecture

```text
                         Shopify Official Docs
                                  │
                                  ▼
                         Knowledge Ingestion
                                  │
                    ┌─────────────▼─────────────┐
                    │    Document Processing    │
                    │                            │
                    │ Fetch → Parse → Clean      │
                    │ Chunk → Metadata           │
                    └─────────────┬─────────────┘
                                  │
                              Embeddings
                                  │
                                  ▼
                         PostgreSQL + pgvector
                                  │
                                  │
User ──► FastAPI ──► AI Orchestrator
                         │
              ┌──────────┼───────────┐
              │          │           │
              ▼          ▼           ▼
           Intent      RAG         Tools
           Router     Pipeline     Calling
                         │
                ┌────────▼────────┐
                │ Query Rewriting │
                │ Hybrid Search   │
                │ Reranking       │
                └────────┬────────┘
                         │
                         ▼
                  Context Builder
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
       Conversation Memory     Tool Results
              │                     │
              └──────────┬──────────┘
                         ▼
                   LLM Generation
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
        Grounding Check        Citations
              │                     │
              └──────────┬──────────┘
                         ▼
                    SSE Response
                         │
                         ▼
                        User
```

---

# 10. Python Learning Requirement

This project is also a Python learning project.

The developer should learn Python concepts naturally while implementing each feature.

Important concepts to practice:

## Python Fundamentals

* variables
* strings
* lists
* dictionaries
* tuples
* sets
* comprehensions
* functions
* arguments
* exceptions
* modules
* packages

## Object-Oriented Programming

* classes
* inheritance
* composition
* dataclasses
* properties
* abstract base classes
* protocols/interfaces where useful

## Type System

Use Python type hints extensively.

Learn:

* `str`
* `int`
* `float`
* `bool`
* `list`
* `dict`
* `Optional`
* `Union`
* `Literal`
* `TypedDict`
* `Protocol`
* generics
* type aliases

Prefer modern Python syntax.

---

# 11. Async Python

Because the system performs:

* HTTP requests
* LLM requests
* database queries
* streaming
* concurrent operations

learn and use:

* `async`
* `await`
* `asyncio`
* async context managers
* async generators

Understand why asynchronous execution is useful instead of blindly using it.

---

# 12. Python Project Structure

Start with a modular monolith.

Suggested structure:

```text
app/

    main.py

    api/
        routes/
        dependencies/

    core/
        config.py
        logging.py
        exceptions.py

    modules/

        ai/
            orchestrator.py
            llm_service.py
            prompts.py
            structured_output.py

        rag/
            retrieval.py
            embeddings.py
            reranking.py
            query_rewriter.py
            context_builder.py

        knowledge/
            crawler.py
            parser.py
            cleaner.py
            chunker.py
            ingestion.py

        conversations/
            service.py
            repository.py

        tools/
            registry.py
            base.py
            order.py
            refund.py
            customer.py

        evaluation/
            evaluator.py
            metrics.py
            dataset.py

    db/
        connection.py
        models.py
        repositories/

    schemas/
        conversations.py
        messages.py
        ai.py

tests/
```

Do not create every directory immediately.

Introduce modules as the corresponding features are implemented.

---

# 13. FastAPI Architecture

Keep route handlers thin.

Example:

```text
Route
  ↓
Service
  ↓
AI Orchestrator
  ↓
RAG / Tool / LLM Services
  ↓
Repository
  ↓
Database
```

Do not place:

* retrieval logic
* prompts
* database queries
* LLM calls
* tool execution

directly inside route handlers.

---

# 14. Knowledge Ingestion Pipeline

Implement:

```text
Shopify URL
    ↓
Async HTTP Fetcher
    ↓
HTML Parser
    ↓
Content Cleaner
    ↓
Metadata Extraction
    ↓
Structure-Aware Chunking
    ↓
Embedding
    ↓
PostgreSQL + pgvector
```

The pipeline must be:

* repeatable
* idempotent
* observable

---

# 15. Web Fetcher

Implement a safe asynchronous fetcher.

Requirements:

* HTTPS only
* URL validation
* domain allowlist
* SSRF protection
* timeout
* response size limit
* content-type validation
* redirect handling
* retry transient failures
* reasonable crawling rate

The initial crawler should only access Shopify documentation.

Do not expose arbitrary URL fetching to end users.

---

# 16. HTML Parsing

Extract useful documentation content.

Remove:

* navigation
* footer
* scripts
* styles
* advertisements
* irrelevant UI
* duplicate content

Preserve:

* title
* headings
* paragraphs
* lists
* tables where possible
* links
* document hierarchy

Use a dedicated parser/cleaner module.

---

# 17. Document Model

Each document should contain:

```text
id
title
url
source
category
content_hash
content
created_at
updated_at
```

Content hash is required for detecting changes.

If the source content has not changed:

* do not reprocess unnecessarily
* do not regenerate embeddings unnecessarily

---

# 18. Chunking

Implement structure-aware chunking.

Avoid blindly splitting text every N characters.

Prefer boundaries such as:

* headings
* sections
* paragraphs
* lists
* related instructions

Each chunk should contain:

```text
id
document_id
content
chunk_index
title
section
source_url
metadata
embedding
```

Experiment with chunking strategies later and evaluate their impact.

---

# 19. Embeddings

Generate embeddings for chunks.

Requirements:

* configurable embedding model
* content hashing
* embedding caching
* model metadata
* batch processing where appropriate

Store:

```text
embedding_model
embedding_dimension
content_hash
```

---

# 20. Baseline RAG

Build the simplest correct RAG pipeline first.

```text
Question
   ↓
Embedding
   ↓
Vector Search
   ↓
Top K Chunks
   ↓
Context
   ↓
LLM
   ↓
Answer + Citation
```

Do not implement hybrid search, reranking, or agents before the baseline works.

The baseline becomes the evaluation reference point.

---

# 21. Hybrid Retrieval

After baseline RAG works, implement:

### Semantic Search

pgvector similarity search.

### Lexical Search

PostgreSQL full-text search.

Then combine results.

Example:

```text
                Query
                  │
          ┌───────┴────────┐
          ▼                ▼
    Vector Search      Keyword Search
          │                │
          └───────┬────────┘
                  ▼
                Fusion
                  │
                  ▼
             Candidates
```

The ranking/fusion algorithm must be explicit and documented.

---

# 22. Query Rewriting

Implement query rewriting for ambiguous conversational questions.

Example:

```text
User:
How do I create a discount?

Assistant:
...

User:
Can it expire tomorrow?
```

Retrieval query:

```text
How can I configure a Shopify discount code with an expiration date?
```

The rewritten query should be generated from relevant conversation context.

Do not send unlimited conversation history to the model.

---

# 23. Reranking

Implement a reranking stage after candidate retrieval.

Input:

```text
query
candidate_chunks
```

Output:

```text
chunk
relevance_score
```

Only the highest-quality chunks should be passed to the generation model.

Keep reranking independent from retrieval.

---

# 24. Context Builder

Create a dedicated context builder.

Responsibilities:

* select relevant chunks
* remove duplicates
* enforce token/context limits
* preserve metadata
* preserve citation information
* format context consistently

Do not blindly send all retrieved chunks to the LLM.

---

# 25. Grounded Generation

The LLM must generate answers based on:

* user question
* conversation context
* retrieved Shopify documentation
* tool results when available

The model must not fabricate Shopify functionality.

When evidence is insufficient:

```text
I couldn't find enough information in the available Shopify documentation to answer that confidently.
```

The system should prefer refusal/uncertainty over hallucination.

---

# 26. Citation System

Every documentation-grounded answer should preserve source metadata.

Example:

```json
{
  "answer": "You can create a discount...",
  "citations": [
    {
      "document_id": "...",
      "chunk_id": "...",
      "title": "Creating discount codes",
      "url": "https://help.shopify.com/..."
    }
  ]
}
```

Citation URLs must come from the stored source documents.

Never fabricate URLs.

---

# 27. Intent Classification

Initially support:

* orders
* products
* payments
* discounts
* shipping
* taxes
* customers
* apps
* store settings
* billing
* troubleshooting
* general

Intent classification can influence:

* retrieval filters
* query rewriting
* tool selection

Do not over-engineer routing before baseline RAG works.

---

# 28. Agent Architecture

After RAG is stable, introduce agentic behavior.

The agent should decide whether a question requires:

```text
RAG
Tool
RAG + Tool
Clarification
Refusal
```

Example:

```text
"How do I create a discount?"
        ↓
       RAG

"What is the status of order #1234?"
        ↓
      Tool

"How do I refund order #1234?"
        ↓
RAG + Tool
```

Do not use an agent framework initially.

Implement the workflow manually using Python functions and explicit state.

Only introduce LangGraph or another framework later if it solves a demonstrated complexity problem.

---

# 29. Tool Calling

Create a tool registry.

Potential tools:

```text
search_shopify_docs()
get_order()
get_refund_status()
get_customer()
```

Business tools must connect to real Shopify APIs when implemented.

Do not simulate business data.

Business tools require:

* authentication
* authorization
* store context
* validated arguments

Destructive actions must require explicit confirmation.

---

# 30. Structured Outputs

Use structured outputs for:

* intent classification
* routing decisions
* tool arguments
* evaluation results
* final response metadata

Example:

```json
{
  "intent": "orders",
  "action": "search",
  "needs_retrieval": true,
  "needs_tool": false
}
```

Validate model output with Pydantic.

Never trust raw model-generated JSON.

---

# 31. Conversation Memory

Persist:

```text
users
conversations
messages
citations
```

Message fields:

```text
id
conversation_id
role
content
status
created_at
token_usage
latency
```

Support multi-turn context.

Do not send unlimited history to the LLM.

Implement a context management strategy.

---

# 32. SSE Streaming

Create an SSE endpoint for AI responses.

Example:

```text
GET /api/messages/{message_id}/stream
```

Events:

```text
response_start
token
citation
tool_start
tool_result
response_complete
error
```

Use async generators where appropriate.

This is also an opportunity to learn asynchronous Python.

---

# 33. Hallucination Prevention

Implement multiple layers:

1. Retrieval relevance threshold
2. Context filtering
3. Grounded generation prompt
4. Citation requirement
5. Post-generation grounding validation
6. Evaluation dataset

Measure hallucination rate rather than assuming the system is grounded.

---

# 34. Prompt Injection Defense

Treat:

* user input
* retrieved documents
* tool results

as untrusted data.

Retrieved documentation must never override system instructions.

Protect against attempts to:

* reveal system prompts
* reveal secrets
* bypass grounding
* fabricate citations
* execute unauthorized tools

---

# 35. Evaluation Dataset

Create at least 50 evaluation questions.

Categories:

* factual
* multi-step
* ambiguous
* multi-turn
* no-answer
* adversarial
* prompt injection

Each case:

```text
question
category
difficulty
expected_sources
expected_answer_characteristics
```

---

# 36. Evaluation Metrics

## Retrieval

Measure:

* Recall@K
* Precision@K
* MRR where useful

## Generation

Measure:

* answer relevance
* groundedness
* citation correctness
* hallucination rate

## System

Measure:

* latency
* token usage
* estimated cost
* error rate

Compare:

```text
Baseline Vector RAG
        ↓
Hybrid Search
        ↓
Query Rewriting
        ↓
Reranking
```

Each improvement must be evaluated.

Do not add complexity simply because it is popular.

---

# 37. AI Observability

Track:

```text
request_id
conversation_id
message_id
model
latency
retrieval_latency
reranking_latency
retrieved_chunks
input_tokens
output_tokens
total_tokens
estimated_cost
errors
```

Use structured Python logging.

Avoid logging sensitive information unnecessarily.

---

# 38. Cost Optimization

Implement:

* embedding caching
* content hashing
* batch embeddings
* context limits
* history limits
* model selection by task
* retrieval result limits
* optional response caching

Use cheap models for:

* classification
* routing
* query rewriting

Use stronger models for final responses when needed.

---

# 39. Reliability

Handle:

* LLM timeouts
* rate limits
* embedding failures
* database failures
* crawler failures
* retrieval failures
* malformed documents
* SSE disconnects
* tool failures

Use:

* timeouts
* bounded retries
* exponential backoff
* graceful failures
* typed exceptions

Do not retry non-retryable errors.

---

# 40. Database Schema

Initial tables:

```text
users
conversations
messages
citations
documents
document_chunks
ingestion_jobs
ai_usage
evaluation_runs
evaluation_results
```

Use PostgreSQL migrations.

Use indexes for:

* conversation ownership
* message lookup
* document URL
* content hash
* chunk document ID
* vector search

---

# 41. API

Initial endpoints:

```text
POST   /api/conversations
GET    /api/conversations
GET    /api/conversations/{id}
DELETE /api/conversations/{id}

POST   /api/conversations/{id}/messages
GET    /api/messages/{id}/stream

POST   /api/knowledge/ingest
GET    /api/knowledge/documents

GET    /api/health
GET    /api/metrics
```

Use Pydantic request/response schemas.

---

# 42. Testing

Use pytest.

Test:

### Unit tests

* chunking
* parsing
* query rewriting
* retrieval ranking
* context construction
* tool validation
* citation extraction

### Integration tests

* PostgreSQL
* pgvector
* ingestion pipeline
* RAG pipeline
* API

### AI evaluation tests

* retrieval quality
* groundedness
* citation correctness
* hallucination cases
* prompt injection cases

Do not depend entirely on live LLM calls for unit tests.

Mock external AI calls where appropriate.

---

# 43. Development Phases

## Phase 1 — Python + Backend Foundation

Learn and implement:

* Python fundamentals
* type hints
* classes
* modules
* exceptions
* async/await
* FastAPI
* Pydantic
* PostgreSQL
* pytest

Build:

* FastAPI project
* configuration
* database connection
* migrations
* health endpoint
* error handling
* logging

---

## Phase 2 — Shopify Knowledge Ingestion

Learn and implement:

* async HTTP
* HTML parsing
* text processing
* hashing
* chunking
* embeddings
* pgvector

Build:

```text
Shopify Docs
    ↓
Crawler
    ↓
Parser
    ↓
Cleaner
    ↓
Chunker
    ↓
Embedding
    ↓
PostgreSQL
```

---

## Phase 3 — Baseline RAG

Learn:

* embeddings
* cosine similarity
* vector search
* context construction
* prompt design
* grounded generation

Build the simplest working RAG system.

---

## Phase 4 — Retrieval Engineering

Learn:

* lexical search
* semantic search
* hybrid retrieval
* ranking
* reranking
* query rewriting

Evaluate each improvement.

---

## Phase 5 — Agent

Learn:

* tool calling
* structured outputs
* agent state
* routing
* tool selection
* failure handling

Build explicit agent workflows before introducing an agent framework.

---

## Phase 6 — AI Evaluation

Learn:

* evaluation dataset design
* retrieval metrics
* groundedness
* hallucination measurement
* regression testing

Build automated evaluation.

---

## Phase 7 — Production AI

Implement:

* SSE
* tracing
* token/cost tracking
* caching
* rate limiting
* retries
* prompt injection defense
* Docker
* deployment

---

# 44. Python Learning Rules

While implementing the project:

* Prefer standard Python before third-party abstractions
* Understand `async`/`await`
* Understand generators and async generators
* Understand decorators when FastAPI introduces them
* Understand Pydantic instead of treating it as magic
* Understand dependency injection in FastAPI
* Understand context managers
* Understand Python typing
* Understand exceptions
* Understand package/module organization

Do not blindly copy Python patterns without understanding them.

When a new Python concept is introduced, explain why it is being used and what problem it solves.

---

# 45. Framework Rules

Do NOT start with:

* LangChain
* LangGraph
* LlamaIndex
* complex agent frameworks

First implement:

```text
LLM API
RAG
Retrieval
Tool Calling
Agent Routing
Evaluation
```

using lightweight Python code.

Frameworks may be introduced later if they solve a concrete problem.

The portfolio should demonstrate understanding of AI system fundamentals rather than framework dependency.

---

# 46. Engineering Principles

Prioritize:

1. AI correctness
2. Retrieval quality
3. Grounded generation
4. Evaluation
5. Agent reliability
6. Cost efficiency
7. Observability
8. Maintainability
9. Performance

Avoid unnecessary complexity.

Do not introduce:

* microservices
* Kubernetes
* multiple vector databases
* complex distributed systems

unless there is a demonstrated requirement.

Use a modular monolith initially.

---

# 47. Definition of Done

The project is complete when:

* Shopify documentation can be ingested
* Documents are cleaned and chunked
* Embeddings are stored in pgvector
* Baseline vector RAG works
* Hybrid retrieval works
* Query rewriting works
* Reranking works
* Answers are grounded
* Citations are accurate
* Unsupported questions are handled safely
* Multi-turn conversations work
* Tool calling works with authenticated tools
* Structured outputs are validated
* SSE streaming works
* Prompt injection defenses exist
* Evaluation dataset exists
* Retrieval metrics are measurable
* Generation quality is measurable
* AI latency is observable
* Token usage is tracked
* AI cost is estimated
* Tests cover critical functionality
* Docker setup works
* README explains architecture and trade-offs

---

# 48. Portfolio Objective

The final project should demonstrate:

```text
Python
   +
FastAPI
   +
LLM APIs
   +
Embeddings
   +
RAG
   +
Vector Search
   +
Hybrid Retrieval
   +
Reranking
   +
Query Rewriting
   +
Agent / Tool Calling
   +
Structured Outputs
   +
Conversation Memory
   +
Grounding
   +
Hallucination Prevention
   +
Prompt Injection Defense
   +
AI Evaluation
   +
AI Observability
   +
Cost Optimization
```

The project should be presented as an **AI Customer Support Agent**, not simply as a chatbot.

The primary portfolio value should come from demonstrating the ability to design, implement, evaluate, debug, and improve an AI system.

---

# 49. Instructions for Codex

Before implementing anything:

1. Inspect the repository.
2. Read this `requirements.md`.
3. Understand the current project state.
4. Do not rewrite existing code unnecessarily.
5. Propose a small implementation plan before major changes.
6. Implement incrementally.
7. Explain important Python concepts when they appear.
8. Prefer simple Python implementations before introducing abstractions.
9. Keep AI components modular.
10. Add tests for important functionality.
11. Do not add libraries without a clear reason.
12. Do not introduce LangChain/LangGraph unless explicitly requested or a concrete complexity justifies it.
13. Do not implement future phases prematurely.

The implementation process should follow:

```text
Understand
    ↓
Design
    ↓
Implement
    ↓
Test
    ↓
Evaluate
    ↓
Improve
```

Always prioritize learning the underlying AI engineering concepts over rapidly producing code.
