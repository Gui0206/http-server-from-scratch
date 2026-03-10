import socket  # noqa: F401
import threading
import tempfile
import os
import pathlib

def handle_client(connection):
    try:
        data = connection.recv(1024)
        if not data:
            return

        lines = data.decode().split("\r\n")
        method, path, http_version = lines[0].split()

        headers = {}
        for line in lines[1:]:
            if line == "":
                break
            key, value = line.split(": ", 1)
            headers[key] = value

        if path.startswith('/echo/'):
            response = f'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(path[6:])}\r\n\r\n{path[6:]}'

        elif path == "/":
            response = "HTTP/1.1 200 OK\r\n\r\n"

        elif path.startswith('/user-agent'):
            user_agent = headers.get("User-Agent")
            if user_agent:
                response = f'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}'
        
        elif path.startswith('/files/'):
            file_path = f'/tmp/{path[7:]}'
            local_file_path = pathlib.Path(os.curdir, file_path)
            f = open(local_file_path)
            file_content = f.read()
            file_size = len(file_content.encode())
            response = f'HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {file_size}\r\n\r\n{file_content}'
        
        else: 
            response = 'HTTP/1.1 404 Not Found\r\n\r\n'
        
        connection.sendall(response.encode())

    finally: connection.close()


def main():    
    
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    while True:
        connection, address = server_socket.accept()

        client_thread = threading.Thread(target=handle_client, args=(connection, ))
        client_thread.start()

if __name__ == "__main__":
    main()