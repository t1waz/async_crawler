import asyncio
import aiohttp
import settings as settings
from bs4 import BeautifulSoup
from links.managers import LinkDataManager


async def get_link_data(link):
    q = asyncio.Semaphore(1000)
    timeout = aiohttp.ClientTimeout(settings.TASK_SESSION_TIMEOUT)

    link_data = {
        'status_code': None,
        'data': None,
        'link': link
    }

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with q as q, session.get(link.url) as response:
                response_data = await response.read()
                link_data['status_code'] = response.status
                soup = BeautifulSoup(response_data, features="html.parser")
                link_data['data'] = response_data.decode(soup.original_encoding)
    except:
        pass

    await LinkDataManager.create(**link_data)
