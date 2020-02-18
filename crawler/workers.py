import asyncio
import aiohttp
import settings as settings
from links.managers import LinkDataManager


class UrlWorker:
    def __init__(self, input_queue, output_queue):
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.q = asyncio.Semaphore(1000)
        self.timeout = aiohttp.ClientTimeout(settings.URL_WORKER_SESSION_TIMEOUT)

    async def get_url_data(self, link, session, q):
        link_data = {
            'status_code': None,
            'data': None,
            'link': link
        }

        try:
            async with q as q, session.get(link.url) as response:
                link_data['status_code'] = response.status
                link_data['data'] = await response.read()
        except BaseException:
            pass

        await self.output_queue.put(link_data)

    async def get_urls_data(self):
        link = await self.input_queue.get()
        if link:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                tasks = [asyncio.ensure_future(self.get_url_data(link=link,
                                                                 session=session,
                                                                 q=self.q))]
                for _ in range(self.input_queue.qsize()):
                    link = await self.input_queue.get()
                    tasks.append(asyncio.ensure_future(self.get_url_data(link=link,
                                                                         session=session,
                                                                         q=self.q)))
                return await asyncio.gather(*tasks)

    async def start(self):
        while True:
            await self.get_urls_data()


class LinkDataWorker:
    def __init__(self, input_queue, output_queue):
        self.input_queue = input_queue
        self.output_queue = output_queue

    async def save_link_data(self):
        link_data = await self.input_queue.get()
        if link_data:
            instances = [await LinkDataManager.instance(**link_data)]
            while self.input_queue.qsize():
                link_data = await self.input_queue.get()
                instances.append(await LinkDataManager.instance(**link_data))

            await LinkDataManager.bulk_create(instances)

    async def start(self):
        while True:
            await self.save_link_data()
