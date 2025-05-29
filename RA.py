import socket
import threading
import json
import os
import uuid

host = "127.0.0.1"
raPort = 65000
clients_file = "clients.json"

def load_clients():
    if not os.path.exists(clients_file):
        with open(clients_file, "w") as f:
            json.dump({}, f)
    with open(clients_file, "r") as f:
        return json.load(f)

def save_clients(clients):
    with open(clients_file, "w") as f:
        json.dump(clients, f, indent=4)

def register_public_key(pem_key):
    clients = load_clients()
    client_id = str(uuid.uuid4())
    clients[client_id] = pem_key
    save_clients(clients)
    return client_id

def handle_client(client_socket, addr):
    try:
        data = client_socket.recv(8192).decode()

        try:
            request = json.loads(data)
            # Registro: JSON con "public_key"
            if isinstance(request, dict) and "public_key" in request:
                pem_key = request["public_key"]
                client_id = register_public_key(pem_key)
                client_socket.sendall(client_id.encode())
                print(f"[RA] Registrado cliente con ID: {client_id}")
                return
        except Exception:
            pass

        # Consulta: id plano
        client_id = data.strip()
        clients = load_clients()
        if client_id in clients:
            pem_key = clients[client_id]
            client_socket.sendall(pem_key.encode())
            print(f"[RA] Enviada llave pública para ID: {client_id}")
        else:
            client_socket.sendall(b"ERROR: ID no registrado")
            print(f"[RA] ID no encontrado: {client_id}")

    except Exception as e:
        print(f"[RA ERROR] {e}")
        client_socket.sendall(b"ERROR interno en RA")
    finally:
        client_socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, raPort))
    server.listen()
    print(f"[RA] Servidor escuchando en {host}:{raPort}")

    try:
        while True:
            client_socket, addr = server.accept()
            threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\n[RA] Servidor detenido")
    finally:
        server.close()

if __name__ == "__main__":
    main()
