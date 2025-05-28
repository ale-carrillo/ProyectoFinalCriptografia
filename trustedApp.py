import socket
import threading

host = "127.0.0.1"
trustedAppPort = 65001
raPort = 65000

def serverSocketCreation():
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((host, trustedAppPort))
    serverSocket.listen()
    return serverSocket

def clientConnection(clientSocket, address):
    try:
        print(f"[NEW CONNECTION] From {address}")
        data = clientSocket.recv(1024).decode()
        print(f"[RECEIVED] {data}")

        response = "Trusted Application: Communication request received"
        clientSocket.sendall(response.encode())

        raSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raSocket.connect((host, raPort))
        print(f"[SOCKET CONNECTION] Connected to RA")

        message = "Trusted Application: Validation request"
        raSocket.sendall(message.encode())

        raResponse = raSocket.recv(1024).decode()
        print(f"[RECEIVED] {raResponse}")

        raResponse = raSocket.recv(1024).decode()
        print(f"[RECEIVED] {raResponse}")

        raSocket.close()
        print(f"[CONNECTION END] RA socket has been closed")

        response = "Trusted Application: Communication request accepted"
        clientSocket.sendall(response.encode())

        response = clientSocket.recv(1024).decode()
        print(f"[RECEIVED] {response}") 

        message = "Trusted Application: Encrypted message"
        clientSocket.sendall(message.encode())
        
    except Exception as e:
        print(f"[ERROR] {e}")

    finally:
        clientSocket.close()
        print(f"[CONNECTION END] Client socket has been closed")

def main():
    serverSocket = serverSocketCreation()
    print(f"[SOCKET CREATION] Trusted Application is up")

    try:
        while True:
            clientSocket, address = serverSocket.accept()
            clientThread = threading.Thread(target = clientConnection, args = (clientSocket, address))
            clientThread.daemon = True
            clientThread.start()

    except KeyboardInterrupt:
        print(f"[SOCKET CLOSE] Trusted Application is down")

    finally:
        serverSocket.close()
        print(f"[SOCKET CLOSE] Trusted Application socket has been closed")

if __name__ == "__main__":
    main()