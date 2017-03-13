import threading
import time
from .node import Node


class IterativeModule:

    thread_running = False

    def __init__(self, module_id):
        self.module_id = module_id

    def bootstrap_module(self, node):
        self.node = node
        self.module_config = node.module_conf[self.module_id]
        node.register_module(self.module_id)

        self._parent_thread = threading.current_thread()
        self.thread_running = True
        self._loop_thread = threading.Thread(target=self._main_loop)
        self._loop_thread.start()

    def _check_alive(self):
        self.thread_running = self.thread_running and self._parent_thread.is_alive()

    def _stop(self):
        self.thread_running = False
        self._loop_thread.join()

    def _main_loop(self):
        last_beat = 0
        last_running_state = "stopped"
        while self.thread_running:
            if time.time() - last_beat > 1:
                self.node.send_heartbeat(self.module_id)
                last_beat = time.time()
            curr_running_state = self.node.get_running_state(self.module_id)
            try:
                if last_running_state != "running" and curr_running_state == "running":
                    self.start()
                if curr_running_state == "running":
                    self.update()
                if last_running_state == "running" and curr_running_state != "running":
                    self.stop()
            except Exception as e:
                self.node.report_module_exception(self.module_id, e)
            last_running_state = curr_running_state
            time.sleep(1/self.module_config["update_frequency"])
            self._check_alive()

    def get_state(self, key, module_id=None, age_limit=0):
        if module_id is None:
            module_id = self.module_id
        return self.node.get_state(key, module_id, age_limit)

    def set_state(self, key, value, module_id=None, blocking=False):
        if module_id is None:
            module_id = self.module_id
        self.node.set_state(key, value, module_id, blocking)

    def start(self):
        pass

    def update(self):
        pass

    def stop(self):
        pass


def bootstrap_module(module_class, module_id, config_path, join=True):
    node = Node("node_" + module_id, config_path)
    node.bootstrap_node(node.module_conf[module_id]["mon"])
    module = module_class(module_id)
    module.bootstrap_module(node)
    if join:
        module._loop_thread.join()
