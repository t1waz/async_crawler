import time
import json
import asyncio
import aiohttp
from concurrent.futures import ProcessPoolExecutor


request_number = 1000

url = 'http://127.0.0.1:9000/add_link'

post_data = {
    "url": "https://www.google.pl/",
}


async def register_url(session=None, q=None):
    data = dict()
    try:
        async with q as q, session.post(url, data=json.dumps(post_data)) as response:
            data = await response.read()
            data = data.decode('utf-8')
            return (response.status, data)
    except Exception as e:
        print(e)
        return None


async def handle_register():
    tasks = []
    timeout = aiohttp.ClientTimeout(total=30)
    q = asyncio.Semaphore(10000)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        for _ in range(request_number):
            task = asyncio.ensure_future(register_url(session=session,
                                                      q=q))
            tasks.append(task)

        return await asyncio.gather(*tasks)


def test():
    start = time.time()
    loop = asyncio.get_event_loop()
    data = loop.run_until_complete(handle_register())
    print(data)
    print('it takes: ', (time.time() - start) * 1000)


if __name__ == "__main__":
    executor = ProcessPoolExecutor(10)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.ensure_future(loop.run_in_executor(executor, test))
