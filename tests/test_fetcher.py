import asyncio
from collections.abc import Callable

import httpx
import pytest

from customer_service_agent.knowledge.fetcher import (
    DomainNotAllowedError,
    FetchError,
    FetchTooLargeError,
    SafeFetcher,
    UnsupportedSchemeError,
)

# Kieu cua mot "handler" MockTransport: nhan Request, tra Response.
Handler = Callable[[httpx.Request], httpx.Response]


def _make_fetcher(handler: Handler) -> SafeFetcher:
    """Tao SafeFetcher chay tren "server gia" trong bo nho (MockTransport).

    QUAN TRONG: client gia phai co CUNG cau hinh voi production
    (follow_redirects=True) - neu khong, test se khong phat hien duoc
    loi an toan chi xay ra khi redirect duoc theo.
    """
    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(transport=transport, follow_redirects=True)
    return SafeFetcher(client=client)


def test_fetch_returns_content_and_metadata() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            text="<h1>Hello Shopify</h1>",
            headers={"content-type": "text/html"},
        )

    fetcher = _make_fetcher(handler)
    result = asyncio.run(fetcher.fetch("https://help.shopify.com/manual"))

    assert result.content == "<h1>Hello Shopify</h1>"
    assert result.final_url == "https://help.shopify.com/manual"
    assert "text/html" in result.content_type


def test_rejects_non_https_url() -> None:
    # Handler khong bao gio duoc goi (URL bi chan truoc khi vao mang),
    # nhung kieu tra ve van phai la Response.
    fetcher = _make_fetcher(lambda request: httpx.Response(500))

    with pytest.raises(UnsupportedSchemeError):
        asyncio.run(fetcher.fetch("http://help.shopify.com/manual"))


def test_rejects_disallowed_domain() -> None:
    fetcher = _make_fetcher(lambda request: httpx.Response(500))

    with pytest.raises(DomainNotAllowedError):
        asyncio.run(fetcher.fetch("https://evil.example.com/page"))


def test_rejects_redirect_to_disallowed_domain() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        # URL dau: redirect sang domain xau; URL evil: tra 200 (dung lai).
        if "evil" in str(request.url):
            return httpx.Response(200, text="phish")
        return httpx.Response(302, headers={"location": "https://evil.example.com/phish"})

    fetcher = _make_fetcher(handler)

    with pytest.raises(DomainNotAllowedError):
        asyncio.run(fetcher.fetch("https://help.shopify.com/manual"))


def test_rejects_response_larger_than_limit() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="x" * 100)

    fetcher = _make_fetcher(handler)
    fetcher._max_bytes = 50  # noqa: SLF001

    with pytest.raises(FetchTooLargeError):
        asyncio.run(fetcher.fetch("https://help.shopify.com/manual"))


def test_retries_then_gives_up_on_persistent_5xx() -> None:
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        return httpx.Response(503, text="busy")

    fetcher = _make_fetcher(handler)
    fetcher._max_retries = 3  # noqa: SLF001
    fetcher._backoff = 0.01  # noqa: SLF001

    with pytest.raises(FetchError):
        asyncio.run(fetcher.fetch("https://help.shopify.com/manual"))

    assert calls["count"] == 3
