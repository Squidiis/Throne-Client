import re
from dataclasses import dataclass

@dataclass
class WishlistItem:
    id: str
    title: str
    price: float
    currency: str
    link: str
    image: str

    @classmethod
    def from_raw_dict(cls, data: dict):
        """Converts raw JS dictionary to a WishlistItem object."""
        
        price_str = data.get("price", "0.00")
        numeric_price = re.sub(r'[^\d.]', '', price_str.replace(',', '.'))
        
        currency = "EUR" if "€" in price_str else "USD" if "$" in price_str else "Unknown"
        
        return cls(
            id=data.get("link", "").split("/")[-1], # Extract ID from URL
            title=data.get("name", "Unknown"),
            price=float(numeric_price) if numeric_price else 0.0,
            currency=currency,
            link=data.get("link", ""),
            image=data.get("image", "")
        )