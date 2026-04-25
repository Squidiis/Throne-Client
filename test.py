from src.throne_api.client import ThroneClient
import asyncio

async def run_task():
    
    async with ThroneClient() as client:
        
        data = await client.get_wishlist("username")
        
        for link in data:
            print(link.link)

asyncio.run(run_task())