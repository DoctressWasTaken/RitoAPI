import asyncio
import random

from aiohttp.web import middleware

import settings
from ratelimiting import Limit, LimitBlocked


class Spacing:

    @middleware
    async def middleware(self, request, handler):
        await asyncio.sleep(random.random() * settings.MAX_EXTRA_DELAY / 2)
        handler(request)
        await asyncio.sleep(random.random() * settings.MAX_EXTRA_DELAY / 2)


class LimitManager:
    limits = list()

    def __init__(self, name, limits):
        self.name = name
        for limit in limits.split(','):
            self.limits.append(Limit(name, *limit.split(':')))

    @middleware
    async def middleware(self, request, handler):
        return_value = None
        list_count = []
        list_max = []

        for limit in self.limits:
            try:
                max, count = limit.requested()
                list_count += count
                list_max += max
            except LimitBlocked as err:
                return_value = 429
                max, count = err.header
                list_count += count
                list_max += max
        if return_value:
            request.return_value = return_value
        if not hasattr(request, 'header'):
            request.header = {}
        request.header |= {self.name: ",".join(list_max),
                           "%s-Count" % self.name: ",".join(list_count)}
        return handler(request)
