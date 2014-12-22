import yeti
import asyncio
import os
import json
from aiohttp import web

class WebUI(yeti.Module):

    def module_init(self):
        self.context = yeti.get_context()
        self.file_root = os.path.join(os.path.dirname(os.path.realpath(__file__)), "webui-resources")
        self.add_task(self.init_server())

    @asyncio.coroutine
    def data_handler(self, request):
        data_structure = dict()
        data_structure["modules"] = list()
        for modname in self.context.loaded_modules:
            mod_object = self.context.loaded_modules[modname]
            mod_data = dict()
            mod_data["subsystem"] = modname
            if hasattr(mod_object, "loader"):
                mod_data["filename"] = mod_object.loader.module_path
            data_structure["modules"].append(mod_data)
        text = json.dumps(data_structure, allow_nan=False)
        return web.Response(body=text.encode("utf-8"))

    @asyncio.coroutine
    def init_server(self):
        app = web.Application()
        app.router.add_route("GET", "/json", self.data_handler)
        app.router.add_static("/", self.file_root)
        srv = yield from self.event_loop.create_server(app.make_handler(),
                                                       '127.0.0.1', 8080)
        print("Yeti WebUI started at  http://127.0.0.1:8080")
        return srv