import yaml
from aiohttp import web

import settings
from middleware import LimitManager, Spacing


class Server:

    def __init__(self):

        with open('endpoints.yaml', 'r') as endpoints:
            data = yaml.load(endpoints)
        self.server = data['server']
        self.endpoints = data['apis']

    async def make_app(self):
        self.app = web.Application(middlewares=[Spacing().middleware])

        for server in self.server:
            svr = web.Application(
                middlewares=[LimitManager(name='X-App-Rate-Limit', limits=settings.APP_RATE_LIMIT).middleware])
            for api in self.endpoints:
                if server in api['allowed_server']:

            self.app.add_route

        self.app.add_routes(
            [
                web.get("/{tail:.*}", self.default),
            ]
        )
        return self.app

    async def default(self, request):
        """Query handler for all endpoints."""
        return_code = 200
        if hasattr(request, 'return_value'):
            return_code = request.return_value

        return web.json_response(
            {"nice": "Nice."},
            status=return_code,
            headers=request.headers,
        )


def main(**kwargs):
    p = Server(**kwargs)
    return p


if __name__ == "__main__":
    p = main()
    web.run_app(p.make_app(), port=8888)
