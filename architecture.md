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