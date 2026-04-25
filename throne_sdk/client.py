from typing import List, Optional
from playwright.async_api import async_playwright

from .models import WishlistItem
from .exceptions import (
    ThroneError, 
    WishlistNotFoundError, 
    ThroneConnectionError, 
    ThroneRateLimitError
)

class ThroneClient:
    """
    A professional SDK client for interacting with Throne.com wishlists.
    
    This client manages a headless browser instance to scrape public wishlist data.
    It supports use as an async context manager for safe resource management.
    """

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def __aenter__(self) -> 'ThroneClient':
        """Enables 'async with ThroneClient() as client' syntax."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Ensures the browser closes automatically when exiting the context."""
        await self.stop()

    async def start(self) -> 'ThroneClient':
        """
        Initializes the Playwright browser, context, and page.
        
        Returns:
            ThroneClient: The initialized client instance.
            
        Raises:
            ThroneConnectionError: If the browser fails to launch.
        """
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
            )
            self.context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                viewport={'width': 1280, 'height': 720}
            )
            
            # Anti-bot measure: Hide webdriver property
            await self.context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.page = await self.context.new_page()
            return self
        except Exception as e:
            raise ThroneConnectionError(f"Failed to initialize browser: {e}")

    async def stop(self):
        """
        Cleanly closes the browser and stops the Playwright engine.
        Should be called if not using the context manager.
        """
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def get_wishlist(self, username: str) -> List[WishlistItem]:
        """
        Fetches all currently visible items on a user's storefront.

        Args:
            username: The Throne username to fetch (e.g., 'elaska').

        Returns:
            A list of WishlistItem objects.

        Raises:
            WishlistNotFoundError: If the user doesn't exist (404).
            ThroneRateLimitError: If Throne is blocking requests (429).
            ThroneConnectionError: If the page fails to load or items don't appear.
        """
        if not self.page:
            await self.start()
            
        url = f"https://throne.com/{username}"
        
        try:
            response = await self.page.goto(url, wait_until="commit", timeout=60000)
            
            # Handle specific HTTP status codes
            if response and response.status == 404:
                raise WishlistNotFoundError(f"The user '{username}' was not found on Throne.")
            if response and response.status == 429:
                raise ThroneRateLimitError("Rate limit exceeded. Throne is blocking requests.")

            # Wait for the item container to appear
            await self.page.wait_for_selector('div#parent', timeout=15000)
            
        except (WishlistNotFoundError, ThroneRateLimitError):
            raise
        except Exception as e:
            raise ThroneConnectionError(f"Error loading wishlist for '{username}': {e}")
        
        # Extract data via JavaScript injection
        results = await self.page.evaluate("""
            () => {
                const cards = Array.from(document.querySelectorAll('div#parent, [class*="ItemCard"]'));
                const seenLinks = new Set();
                const data = [];

                cards.forEach(card => {
                    const linkElement = card.querySelector('a[href*="/item/"]');
                    if (!linkElement) return;
                    
                    const href = linkElement.getAttribute('href');
                    if (!href || seenLinks.has(href)) return;
                    seenLinks.add(href);

                    const name = card.querySelector('img')?.getAttribute('alt') || 
                                 card.querySelector('p')?.innerText || "Unknown";

                    const priceElement = Array.from(card.querySelectorAll('span, p, div'))
                                              .find(el => el.innerText.includes('€') || el.innerText.includes('$'));
                    
                    const img = card.querySelector('img')?.getAttribute('src');

                    data.push({
                        name: name.trim(),
                        price: priceElement ? priceElement.innerText.trim() : "0.00",
                        link: "https://throne.com" + href,
                        image: img
                    });
                });
                return data;
            }
        """)
        
        return [WishlistItem.from_raw_dict(item) for item in results]

    async def get_last_item(self, username: str) -> Optional[WishlistItem]:
        """
        Retrieves only the most recently added item from the wishlist.

        Args:
            username: The Throne username.

        Returns:
            The newest WishlistItem object, or None if the list is empty.
        """
        items = await self.get_wishlist(username=username)
        return items[0] if items else None