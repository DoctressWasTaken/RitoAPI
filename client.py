import asyncio
import random
import aiohttp
import yaml
import logging

level = logging.INFO
handler = logging.StreamHandler()
handler.setLevel(level)
handler.setFormatter(logging.Formatter("%(asctime)s %(name)8s| %(message)s"))
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(level)

class Client:
    base_url = "http://%s.api.riotgames.com%s"

    def __init__(self):
        self.response_codes = {}
        with open('endpoints.yaml') as endpoints:
            data = yaml.load(endpoints)
        self.apis = data['apis']

    async def fetch(self, session, url, counter):
        async with session.get(
                url,
                proxy='http://127.0.0.1:8000',
                headers={'Count': str(counter)}) as response:
            resp = await response.text()
            # print(response.headers)
            return response.status

    async def worker(self):
        select_api = random.choice(list(self.apis.keys()))
        select_server = random.choice(self.apis[select_api]['allowed_server'])
        select_zone = random.choice(list(self.apis[select_api]['zones'].keys()))
        select_endpoint = self.apis[select_api]['zones'][select_zone][0]
        print("Worker selected %s on server %s to test." % (select_zone + select_endpoint, select_server))
        url = self.base_url % (select_server, select_zone + select_endpoint)
        async with aiohttp.ClientSession() as session:
            await self.fetch(session, url, 0)
            await asyncio.sleep(2)
            while True:
                responses = await asyncio.gather(*[asyncio.create_task(
                    self.fetch(session, url, r)
                ) for r in range(random.randint(25, 75))], asyncio.sleep(random.random()))
                for status in responses:
                    if not status:
                        continue
                    if status not in self.response_codes:
                        self.response_codes[status] = 0
                    self.response_codes[status] += 1

    async def printer(self):
        while True:
            await asyncio.sleep(1)
            logging.info(self.response_codes)

    async def main(self):
        await asyncio.gather(*[asyncio.create_task(
            self.worker()
        ) for r in range(10)], asyncio.create_task(self.printer()))


if __name__ == '__main__':
    c = Client()
    asyncio.run(c.main())
