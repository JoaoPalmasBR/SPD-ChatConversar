# server_chat_mp.py
import socket
import multiprocessing
from datetime import datetime

LOG_FILE = "chat_log.txt"

def log(mensagem):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {mensagem}\n")

def broadcast(mensagem, remetente_socket, clientes, apelidos):
    for sock in list(clientes.keys()):
        if sock != remetente_socket:
            try:
                sock.send(mensagem.encode())
            except:
                sock.close()
                del clientes[sock]
                del apelidos[sock]

def handle_client(client_socket, addr, clientes, apelidos):
    try:
        client_socket.send("Digite seu apelido: ".encode())
        apelido = client_socket.recv(1024).decode().strip()[:30]

        if not apelido:
            apelido = f"{addr[0]}:{addr[1]}"

        clientes[client_socket] = addr
        apelidos[client_socket] = apelido

        msg_boas_vindas = f"✅ {apelido} entrou no chat."
        print(msg_boas_vindas)
        log(msg_boas_vindas)
        broadcast(msg_boas_vindas, client_socket, clientes, apelidos)
        client_socket.send("Você entrou no chat! Digite mensagens ou use comandos como /users.\n".encode())

        while True:
            msg = client_socket.recv(1024).decode()
            if not msg or msg.lower() == "sair":
                break

            msg = msg.strip()
            if len(msg) > 500:
                client_socket.send("⚠️ Mensagem muito longa.".encode())
                continue

            # Comando /users
            if msg.startswith("/users"):
                online = [apelidos[s] for s in apelidos]
                client_socket.send(f"👥 Online: {', '.join(online)}\n".encode())
                continue

            mensagem_formatada = f"[{apelidos[client_socket]}] {msg}"
            print(mensagem_formatada)
            log(mensagem_formatada)
            broadcast(mensagem_formatada, client_socket, clientes, apelidos)

    except Exception as e:
        print(f"Erro com cliente {addr}: {e}")
    finally:
        apelido = apelidos.get(client_socket, f"{addr}")
        despedida = f"❌ {apelido} saiu do chat."
        print(despedida)
        log(despedida)
        broadcast(despedida, client_socket, clientes, apelidos)

        client_socket.close()
        if client_socket in clientes:
            del clientes[client_socket]
        if client_socket in apelidos:
            del apelidos[client_socket]

def start_server(host='0.0.0.0', port=12345):
    manager = multiprocessing.Manager()
    clientes = manager.dict()
    apelidos = manager.dict()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print(f"💬 Servidor multiprocessado ouvindo em {host}:{port}")
    log(f"Servidor iniciado em {host}:{port}")

    try:
        while True:
            client_socket, addr = server.accept()
            processo = multiprocessing.Process(target=handle_client, args=(client_socket, addr, clientes, apelidos))
            processo.daemon = True
            processo.start()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()
