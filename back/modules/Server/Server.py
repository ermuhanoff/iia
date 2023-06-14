import json
from socket import socket, AF_INET, SOCK_STREAM
from typing import Any, Callable

from modules.Server.HandlerObejct import HandlerObejct
from modules.Utils.Logger import Logger
from modules.Utils.utils import text_to_bytes

Handler = Callable[[HandlerObejct], None]
MessageObject = dict[str, Any]


class Server:
    server_host: str = "localhost"
    backlog: int = 10

    command_handlers: dict[str, Handler] = {}

    def __init__(self, port: int):
        self.server_port = port
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind((self.server_host, port))

    def __receive_data(self, connection: socket) -> MessageObject:
        data = connection.recv(1024)

        return json.loads(data.decode())

    def __execute_command(self, received_object: MessageObject, connection: socket) -> None:
        command = received_object["command"]
        body = received_object["body"]

        if command is not None:
            Logger.debug(f"Received command '{command}' with body '{body}'")

            self.command_handlers[command](HandlerObejct(connection, command, body))

    def __accept_new_connection(self) -> None:
        try:
            connection, address = self.server_socket.accept()
            Logger.info(f"New connection from {address[0]}:{address[1]}")

            while True:
                received_object = self.__receive_data(connection=connection)

                self.__execute_command(received_object, connection=connection)
        except KeyboardInterrupt:
            Logger.info("Closed by user")

    def send_data(self, connection: socket, send_object: MessageObject) -> None:
        connection.send(text_to_bytes(json.dumps(send_object)))

    def listen(self):
        try:
            self.server_socket.listen(10)

            Logger.info(f"Server is running at {self.server_host}:{self.server_port}")

            self.__accept_new_connection()
        except Exception as err:
            Logger.error(f"Unexpected {err=}, {type(err)=}")
            self.__accept_new_connection()

    def add_handler(self, command: str, handler: Handler):
        self.command_handlers[command] = handler
