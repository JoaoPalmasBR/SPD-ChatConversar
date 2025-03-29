import socket
import threading

def receive_messages(client_socket):
    while True:
        try:
            # Recebe a mensagem do servidor (de outros clientes)
            message = client_socket.recv(1024).decode()
            if message:
                print(f"\n{message}")  # Exibe a mensagem recebida
        except Exception as e:
            print(f"Erro ao receber mensagem: {e}")
            break

def start_client(server_host='172.29.28.32', server_port=12345):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Tenta se conectar ao servidor
    try:
        client.connect((server_host, server_port))
    except ConnectionRefusedError:
        print("Erro: O servidor não está disponível.")
        return
    
    # Recebe a mensagem inicial do servidor (ex: servidor cheio ou mensagem de boas-vindas)
    initial_msg = client.recv(1024).decode()
    
    if "Servidor cheio" in initial_msg:
        print(f"⚠️ {initial_msg}")
        client.close()
        return

    print(initial_msg)

    # Exibe o endereço do cliente
    client_address = client.getsockname()
    print(f"Conectado ao servidor como {client_address}. Comece a conversar!")

    # Inicia a thread para receber mensagens do servidor
    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.daemon = True  # Permite que a thread seja encerrada quando o cliente for desconectado
    receive_thread.start()

    while True:
        message = input("Digite sua mensagem: ")
        
        # Se o cliente digitar 'sair', envia a mensagem e encerra a conexão
        if message.lower() == 'sair':
            client.send(message.encode())
            print("Desconectando...")
            break

        # Envia a mensagem para o servidor
        client.send(message.encode())

    print(f"Cliente {client_address} desconectado.")
    client.close()

if __name__ == "__main__":
    start_client()
