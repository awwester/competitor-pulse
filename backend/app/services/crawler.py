from dataclasses import dataclass, field
from types import TracebackType
from typing import Self

from playwright.async_api import Browser, Playwright, async_playwright

from app.config import settings
from app.services.diffing import normalize_text


@dataclass(frozen=True)
class PageFetch:
    url: str
    http_status: int | None
    text: str
    links: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return bool(self.text) and not (self.http_status and self.http_status >= 400)


class Crawler:
    """Renders pages in headless Chromium so JS-heavy pages are captured as users see them."""

    _playwright: Playwright
    _browser: Browser

    async def __aenter__(self) -> Self:
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self._browser.close()
        await self._playwright.stop()

    async def fetch(self, url: str) -> PageFetch:
        page = await self._browser.new_page()
        try:
            response = await page.goto(
                url, wait_until="networkidle", timeout=settings.crawl_timeout_ms
            )
            # Prefer <main> to skip nav/footer chrome; fall back to the whole body.
            main = page.locator("main").first
            target = main if await main.count() else page.locator("body")
            text = await target.inner_text()
            # The href property is already resolved against the page URL.
            links = await page.eval_on_selector_all("a[href]", "els => els.map(e => e.href)")
            return PageFetch(
                url=url,
                http_status=response.status if response else None,
                text=normalize_text(text),
                links=list(dict.fromkeys(link.split("#")[0] for link in links if link)),
            )
        finally:
            await page.close()
