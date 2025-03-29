# client_chat.py
import socket
import threading

def receber_mensagens(sock):
    while True:
        try:
            msg = sock.recv(1024).decode()
            if msg:
                print(f"\n{msg}")
        except:
            print("❌ Conexão encerrada.")
            break

def start_client(server_host='172.29.28.20', server_port=12345):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((server_host, server_port))
    except:
        print("Erro ao conectar ao servidor.")
        return

    threading.Thread(target=receber_mensagens, args=(client,), daemon=True).start()

    try:
        while True:
            msg = input()
            if msg.lower() == "sair":
                client.send(msg.encode())
                break
            client.send(msg.encode())
    except KeyboardInterrupt:
        client.send("sair".encode())
    finally:
        client.close()

if __name__ == "__main__":
    start_client()
