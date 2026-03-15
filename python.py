import socket
import threading
import pathlib
import sys
import gzip

# ==========================================
# 1. O ROTEADOR (Decorator Pattern)
# ==========================================
ROUTES = {}

def route(path_prefix):
    def decorator(handler_func):
        ROUTES[path_prefix] = handler_func
        return handler_func
    return decorator

# Helper para enviar respostas
def send_response(connection, status, response_headers, headers, body=b''):
    if headers.get('Connection') == 'close':
        response_headers['Connection'] = 'close'
    
    header_str = f'HTTP/1.1 {status}\r\n'
    for key, value in response_headers.items():
        header_str += f'{key}: {value}\r\n'
    header_str += '\r\n'
    full_response = header_str.encode('utf-8') + body
    connection.sendall(full_response)


# ==========================================
# 2. OS CONTROLLERS (Regras de negócio isoladas)
# ==========================================

@route('/echo/')
def handle_echo(method, path, headers, body, directory):
    # A lógica original do GZIP foi mantida aqui dentro, exatamente como você pediu
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
            return '200 OK', response_headers, content_compress
        else:
            response_headers = {
                'Content-Type': 'text/plain',
                'Content-Length': len(path[6:])
            }
            return '200 OK', response_headers, content_b
    else:
        response_headers = {
            'Content-Type': 'text/plain',
            'Content-Length': len(path[6:])
        }
        return '200 OK', response_headers, content_b

@route('/user-agent')
def handle_user_agent(method, path, headers, body, directory):
    user_agent = headers.get("User-Agent").encode()
    if user_agent:
        response_headers = {
            'Content-Type': 'text/plain',
            'Content-Length': len(user_agent)
        }
        return '200 OK', response_headers, user_agent
    return '200 OK', {}, b''

@route('/files/')
def handle_files(method, path, headers, body, directory):
    file_path = path[7:]
    local_file_path = pathlib.Path(directory, file_path)
    
    # Mantido o open() em modo texto, conforme solicitado
    if local_file_path.exists() and local_file_path.is_file() and method == 'GET':
        with open(local_file_path) as f:
            file_content = f.read()
            file_size = len(file_content.encode())
            response_headers = {
                'Content-Type': 'application/octet-stream',
                'Content-Length': file_size
            }
            return '200 OK', response_headers, file_content.encode()

    elif method == 'POST':
        with open(local_file_path, 'w') as new_file:
            file_content = body
            new_file.write(file_content)
        return '201 Created', {}, b''
    
    return '404 Not Found', {}, b''

@route('/')
def handle_root(method, path, headers, body, directory):
    if path == '/':
        return '200 OK', {}, b''
    return '404 Not Found', {}, b''


# ==========================================
# 3. O FRONT CONTROLLER (Motor de roteamento)
# ==========================================

def handle_client(connection, directory):
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                return

            # Mantido o bug do decode e split nas quebras de linha textuais
            req, body = data.decode().split('\r\n\r\n')

            lines = req.split("\r\n")
            method, path, http_version = lines[0].split()

            headers = {}
            for line in lines[1:]:
                if line == "":
                    break
                key, value = line.split(": ", 1)
                headers[key] = value
                
            # A MÁGICA ACONTECE AQUI: O Roteador Dinâmico
            handler_function = None
            
            # Ordenamos as rotas da maior para a menor para garantir que 
            # '/files/' seja testado antes de '/'
            for route_prefix, func in sorted(ROUTES.items(), key=lambda x: len(x[0]), reverse=True):
                if path.startswith(route_prefix):
                    # Pequena trava de segurança para a rota raiz
                    if route_prefix == '/' and path != '/':
                        continue
                    handler_function = func
                    break

            # Executa a função encontrada ou devolve 404
            if handler_function:
                status, resp_headers, resp_body = handler_function(method, path, headers, body, directory)
            else:
                status, resp_headers, resp_body = '404 Not Found', {}, b''

            # O envio da resposta fica centralizado num único lugar!
            send_response(connection, status, resp_headers, headers, resp_body)

            if headers.get('Connection') == 'close':
                break
    finally:
        connection.close()

def main():        
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    directory = sys.argv[2] if len(sys.argv) >= 3 and sys.argv[1] == '--directory' else '.'

    while True:
        connection, address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(connection, directory))
        client_thread.start()

if __name__ == "__main__":
    main()