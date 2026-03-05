import socket  # noqa: F401

CRLF = '\r\n'

def main():    
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    connection, address = server_socket.accept() # wait for client

    data = connection.recv(1024)
    
    """
    print('data:')
    print(data)
    print('--------')
    print('data.split():')
    print(data.split())
    print('------')
    print("split()[2]")
    print(data.split()[1])
    """

    if data.split()[1] != b'/':
        connection.sendall(b'HTTP/1.1 404 Not Found\r\n\r\n') 
        print('ERRROUUU')   
    else:
        connection.sendall(b'HTTP/1.1 200 OK\r\n\r\n')
        print('ACERTO')   
   
    #connection.sendall(b'HTTP/1.1 200 OK\r\n\r\n')    


if __name__ == "__main__":
    main()