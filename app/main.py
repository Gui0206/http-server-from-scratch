import socket  # noqa: F401

CRLF = '\r\n'

def main():    
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    connection, address = server_socket.accept() # wait for client

    data = connection.recv(1024)

    if data.split()[1] != b'/':
        connection.sendall(b'HTTP/1.1 404 Not Found\r\n\r\n') 
        print('Connection Error')   
    else:
        connection.sendall(b'HTTP/1.1 200 OK\r\n\r\n')
        print('Connection Success')   
   
    #connection.sendall(b'HTTP/1.1 200 OK\r\n\r\n')    


if __name__ == "__main__":
    main()