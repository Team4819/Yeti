import json
import threading
import socket
import selectors
import traceback


class Messenger:

    running = False
    udp_port = None
    tcp_port = None
    message_types = {}

    def __init__(self, debug_name=None):
        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Init message receive threads
        self.parent_thread = threading.current_thread()
        self.tcp_thread = threading.Thread(target=self._tcp_receive_loop, name="messenger_{}_tcp".format(debug_name))
        self.udp_thread = threading.Thread(target=self._udp_receive_loop)

    def start_server(self, tcp_port, udp_port):
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        self.running = True
        self.tcp_thread.start()
        self.udp_thread.start()

    def _check_alive(self):
        self.running = self.running and self.parent_thread.is_alive()

    def stop_server(self):
        self.running = False
        if self.udp_thread.is_alive():
            self.udp_thread.join()
        if self.tcp_thread.is_alive():
            self.tcp_thread.join()

    def _tcp_receive_loop(self):
        self.tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_sock.bind(("0.0.0.0", self.tcp_port))
        self.tcp_sock.setblocking(False)
        self.tcp_sock.listen(10)
        selector = selectors.DefaultSelector()
        selector.register(self.tcp_sock, selectors.EVENT_READ)
        while self.running:
            self._check_alive()
            events = selector.select(1)
            for _, _ in events:
                try:
                    conn, addr = self.tcp_sock.accept()
                    conn.setblocking(True)
                    conn.settimeout(0.005)
                    str_dat = conn.recv(1024)

                    message = self._parse_message(str_dat.decode("utf-8"))
                    ret = message["handler"](message)
                    if ret is not None:
                        conn.send(json.dumps(ret).encode("utf-8"))
                finally:
                    conn.close()
        self.tcp_sock.shutdown(socket.SHUT_RDWR)
        self.tcp_sock.close()

    def _udp_receive_loop(self):
        self.udp_sock.bind(("0.0.0.0", self.udp_port))
        print(self.udp_port)
        self.udp_sock.setblocking(False)
        selector = selectors.DefaultSelector()
        selector.register(self.udp_sock, selectors.EVENT_READ)
        while self.running:
            self._check_alive()
            events = selector.select(1)
            for _, _ in events:
                try:
                    str_dat = self.udp_sock.recv(1024)
                    message = self._parse_message(str_dat.decode("utf-8"))
                    message["handler"](message)
                except Exception as e:
                    print(traceback.format_exc())
        self.udp_sock.close()

    def _parse_message(self, msg):
        if msg == "":
            return None
        data = json.loads(msg)
        for k in ["msg_type"]:
            if k not in data:
                raise ValueError("Invalid message, missing {} field.".format(k))
        if data["msg_type"] not in self.message_types:
            raise ValueError("Invalid message type: was {}, should be one of {}".format(data["msg_type"], [k for k in self.message_types.keys()]))
        message_type = data["msg_type"]
        data["handler"] = self.message_types[message_type]["handler"]
        return data

    def send_message(self, message, address, blocking=False):
        data = json.dumps(message)
        if blocking:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setblocking(True)
            sock.settimeout(10.0)
            sock.connect(address)
            sock.send(data.encode("utf-8"))
            ret_data = sock.recv(1024)
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
            s = ret_data.decode("utf-8")
            if s == "":
                return None
            return json.loads(s)
        else:
            self.udp_sock.sendto(data.encode("utf-8"), address)
