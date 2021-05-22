import asyncio
import random
import traceback

from aiohttp.web import middleware

import settings
from ratelimiting import Limit, LimitBlocked


class Spacing:
    def __init__(self):
        print("Setting average extra wait time to %s" % settings.MAX_EXTRA_DELAY)

    @middleware
    async def middleware(self, request, handler):
        wait_time = random.random() * settings.MAX_EXTRA_DELAY
        await asyncio.sleep(wait_time / 2)
        try:
            response = await handler(request)
        except Exception as err:
            traceback.print_tb(err.__traceback__)
            print(err)
            raise err
        await asyncio.sleep(wait_time / 2)
        return response


class LimitManager:

    def __init__(self, name, limits):
        self.name = name
        self.limits = []
        for limit in limits.split(','):
            max_, duration = limit.split(':')
            self.limits.append(Limit(max_, duration))

    @middleware
    async def middleware(self, request, handler):
        return_value = None
        list_count = []
        list_max = []

        for limit in self.limits:
            try:
                max, count = await limit.requested()
                list_count.append(count)
                list_max.append(max)
            except LimitBlocked as err:
                return_value = 429
                max, count = err.header
                list_count.append(count)
                list_max.append(max)
        if return_value:
            request.return_value = return_value
        if not hasattr(request, 'extra_headers'):
            request.extra_headers = {}
        request.extra_headers |= {self.name: ",".join(list_max),
                                  "%s-Count" % self.name: ",".join(list_count)}

        return await handler(request)
