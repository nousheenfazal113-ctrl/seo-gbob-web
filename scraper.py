# scraper.py
import aiohttp
import asyncio

async def fetch_html_async(url):
    """Single website ka HTML code asynchronously download karta hai."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        # Timeout set karte hain taake koi website freeze na kare
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers, allow_redirects=True) as response:
                if response.status == 200:
                    return await response.text()
                return None
    except Exception:
        return None

async def process_bulk_websites(domain_list, max_concurrent=5):
    """Ek sath bohot sari websites ko scan karne ke liye loop chalata hai."""
    connector = aiohttp.TCPConnector(limit_per_host=2)
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def worker(url):
        async with semaphore:
            return await fetch_html_async(url)
            
    tasks = [worker(url) for url in domain_list]
    return await asyncio.gather(*tasks)