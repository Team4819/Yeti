import json
import threading
import socket
import selectors
import traceback


class Messenger:

    running = False

    udp_port = None
    tcp_port = None
    address = None

    def __init__(self, messenger_id):
        self.message_types = {}
        self.address_book = {}

        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.messenger_id = messenger_id

        # Init message receive threads
        self.parent_thread = threading.current_thread()
        self.tcp_thread = threading.Thread(target=self._tcp_receive_loop, name="messenger_{}_tcp".format(messenger_id))
        self.udp_thread = threading.Thread(target=self._udp_receive_loop, name="messenger_{}_udp".format(messenger_id))

        # Init builtin message type
        self.register_message_type("address_resolution_request", self._on_address_resolution_request)

    def start_server(self, address, udp_port, tcp_port):
        self.address = address
        self.udp_port = udp_port
        self.tcp_port = tcp_port

        self.register_messenger_address(self.messenger_id, address, udp_port, tcp_port)
        self.running = True
        self.tcp_thread.start()
        self.udp_thread.start()
        print("Started {} on {}, {}, {}".format(self.messenger_id, address, udp_port, tcp_port))

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
                    ret = message["handler"](message["data"])
                    if ret is not None:
                        conn.send(json.dumps(ret).encode("utf-8"))
                finally:
                    conn.close()
        print("tcp loop terminated")
        self.tcp_sock.shutdown(socket.SHUT_RDWR)
        self.tcp_sock.close()

    def _udp_receive_loop(self):
        self.udp_sock.bind(("0.0.0.0", self.udp_port))
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
                    message["handler"](message["data"])
                except Exception as e:
                    print(traceback.format_exc())
        print("udp loop terminated")
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
        data["handler"] = self.message_types[message_type]
        return data

    def register_messenger_address(self, messenger_id, address=None, udp_port=None, tcp_port=None):
        if address is None:
            address = self.address
            udp_port = self.udp_port
            tcp_port = self.tcp_port
        self.address_book[messenger_id] = (address, udp_port, tcp_port)

    def register_message_type(self, message_type, callback):
        self.message_types[message_type] = callback

    def send_message(self, message_type, data, client_id, blocking=False):
        address, udp_port, tcp_port = self.resolve_address(client_id)
        message_dict = {
            "msg_type": message_type,
            "data": data,
        }
        data = json.dumps(message_dict)
        if blocking:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setblocking(True)
            sock.settimeout(3.0)
            sock.connect((address, tcp_port))
            sock.send(data.encode("utf-8"))
            ret_data = sock.recv(1024)
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
            s = ret_data.decode("utf-8")
            if s == "":
                return None
            return json.loads(s)
        else:
            self.udp_sock.sendto(data.encode("utf-8"), (address, udp_port))

    def _on_address_resolution_request(self, data):
        response = {"request_blacklist": data["request_blacklist"]}
        try:
            response["addr"], \
            response["udp_port"], \
            response["tcp_port"] = self.resolve_address(data["messenger_id"], data["request_blacklist"])
        except CouldNotResolveMessengerException:
            pass
        return response

    def resolve_address(self, messenger_id, request_blacklist=None):
        """
        Resolves the address and port number of a messenger.
        First tries to use cache, then scans all other registered messengers.
        """
        if messenger_id not in self.address_book:
            # Setup a request blacklist so we don't recurse over the network.
            if request_blacklist is None:
                request_blacklist = []
            for client_id in self.address_book:
                if (self.address, self.udp_port, self.tcp_port) == self.address_book[client_id]:
                    request_blacklist.append(client_id)
            for client_id in self.address_book:
                if client_id in request_blacklist:
                    continue
                try:
                    response = self.send_message("address_resolution_request",
                                                 {"messenger_id": messenger_id,
                                                  "request_blacklist": request_blacklist},
                                                 client_id, blocking=True)
                    if "addr" in response:
                        break
                    else:
                        request_blacklist.clear()
                        request_blacklist.extend(response["request_blacklist"])
                except (ConnectionError, socket.timeout) as e:
                    request_blacklist.append(client_id)
            else:
                raise CouldNotResolveMessengerException(messenger_id)
            self.address_book[messenger_id] = response["addr"], response["udp_port"], response["tcp_port"]
        return self.address_book[messenger_id]


class CouldNotResolveMessengerException(Exception):

    def __init__(self, messenger_id):
        super().__init__("{}".format(messenger_id))
        self.monitor_id = messenger_id