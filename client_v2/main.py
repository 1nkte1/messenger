import socket

def establish_connection():
    host = socket.gethostbyname(socket.gethostname())
    port = 8080

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    print('established')


establish_connection()