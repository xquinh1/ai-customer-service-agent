from customer_service_agent.db.base import Base


def _table_columns(table_name: str) -> set[str]:
    table = Base.metadata.tables[table_name]
    return set(table.columns.keys())


def test_documents_table_shape() -> None:
    assert _table_columns("documents") == {
        "id",
        "url",
        "title",
        "source",
        "category",
        "content_hash",
        "content",
        "created_at",
        "updated_at",
    }


def test_document_chunks_table_shape() -> None:
    assert _table_columns("document_chunks") == {
        "id",
        "document_id",
        "chunk_index",
        "title",
        "section",
        "content",
        "source_url",
        "metadata",
        "content_hash",
        "embedding",
        "embedding_model",
        "created_at",
    }


def test_document_url_is_unique() -> None:
    url_column = Base.metadata.tables["documents"].c.url
    assert url_column.unique is True
