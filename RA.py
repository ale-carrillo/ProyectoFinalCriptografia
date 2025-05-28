import socket
import threading

host = "127.0.0.1"
raPort = 65000

def serverSocketCreation():
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((host, raPort))
    serverSocket.listen()
    return serverSocket

def clientConnection(clientSocket, address):
    try:
        data = clientSocket.recv(1024)
        public_key = serialization.load_pem_public_key(data)
        pem_key = public_key.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo).decode('utf-8')
        print(f"[RECEIVED] {public_key}")
        
        client_id = register_public_key(pem_key)
        response = f"{client_id}"
        clientSocket.sendall(response.encode())
        clientSocket.close()

        # !!!
        if "Smart Device: " in data:
            response = "RA: Public key and ID request received"
            clientSocket.sendall(response.encode())

        elif "Trusted Application: " in data:
            response = "RA: Validation request received"
            clientSocket.sendall(response.encode())

            response = "RA: Validation OK"
            clientSocket.sendall(response.encode())
        
        else:
            response = "RA: Unkown request"
            clientSocket.sendall(response.encode())

    except Exception as e:
        print(f"[ERROR] {e}")

    finally:
        clientSocket.close()
        print(f"[CONNECTION END] Client socket has been closed")

def main():
    serverSocket = serverSocketCreation()
    print(f"[SOCKET CREATION] RA is up")
    try:
        while True:
            clientSocket, address = serverSocket.accept()
            clientThread = threading.Thread(target = clientConnection, args = (clientSocket, address))
            clientThread.daemon = True
            clientThread.start()

    except KeyboardInterrupt:
        print(f"[SOCKET CLOSE] RA is down")

    finally:
        serverSocket.close()
        print(f"[CONNECTION END] RA socket has been closed")

if __name__ == "__main__":
    main()
