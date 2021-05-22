import traceback

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
            for key, value in self.endpoints.items():
                if server in value['allowed_server']:
                    for zone in value['zones']:
                        manager = LimitManager(name='X-Method-Rate-Limit', limits=settings.METHOD_RATE_LIMIT)
                        zne = web.Application(
                            middlewares=[manager.middleware]
                        )
                        zne.add_routes(
                            [
                                web.get('/{tail:.*}', self.default)
                            ]
                        )
                        svr.add_subapp(zone, zne)
            self.app.add_subapp("/%s" % server.lower(), svr)
        return self.app

    async def default(self, request):
        """Query handler for all endpoints."""
        try:
            return_code = 200
            if hasattr(request, 'return_value'):
                return_code = request.return_value
            return web.json_response(
                {"nice": "Nice."},
                status=return_code,
                headers=request.extra_headers | dict(request.headers),
            )
        except Exception as err:
            traceback.print_tb(err.__traceback__)
            print(err)


def main():
    p = Server()
    return p

async def start_gunicorn():
    """Return webserver element to gunicorn.

    Called by gunicorn directly.
    """
    p = Server()
    return await p.make_app()

if __name__ == "__main__":
    p = main()
    web.run_app(p.make_app(), port=8888)
