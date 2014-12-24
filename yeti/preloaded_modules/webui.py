import yeti
import asyncio
import os
import json
from aiohttp import web

class WebUI(yeti.Module):
    """
    A pre-loaded module that provides an elegant interface with which to manage loaded modules.
    """

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
            mod_data["description"] = mod_object.__doc__
            if hasattr(mod_object, "loader"):
                mod_data["filename"] = mod_object.loader.module_path
                mod_data["status"] = "Loaded"
                mod_data["fallbacks"] = mod_object.loader.fallback_list
            data_structure["modules"].append(mod_data)
        text = json.dumps(data_structure, allow_nan=False)
        return web.Response(body=text.encode("utf-8"))

    @asyncio.coroutine
    def command_handler(self, request):
        commands = {"load": self.load_command, "unload": self.unload_command, "reload": self.reload_command}
        data = yield from request.post()
        try:
            msg = yield from commands[data["command"]](data["target"])
            res = {"status": 0, "message": msg}
        except Exception as e:
            res = {"status": -1, "message": str(e)}
            self.logger.error(str(e))

        text = json.dumps(res, allow_nan=False)
        return web.Response(body=text.encode("utf-8"))

    @asyncio.coroutine
    def load_command(self, target):
        loader = yeti.ModuleLoader()
        loader.set_context(self.context)
        yield from loader.load_coroutine(target)
        return "Successfully loaded " + target

    @asyncio.coroutine
    def unload_command(self, target):
        yield from self.context.unload_module_coroutine(target)
        return "Successfully unloaded " + target

    @asyncio.coroutine
    def reload_command(self, target):
        if target == "all":
            self.context.call_hook("reload")
        else:
            self.context.loaded_modules[target].call_hook("reload")
        return "Successfully reloaded " + target

    @asyncio.coroutine
    def init_server(self):
        app = web.Application()
        app.router.add_route("GET", "/api/json", self.data_handler)
        app.router.add_route("POST", "/api/command", self.command_handler)
        app.router.add_static("/", self.file_root)
        self.srv = yield from self.event_loop.create_server(app.make_handler(), port=8080)

        self.logger.info("Yeti WebUI started at  http://127.0.0.1:8080/index.html")

    def module_deinit(self):
        self.srv.close()