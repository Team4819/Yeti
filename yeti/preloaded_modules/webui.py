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
                mod_data["status"] = "Loaded"
                data_structure["fallback"] = mod_object.loader.fallback_list
            data_structure["modules"].append(mod_data)
        text = json.dumps(data_structure, allow_nan=False)
        return web.Response(body=text.encode("utf-8"))

    @asyncio.coroutine
    def command_handler(self, request):
        commands = {"load": self.load_command, "unload": self.unload_command, "reload": self.reload_command}
        data = yield from request.post()
        commands[data["command"]](data["target"])

        #print(request.match_info['target'])
        return web.Response(body=":)".encode("utf-8"))

    def load_command(self, target):
        loader = yeti.ModuleLoader()
        loader.set_context(self.context)
        loader.load(target)

    def unload_command(self, target):
        self.context.unload_module(target)

    def reload_command(self, target):
        self.context.loaded_modules[target].call_hook("reload")

    @asyncio.coroutine
    def init_server(self):
        app = web.Application()
        app.router.add_route("GET", "/api/json", self.data_handler)
        app.router.add_route("POST", "/api/command", self.command_handler)
        app.router.add_static("/", self.file_root)
        self.srv = yield from self.event_loop.create_server(app.make_handler(),
                                                       '127.0.0.1', 8080)

        print("Yeti WebUI started at  http://127.0.0.1:8080")

    def module_deinit(self):
        self.srv.close()