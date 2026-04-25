# Throne Python SDK

A professional, asynchronous SDK for interacting with [Throne.com](https://throne.com) wishlists. This library uses a managed Playwright instance to provide a clean, high-level interface for accessing creator storefronts.

## Key Features

* **Context Manager Support:** Use ```async with``` for automatic browser lifecycle management.
* **Strongly Typed:** Returns ```WishlistItem``` objects instead of raw dictionaries.
* **Robust Error Handling:** Custom exceptions for ```404 Not Found```, ```429 Rate Limited```, and connection issues.
* **Anti-Bot Stealth:** Integrated bypasses for automation detection.
* **Last Item Shortcut:** Optimized method to fetch only the most recently added item.

## Installation

1. **Install the package:**
```
pip install throne-client
```

## Usage

### Using the Async Context Manager (Recommended)
This is the cleanest way to use the SDK, as it handles ```start()``` and ```stop()``` automatically.

```python
import asyncio
from throne_sdk import ThroneClient

async def main():
    async with ThroneClient() as client:
        try:
            wishlist = await client.get_wishlist("elaska")
            for item in wishlist:
                print(f"{item.name} - {item.price}")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Fetching the Newest Item
Perfect for "Recent Wishlist Item" widgets in stream overlays:

```python
async with ThroneClient() as client:
    item = await client.get_last_item("elaska")
    if item:
        print(f"Newest wish: {item.name}")
```

##  Data Structure: WishlistItem

The SDK returns objects with the following attributes:
* **name**: String (Product title)
* **price**: String (e.g., "$50.00" or "€20.00")
* **link**: String (Full Throne item URL)
* **image**: String (Image source URL)

## Disclaimer
This is an unofficial community project and is not affiliated with Throne.com. Please use it responsibly and respect the platform's terms of service.

**Built for the Creator Economy.**