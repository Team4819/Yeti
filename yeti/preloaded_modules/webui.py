import yeti
import asyncio
from aiohttp import web

class WebUI(yeti.Module):

    def module_init(self):
        self.add_task(self.init_server())

    @asyncio.coroutine
    def handle(self, request):
        name = request.match_info.get('name', "Anonymous")
        text = "Hello, " + name
        return web.Response(body=text.encode("utf-8"))

    @asyncio.coroutine
    def init_server(self):
        app = web.Application()
        app.router.add_route('GET', "/{name}", self.handle)

        srv = yield from self.event_loop.create_server(app.make_handler(),
                                                       '127.0.0.1', 8080)
        print("Yeti WebUI started at  http://127.0.0.1:8080")
        return srv