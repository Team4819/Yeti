import yaml
#import paramiko
import time
import subprocess

from .messenger import *
from .runtime_exceptions import *


class Monitor:

    running = False
    module_timeout = 3  # Seconds after last heartbeat to declare a module dead

    def __init__(self, monitor_id, conf_path):
        self.monitor_id = monitor_id
        self.conf_path = conf_path

        # System configuration (read from yaml file)
        self.module_conf = {}
        self.monitor_conf = {}

        # Instance data
        self.node_data = {}
        self.module_data = {}

        self.local_module_processes = {}

        # Read yaml file
        file = open(conf_path)
        data = yaml.load(file)
        file.close()

        # Save config data
        self.module_conf.update(data.get("modules", {}))
        self.monitor_conf.update(data.get("monitors", {}))

        self.next_generated_port = max(self.monitor_conf[monitor_id]["udp_port"], self.monitor_conf[monitor_id]["tcp_port"]) + 1

        # Init messenger
        self.messenger = Messenger("mon_{}".format(self.monitor_id))
        self.messenger.register_message_type("heartbeat", self._on_heartbeat)
        self.messenger.register_message_type("node_bootstrap_request", self._on_node_bootstrap_request)
        self.messenger.register_message_type("module_data_request", self._on_module_data_request)


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
        self.messenger.start_server(self.monitor_conf[self.monitor_id]["addr"],
                                    self.monitor_conf[self.monitor_id]["udp_port"],
                                    self.monitor_conf[self.monitor_id]["tcp_port"])

    def stop(self):
        self.messenger.stop_server()

    def send_message(self, message_type, message, entity_id, blocking):
        result = self.messenger.send_message(message_type, message, entity_id, blocking)

        return result

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

                if self.module_conf[blame_module_id]["mon"] == self.monitor_id:
                    response = self._on_module_data_request({"module_id": blame_module_id})
                else:
                    response = self.messenger.send_message(
                        "module_data_request",
                        {"module_id": blame_module_id},
                        "mon_" + self.module_conf[blame_module_id]["mon"], blocking=True)

                if response is not None and response["running_state"] == "running":
                    self.messenger.send_message("module_restart_condition", {"module_id": module_id}, "module_" + module_id, blocking=False)

            if message["exception_cause"].startswith("outdated_state: "):
                blame_module_id, blame_key = message["exception_cause"][16:].split(".")

                response = self.messenger.send_message(
                    "get_state",
                    {
                        "module_id": blame_module_id,
                        "key": blame_key,
                        "age_limit": 1,
                    }, "module_" + blame_module_id, True)

                if not response["too_old"]:
                    self.messenger.send_message("module_restart_condition", {"module_id": module_id}, "module_" + module_id, blocking=False)

    def _on_node_bootstrap_request(self, message):
        if message["node_id"] not in self.node_data:
            udp_port = self.next_generated_port
            tcp_port = self.next_generated_port+1
            addr = self.monitor_conf[self.monitor_id]["addr"]
            self.next_generated_port += 2
            self.node_data[message["node_id"]] = {
                "addr": addr,
                "udp_port": udp_port,
                "tcp_port": tcp_port
            }
            self.messenger.register_messenger_address("node_{}".format(message["node_id"]), addr, udp_port, tcp_port)
        print("Bootstrapped node_{}".format(message["node_id"]))
        return self.node_data[message["node_id"]]

    def _on_module_data_request(self, message):
        if message["module_id"] not in self.module_data or \
                                time.time() - self.module_data[message["module_id"]]["last_beat"] > self.module_timeout:
            return None
        return self.module_data[message["module_id"]]

    def start_modules(self):
        to_start = []
        for module_id in self.module_conf:
            if self.module_conf[module_id]["mon"] == self.monitor_id:
                to_start.append(module_id)
        for module_id in to_start:
            self.start_module(module_id)

    def start_module(self, module_id):
        command = " ".join([self.module_conf[module_id]["cmd"], module_id, self.conf_path])
        self.local_module_processes[module_id] = subprocess.Popen(command, shell=True)
        print("module start command: {}".format(command))
