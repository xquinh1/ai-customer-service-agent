"""Safe async HTTP fetcher for the Shopify documentation crawler.

Only fetches HTTPS URLs whose host is in ALLOWED_HOSTS. This protects
against SSRF (Server-Side Request Forgery): if an attacker could make us
fetch any URL, they could probe internal services (localhost, cloud
metadata endpoints) through our server.
"""

import asyncio
from dataclasses import dataclass
from urllib.parse import urlsplit

import httpx

from customer_service_agent.core.exceptions import AppError

# Chi fetch cac domain chinh thuc cua Shopify docs.
ALLOWED_HOSTS = frozenset({"help.shopify.com", "shopify.dev", "www.shopify.com"})

# Gioi han tai ve: 2MB van du cho 1 trang documentation.
MAX_RESPONSE_BYTES = 2 * 1024 * 1024


class FetchError(AppError):
    """Base class for all fetch failures."""


class UnsupportedSchemeError(FetchError):
    """Raised when the URL is not HTTPS."""


class DomainNotAllowedError(FetchError):
    """Raised when the URL host is not in the allowlist."""


class FetchTooLargeError(FetchError):
    """Raised when the response exceeds the size limit."""


class _ServerError(FetchError):
    """Internal: a 5xx response, which is retryable."""


@dataclass(frozen=True)
class FetchResult:
    """What the fetcher returns: content plus enough metadata to cite it."""

    url: str
    final_url: str
    content_type: str
    content: str


def _validate_url(url: str) -> str:
    """Check the URL is HTTPS and its host is allowed. Returns the host."""
    parsed = urlsplit(url)

    if parsed.scheme != "https":
        raise UnsupportedSchemeError(f"Only HTTPS is allowed, got: {url}")

    host = parsed.hostname or ""
    if host not in ALLOWED_HOSTS:
        raise DomainNotAllowedError(f"Host not allowed: {host}")

    return host


class SafeFetcher:
    """Fetches pages from allowed Shopify domains with limits and retries."""

    def __init__(
        self,
        timeout_seconds: float = 10.0,
        max_bytes: int = MAX_RESPONSE_BYTES,
        max_retries: int = 3,
        backoff_seconds: float = 0.5,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._timeout = timeout_seconds
        self._max_bytes = max_bytes
        self._max_retries = max_retries
        self._backoff = backoff_seconds
        # Dependency injection: tests truyen client gia (MockTransport);
        # production khong truyen gi -> tu tao client that.
        self._client = client

    async def fetch(self, url: str) -> FetchResult:
        """Download ``url``, enforcing scheme, domain, size and timeout limits.

        Transient failures (timeouts, 5xx) are retried with exponential
        backoff. Permanent errors (bad domain, bad scheme, 4xx) fail fast.
        """
        _validate_url(url)

        attempts = 0
        while True:
            attempts += 1
            try:
                return await self._fetch_once(url)
            except (httpx.TransportError, _ServerError) as error:
                if attempts >= self._max_retries:
                    raise FetchError(f"Fetch failed after {attempts} attempts: {url}") from error
                await asyncio.sleep(self._backoff * 2 ** (attempts - 1))

    async def _fetch_once(self, url: str) -> FetchResult:
        if self._client is not None:
            response = await self._client.get(url)
        else:
            async with httpx.AsyncClient(
                follow_redirects=True,
                timeout=self._timeout,
            ) as client:
                response = await client.get(url)

        if response.status_code >= 500:
            raise _ServerError(f"Server error {response.status_code}: {url}")

        # Redirect co the dua ta sang domain khong duoc phep -> kiem tra lai.
        _validate_url(str(response.url))

        content = response.text
        if len(content.encode("utf-8")) > self._max_bytes:
            raise FetchTooLargeError(f"Response exceeds {self._max_bytes} bytes: {url}")

        return FetchResult(
            url=url,
            final_url=str(response.url),
            content_type=response.headers.get("content-type", ""),
            content=content,
        )
