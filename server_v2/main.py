import logging
import socket
import threading
from openpyxl import load_workbook

logging.basicConfig(level=logging.DEBUG, filename="server.log", filemode="w",
                    format="%(asctime)s - %(levelname)s - %(message)s")

database = load_workbook('database.xlsx')
sheet = database.active

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen()
        logging.info(f"server started on {self.host}:{self.port}")

        while True:
            self.client, self.address = server.accept()

            connection = threading.Thread(target=self.create_connection)
            connection.start()

    def create_connection(self):
        user = Client(self.host, self.port, self.client, self.address)

    def receive(self, client):
        pass

    def transmit(self, client):
        pass


class Client(Server):
    def __init__(self, host, port, client, address):
        super().__init__(host, port)
        self.client = client
        self.address = address
        logging.info(f"client on {self.address} connected")


def main():
    host = socket.gethostbyname(socket.gethostname())
    port = None
    while port is None:
        try:
            port = int(input("enter port number: "))
            if port < 0 or port > 65535:
                raise ValueError
        except ValueError:
            port = None
            logging.exception("invalid port number")
    server = Server(host, port)
    server.start()


main()
