import socket
import threading
import pathlib
import sys
import gzip

def send_response(connection, status, headers, body=b''):
    header_str = f'HTTP/1.1 {status}\r\n'
    for key, value in headers.items():
        header_str += f'{key}: {value}\r\n'
    header_str += '\r\n'
    full_response = header_str.encode('utf-8') + body
    connection.sendall(full_response)

def handle_client(connection):
    try:
        data = connection.recv(1024, socket.MSG_PEEK)
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
                content_b = path[6:].encode('utf-8')
                if headers.get('Accept-Encoding'):
                    suported_encoders = {'gzip'}
                    accept_encoding = headers.get('Accept-Encoding').split(',')
                    accept_encoding = {s.strip() for s in accept_encoding}
                    enconders_str = ''.join(suported_encoders)

                    if suported_encoders.issubset(set(accept_encoding)):
                        content_str = path[6:]
                        content_b = content_str.encode('utf-8')
                        content_compress = gzip.compress(content_b)         

                        response_headers = {
                            'Content-Type': 'text/plain',
                            'Content-Encoding': enconders_str,
                            'Content-Length': len(content_compress)
                        }                                       
                        send_response(connection, '200 OK', response_headers, content_compress)

                    else:
                        response_headers = {
                            'Content-Type': 'text/plain',
                            'Content-Length': len(path[6:])
                        }
                        send_response(connection, '200 OK', response_headers, content_b)

                else:
                    response_headers = {
                            'Content-Type': 'text/plain',
                            'Content-Length': len(path[6:])
                        }
                    send_response(connection, '200 OK', response_headers, content_b)

        elif path == "/":
            send_response(connection, '200 OK', {})

        elif path.startswith('/user-agent'):
            user_agent = headers.get("User-Agent").encode()
            if user_agent:
                response_headers = {
                    'Content-Type': 'text/plain',
                    'Content-Length': len(user_agent)
                }
                send_response(connection, '200 OK', response_headers, user_agent)

        elif path.startswith('/files/'):
            file_path = path[7:]
            flag = sys.argv[2]
            local_file_path = pathlib.Path(flag, file_path)
            if local_file_path.exists() and local_file_path.is_file() and method == 'GET':
                f = open(local_file_path)
                file_content = f.read()
                file_size = len(file_content.encode())
                response_headers = {
                    'Content-Type': 'application/octet-stream',
                    'Content-Length': file_size
                }
                send_response(connection, '200 OK', response_headers, file_content.encode())
                f.close()

            elif method == 'POST':
                new_file = open(local_file_path, 'w')
                file_content = lines[-1]
                new_file.write(file_content)
                send_response(connection, '201 Created', {})
                new_file.close()
            else:
                send_response(connection, '404 Not Found', {})

        else: 
            send_response(connection, '404 Not Found', {})
    finally:
        connection.close()

def main():    
    
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    while True:
        connection, address = server_socket.accept()

        client_thread = threading.Thread(target=handle_client, args=(connection, ))
        client_thread.start()

if __name__ == "__main__":
    main()