import asyncio
import aiohttp


async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get(
                'http://euw1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/AAAAA',
        proxy='http://127.0.0.1:8000') as response:
            resp = await response.text()
            print(resp)

if __name__ == '__main__':
    asyncio.run(main())
