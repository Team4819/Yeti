import yaml
import time

from messenger import *
from runtime_exceptions import *


class Node:

    running = False

    def __init__(self, node_id, conf_path):
        self.node_id = node_id

        self.module_conf = {}
        self.monitor_conf = {}

        self.module_state_data = {}
        self.module_net_info = {}

        # Read yaml file
        file = open(conf_path)
        data = yaml.load(file)
        file.close()

        # Save config data
        self.module_conf.update(data.get("modules", {}))
        self.monitor_conf.update(data.get("monitors", {}))

        # Init messenger
        self.messenger = Messenger(messenger_id="node_" + self.node_id)
        self.messenger.register_message_type("get_state", self._on_get_state)
        self.messenger.register_message_type("set_state", self._on_set_state)
        self.messenger.register_message_type("module_restart_condition", self._on_restart_condition)

        # Register all listed connection data.
        for mon_id in self.monitor_conf:
            if "addr" in self.monitor_conf[mon_id]:
                self.messenger.register_messenger_address(
                    "mon_{}".format(mon_id),
                    self.monitor_conf[mon_id]["addr"],
                    self.monitor_conf[mon_id]["udp_port"],
                    self.monitor_conf[mon_id]["tcp_port"])

    def bootstrap_node(self, mon_id):

        response = self.messenger.send_message(
            "node_bootstrap_request",
            {"node_id": self.node_id}, "mon_"+mon_id, True)
        self.messenger.start_server(response["addr"], response["udp_port"], response["tcp_port"])

    def register_module(self, module_id):
        self.module_state_data[module_id] = {}
        self.messenger.register_messenger_address("module_{}".format(module_id))
        self.set_state("_running_state", "running", module_id)
        self.set_state("_exception_cause", "no_exception", module_id)
        # Send an initial heartbeat
        self.send_heartbeat(module_id)

    def send_message(self, msg_type, message, entity_id, blocking):
        try:
            return self.messenger.send_message(msg_type, message, entity_id, blocking)
        except (ConnectionError, socket.timeout, CouldNotResolveMessengerException) as err:
            prefix, specific_id = entity_id.split("_")
            if prefix == "module":
                raise UnreachableModuleException(specific_id)
            elif prefix == "mon":
                raise UnreachableMonitorException(specific_id)
            else:
                raise err

    def send_heartbeat(self, module_id):
        self.send_message(
            "heartbeat",
            {
                "module_id": module_id,
                "running_state": self.get_state("_running_state", module_id),
                "exception_cause": self.get_state("_exception_cause", module_id),
                "node_id": self.node_id,
            },
            "mon_" + self.module_conf[module_id]["mon"], blocking=False)

    def get_running_state(self, module_id):
        return self.get_state("_running_state", module_id)

    def report_module_exception(self, module_id, exception):
        if isinstance(exception, UnreachableModuleException):
            self.set_state("_exception_cause", "missing_module: {}".format(exception.module_id), module_id)
        elif isinstance(exception, OutdatedStateException):
            self.set_state("_exception_cause", "outdated_state: {}.{}".format(exception.module_id, exception.key), module_id)
        else:
            self.set_state("_exception_cause", "other_exception", module_id)
            print(traceback.format_exc())
        print("Module {} in exception state. Exception cause: {}".format(module_id, self.get_state("_exception_cause", module_id)))
        self.set_state("_running_state", "exception", module_id)

    def set_state(self, key, value, module_id, blocking=False):
        if module_id in self.module_state_data:
            self.module_state_data[module_id][key] = {
                "value": value,
                "timestamp": time.time()
            }
        else:
            self.send_message(
                "set_state",
                {
                    "module_id": module_id,
                    "key": key,
                    "value": value,
                },
                "module_" + module_id, blocking)

    def _on_set_state(self, message):
        module_id = message["module_id"]
        assert module_id in self.module_state_data
        self.set_state(message["key"], message["value"], module_id)

    def get_state(self, key, module_id, age_limit=0):
        if module_id in self.module_state_data:
            if key not in self.module_state_data[module_id]:
                raise OutdatedStateException(module_id, key)
            age = time.time() - self.module_state_data[module_id][key]["timestamp"]
            if age > age_limit > 0:
                raise OutdatedStateException(module_id, key)
            return self.module_state_data[module_id][key]["value"]
        else:
            response = self.send_message(
                "get_state",
                {
                    "module_id": module_id,
                    "key": key,
                    "age_limit": age_limit,
                },
                "module_" + module_id, True)
            if response["too_old"]:
                raise OutdatedStateException(module_id, key)
            return response["value"]

    def _on_get_state(self, message):
        module_id = message["module_id"]
        assert module_id in self.module_state_data
        response = {}
        try:
            response["value"] = self.get_state(message["key"], module_id, message["age_limit"])
            response["too_old"] = False
        except OutdatedStateException:
            response["too_old"] = True
        return response

    def _on_restart_condition(self, message):
        module_id = message["module_id"]
        assert module_id in self.module_state_data
        print("Exception cause '{}' cleared, {} restarted.".format(self.get_state("_exception_cause", module_id), module_id))
        self.set_state("_exception_cause", "no_exception", module_id)
        self.set_state("_running_state", "running", module_id)

