import socket  # noqa: F401

CRLF = '\r\n'

def main():    
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    connection, address = server_socket.accept() # wait for client

    data = connection.recv(1024)
    #print(data.decode())

    request_data = data.decode().split("\r\n")
    print(request_data[2][12:])
    request_line = request_data[0]
    method, path, http_version = request_line.split()

    # if data.split()[1].startswith("/echo/"):

    if path.startswith('/echo/'):
        response = f'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(path[6:])}\r\n\r\n{path[6:]}'
        connection.sendall(response.encode())
        print(request_line)
    elif path == "/":
        connection.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
    elif path.startswith('/user-agent'):
        print(request_line)
        response = f'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(request_data[2][12:])}\r\n\r\n{request_data[2][12:]}'
        connection.sendall(response.encode())
    else: 
        connection.sendall(b'HTTP/1.1 404 Not Found\r\n\r\n') 

if __name__ == "__main__":
    main()