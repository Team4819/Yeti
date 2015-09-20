import yeti
import time
import asyncio
import os
import json
import traceback
import logging
from aiohttp import web

try:
    from yeti.version import __version__
except:
    __version__ = "master"

class WebUILoggerHandler(logging.Handler):

    def __init__(self, handler_func):
        self.handler_func = handler_func
        super().__init__()

    def emit(self, record):
        self.handler_func(record)

class WebUI(yeti.Module):
    """
    A pre-loaded module that provides an elegant interface with which to manage loaded modules.
    """

    def module_init(self):
        logging.getLogger("aiohttp.access").setLevel(logging.WARNING)
        self.file_root = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources")
        self.start_coroutine(self.init_server())
        self.yeti_logger = logging.getLogger("yeti")
        def er_hdl(msg):
            self.engine.thread_coroutine(self.error_handler(msg))
        logger_handler = WebUILoggerHandler(er_hdl)
        self.yeti_logger.addHandler(logger_handler)

        self.messages = list()

    next_error_id = 0

    @asyncio.coroutine
    def error_handler(self, message):
        yield from self.clean_messages()
        message_data = {"time": time.monotonic(), "message": message.getMessage(), "level": message.levelname, "id": self.next_error_id}
        self.next_error_id += 1
        self.messages.append(message_data)

    @asyncio.coroutine
    def clean_messages(self):
        # Clean all timed-out messages
        current_time = time.monotonic()
        for message in self.messages[:]:
            if message["time"] + 10 < current_time:
                self.messages.remove(message)

    @asyncio.coroutine
    def json_handler(self, request):
        data_structure = dict()
        data_structure["version"] = __version__
        yield from self.clean_messages()
        data_structure["messages"] = self.messages
        data_structure["next_mid"] = self.next_error_id
        data_structure["modules"] = list()
        for mod_path in self.engine.running_modules:
            mod_object = self.engine.running_modules[mod_path]
            if not mod_object.alive:
                continue
            mod_data = dict()
            mod_data["subsystem"] = mod_path
            mod_data["description"] = mod_object.__doc__
            mod_data["filename"] = mod_path
            mod_data["status"] = "Running"
            mod_data["fallbacks"] = []
            data_structure["modules"].append(mod_data)
        text = json.dumps(data_structure, allow_nan=False)
        return web.Response(body=text.encode("utf-8"))

    @asyncio.coroutine
    def command_handler(self, request):
        commands = {"load": self.load_command, "load_config": self.load_config, "unload": self.unload_command, "reload": self.reload_command}
        data = yield from request.post()
        try:
            text = yield from commands[data["command"]](data["target"])
        except Exception as e:
            self.logger.error(str(e) + "\n" + traceback.format_exc())
            text = str(e)

        return web.Response(body=text.encode("utf-8"))

    @asyncio.coroutine
    def load_command(self, target):
        yield from self.engine.start_module(target)
        return "Successfully loaded " + target

    @asyncio.coroutine
    def unload_command(self, target):
        yield from self.engine.stop_module(target)
        return "Successfully unloaded " + target

    @asyncio.coroutine
    def reload_command(self, target):
        all_mods = self.engine.running_modules.copy()
        if target == "all":
            target_mods = [all_mods[mod] for mod in all_mods]
        else:
            target_mods = [all_mods[target], ]
        for mod in target_mods:
            yield from self.engine.reload_module(mod)
        return "Successfully reloaded " + target

    @asyncio.coroutine
    def load_config(self, path):
        self.engine.load_config(path)
        return "Successfully reloaded config file " + path

    @asyncio.coroutine
    def forward_request(self, request):
        return web.HTTPFound("/index.html")

    @asyncio.coroutine
    def init_server(self):
        app = web.Application()
        app.router.add_route("GET", "/api/json", self.json_handler)
        app.router.add_route("POST", "/api/command", self.command_handler)
        app.router.add_route("GET", "/", self.forward_request)
        app.router.add_static("/", self.file_root)
        self.srv = yield from self.engine.event_loop.create_server(app.make_handler(), port=5800)

        self.logger.info("Yeti WebUI started at  http://127.0.0.1:5800/index.html")

    def module_deinit(self):
        self.srv.close()