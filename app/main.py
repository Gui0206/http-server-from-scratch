import socket  # noqa: F401
import threading

def main():    
    
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    connection, address = server_socket.accept() # wait for client

    data = connection.recv(1024)        
    request_data = data.decode().split("\r\n")

    request_line = request_data[0]
    method, path, http_version = request_line.split()

    headers = {}
    for line in request_data[1:]:
        if line == "":
            break
        key, value = line.split(": ", 1)
        headers[key] = value

    def response(path):
        if path.startswith('/echo/'):
            response = f'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(path[6:])}\r\n\r\n{path[6:]}'
            return response.encode()

        elif path == "/":
            return b"HTTP/1.1 200 OK\r\n\r\n"
            print('deu certo')

        elif path.startswith('/user-agent'):
            user_agent = headers.get("User-Agent")
            if user_agent:

                response = f'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}'
                return response.encode()
        else: 
            return b'HTTP/1.1 404 Not Found\r\n\r\n'

    connection.sendall(response(path))
    connection.close()

    # while True:
    #    client_thread = threading.Thread(args=(connection, address))
    #    client_thread.start()


if __name__ == "__main__":
    main()