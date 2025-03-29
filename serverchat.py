import socket
import multiprocessing

MAX_CLIENTS = 10
lock = multiprocessing.Lock()

# Lista de clientes conectados
def process_request(client_socket, addr, all_clients):
    global lock

    print(f"Cliente {addr} conectado.")
    
    # Envia mensagem inicial
    client_socket.send("Conectado ao servidor. Você pode começar a conversar.".encode())

    while True:
        try:
            # Recebe a mensagem do cliente
            message = client_socket.recv(1024).decode()
            if not message:
                break

            print(f"Mensagem recebida de {addr}: {message}")

            if message.lower() == "sair":
                print(f"Cliente {addr} solicitou desconexão.")
                break

            # Envia a mensagem para todos os clientes conectados
            with lock:
                for c in all_clients:
                    try:
                        c.send(f"Mensagem de {addr}: {message}".encode())  # Envia para todos os clientes
                    except Exception as e:
                        print(f"Erro ao enviar para o cliente {c.getpeername()}: {e}")

        except Exception as e:
            print(f"Erro durante a comunicação com {addr}: {e}")
            break

    # Remove o cliente da lista ao desconectar
    with lock:
        all_clients.remove(client_socket)

    print(f"Cliente {addr} desconectado.")
    client_socket.close()

def start_server(host='0.0.0.0', port=12345):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Servidor ouvindo em {host}:{port}")

    manager = multiprocessing.Manager()
    all_clients = manager.list()  # Lista compartilhada de clientes conectados

    while True:
        client_socket, addr = server.accept()

        with lock:
            if len(all_clients) >= MAX_CLIENTS:
                print(f"Servidor cheio! Recusando conexão de {addr}.")
                client_socket.send("Servidor cheio. Tente novamente mais tarde.".encode())
                client_socket.close()
                continue
            all_clients.append(client_socket)

        # Cria um processo para cada cliente
        client_process = multiprocessing.Process(target=process_request, args=(client_socket, addr, all_clients))
        client_process.daemon = True  # Permite que o processo filho seja finalizado quando o pai terminar
        client_process.start()

if __name__ == "__main__":
    start_server()
