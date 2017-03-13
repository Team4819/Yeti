import yaml
#import paramiko
import time
import subprocess

from messenger import Messenger
from runtime_exceptions import *


class Monitor:

    running = False
    module_timeout = 3  # Seconds after last heartbeat to declare a module dead

    def __init__(self, monitor_id, conf_path):
        self.monitor_id = monitor_id
        self.conf_path = conf_path

        self.module_conf = {}
        self.monitor_conf = {}

        self.node_data = {}
        self.module_data = {}

        self.module_processes = {}

        # Read yaml file
        file = open(conf_path)
        data = yaml.load(file)
        file.close()

        # Save config data
        self.module_conf.update(data.get("modules", {}))
        self.monitor_conf.update(data.get("monitors", {}))

        self.next_generated_port = max(self.monitor_conf[monitor_id]["tcp_port"], self.monitor_conf[monitor_id]["udp_port"]) + 1

        # Init messenger
        self.messenger = Messenger()
        self.messenger.message_types = {
            "heartbeat": {"handler": self._on_heartbeat},
            "node_bootstrap_request": {"handler": self._on_node_bootstrap_request},
            "module_address_request": {"handler": self._on_module_address_request},
            "module_data_request": {"handler": self._on_module_data_request}
        }

    # def bootstrap(self, conf_path):
    #     ssh = paramiko.SSHClient()
    #     sftp = paramiko.SFTPClient.from_transport(ssh.get_transport())
    #     for monitor in self.monitor_data:
    #         if self.monitor_data[monitor]["addr"] == "localhost":
    #             pass
    #         else:
    #             ssh.connect(
    #                 self.monitor_data[monitor]["addr"],
    #                 username=self.monitor_data[monitor]["user"],
    #                 password=self.monitor_data[monitor]["pass"])

    def start(self):
        self.messenger.start_server(
            self.monitor_conf[self.monitor_id]["tcp_port"],
            self.monitor_conf[self.monitor_id]["udp_port"]
        )

    def stop(self):
        self.messenger.stop_server()

    def send_message(self, message, entity_id, blocking):
        prefix, specific_id = entity_id.split("_", 1)
        if prefix == "module":
            if specific_id in self.module_data:
                node = self.module_data[specific_id]["node_id"]
                address = (self.monitor_conf[self.monitor_id]["addr"],
                           self.node_data[node]["tcp_port" if blocking else "udp_port"])
            else:
                response = self.send_message({
                    "msg_type": "module_address_request",
                    "module_id": specific_id,
                }, "mon_" + self.module_conf[specific_id]["mon"], True)
                if response["msg_type"] != "module_address_response":
                    raise NoSuchModuleException(specific_id)
                address = (response["addr"], response["tcp_port"] if blocking else response["udp_port"])

        elif prefix == "mon":
            address = (self.monitor_conf[specific_id]["addr"],
                       self.monitor_conf[specific_id]["tcp_port" if blocking else "udp_port"])
        else:
            raise ValueError("Invalid entitiy id: {}".format(entity_id))
        message["to"] = entity_id
        return self.messenger.send_message(message, address, blocking)

    def _on_heartbeat(self, message):
        # Store heartbeat data
        module_id = message["module_id"]
        self.module_data[module_id] = {
            "running_state": message["running_state"],
            "exception_cause": message["exception_cause"],
            "node_id": message["node_id"],
            "last_beat": time.time(),
        }

        # Handle exception report
        if message["running_state"] == "exception":
            if message["exception_cause"].startswith("missing_module: "):
                blame_module_id = message["exception_cause"][16:]

                response = self.send_message({
                    "msg_type": "module_data_request",
                    "module_id": blame_module_id},
                    "mon_" + self.module_conf[blame_module_id]["mon"], blocking=True)
                assert response["msg_type"] == "module_data_response"

                if response["data"]["running_state"] == "running":
                    self.send_message({"msg_type": "module_restart_condition"}, "module_" + module_id, blocking=False)

            if message["exception_cause"].startswith("outdated_state: "):
                blame_module_id, blame_key = message["exception_cause"][16:].split(".")

                response = self.send_message({
                    "msg_type": "get_state",
                    "key": blame_key,
                    "age_limit": 1,
                }, "module_" + blame_module_id, True)
                assert response["msg_type"] == "get_state_response"

                if not response["too_old"]:
                    self.send_message({"msg_type": "module_restart_condition"}, "module_" + module_id, blocking=False)

    def _on_node_bootstrap_request(self, message):
        udp_port = self.next_generated_port
        tcp_port = self.next_generated_port+1
        self.next_generated_port += 2
        self.node_data[message["node_id"]] = {
            "udp_port": udp_port,
            "tcp_port": tcp_port
        }
        response = {
            "msg_type": "node_bootstrap_response",
            "udp_port": udp_port,
            "tcp_port": tcp_port
        }
        return response

    def _on_module_address_request(self, message):
        if message["module_id"] not in self.module_data or \
                                time.time() - self.module_data[message["module_id"]]["last_beat"] > self.module_timeout:
            return {
                "msg_type": "module_address_response_err"
            }
        node_id = self.module_data[message["module_id"]]["node_id"]
        return {
            "msg_type": "module_address_response",
            "addr": self.monitor_conf[self.monitor_id]["addr"],
            "tcp_port": self.node_data[node_id]["tcp_port"],
            "udp_port": self.node_data[node_id]["udp_port"]
        }

    def _on_module_data_request(self, message):
        if message["module_id"] not in self.module_data or \
                                time.time() - self.module_data[message["module_id"]]["last_beat"] > self.module_timeout:
            return {
                "msg_type": "module_data_response_err"
            }
        return {
            "msg_type": "module_data_response",
            "data": self.module_data[message["module_id"]]
        }

    def start_modules(self):
        to_start = []
        for module_id in self.module_conf:
            if self.module_conf[module_id]["mon"] == self.monitor_id:
                to_start.append(module_id)
        for module_id in to_start:
            self.start_module(module_id)

    def start_module(self, module_id):
        command = " ".join([self.module_conf[module_id]["cmd"], module_id, self.conf_path])
        self.module_processes[module_id] = subprocess.Popen(command, shell=True)
        print("module start command: {}".format(command))
