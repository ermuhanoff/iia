from socket import socket


class HandlerObejct:
    connection: socket
    command: str
    body: str

    def __init__(self, connection: socket, command: str, body: str) -> None:
        self.command = command
        self.body = body
        self.connection = connection
