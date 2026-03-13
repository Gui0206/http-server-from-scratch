import socket
import threading
import pathlib
import sys
import gzip

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

        def send_response(connection, status, headers, body=b''):
            header_str = f'HTTP/1.1 {status}\r\n'
            for key, value in headers.items():
                header_str += f'{key}: {value}\r\n'
            header_str += '\r\n'

            full_response = header_str.encode('utf-8') + body
            connection.sendall(full_response)
        
            
        if path.startswith('/echo/'):
                if headers.get('Accept-Encoding'):
                    suported_encoders = {'gzip'}
                    accept_encoding = headers.get('Accept-Encoding').split(',')
                    accept_encoding = {s.strip() for s in accept_encoding}
                    enconders_str = ''.join(suported_encoders)

                    if suported_encoders.issubset(set(accept_encoding)):
                        content_str = path[6:]
                        content_b = content_str.encode('utf-8')
                        content_compress = gzip.compress(content_b)                                                

                        header = (f'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Encoding: {enconders_str}\r\nContent-Length: {len(content_compress)}\r\n\r\n' )
                        #response = header.encode('utf-8') + content_compress
                        send_response(connection, '200 OK', headers, content_compress)
                    else:
                        response = f'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(path[6:])}\r\n\r\n{path[6:]}'
                else:
                    response = f'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(path[6:])}\r\n\r\n{path[6:]}'

        elif path == "/":
            #response = "HTTP/1.1 200 OK\r\n\r\n"
            send_response(connection, '200 OK', headers)

        elif path.startswith('/user-agent'):
            user_agent = headers.get("User-Agent")
            if user_agent:
                response = f'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}'
        
        elif path.startswith('/files/'):
            file_path = path[7:]
            flag = sys.argv[2]
            local_file_path = pathlib.Path(flag, file_path)
            if local_file_path.exists() and local_file_path.is_file() and method == 'GET':
                f = open(local_file_path)
                file_content = f.read()
                file_size = len(file_content.encode())
                response = f'HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {file_size}\r\n\r\n{file_content}'
                f.close()
            elif method == 'POST':
                new_file = open(local_file_path, 'w')
                file_content = lines[-1]
                new_file.write(file_content)
                response = 'HTTP/1.1 201 Created\r\n\r\n'
                new_file.close()
            else:
                response = 'HTTP/1.1 404 Not Found\r\n\r\n'
        else: 
            response = 'HTTP/1.1 404 Not Found\r\n\r\n'
        
        #connection.sendall(response.encode())

    #finally: connection.close()
    finally: print('uhuuu')


def main():    
    
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    while True:
        connection, address = server_socket.accept()

        client_thread = threading.Thread(target=handle_client, args=(connection, ))
        client_thread.start()

if __name__ == "__main__":
    main()