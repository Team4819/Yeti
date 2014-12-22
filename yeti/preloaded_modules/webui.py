import yeti
import asyncio
import os
from aiohttp import web

class WebUI(yeti.Module):

    def module_init(self):
        self.context = yeti.get_context()
        self.file_root = os.path.join(os.path.dirname(os.path.realpath(__file__)), "webui-resources")
        self.add_task(self.init_server())

    @asyncio.coroutine
    def data_handler(self, request):
        return web.Response(body="JSON!".encode("utf-8"))

    @asyncio.coroutine
    def init_server(self):
        app = web.Application()
        app.router.add_route("GET", "/json", self.data_handler)
        app.router.add_static("/", self.file_root)
        srv = yield from self.event_loop.create_server(app.make_handler(),
                                                       '127.0.0.1', 8080)
        print("Yeti WebUI started at  http://127.0.0.1:8080")
        return srv