import socket

host = "127.0.0.1"
smartDevicePort = 65002
trustedAppPort = 65001
raPort = 65000

def main():
    raSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    raSocket.connect((host, raPort))
    print(f"[SOCKET CONNECTION] Connected to RA")

    message = "Smart Device: Register request"
    raSocket.sendall(message.encode())
    response = raSocket.recv(1024).decode()
    print(f"[RECEIVED] {response}")
    raSocket.close()
    print(f"[CONNECTION END] RA socket has been closed")

    trustedAppSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    trustedAppSocket.connect((host, trustedAppPort))
    print(f"[SOCKET CONNECTION] Connected to Trusted Application")

    message = "Smart Device: Communication request"
    trustedAppSocket.send(message.encode())

    response = trustedAppSocket.recv(1024).decode()
    print(f"[RECEIVED] {response}")

    response = trustedAppSocket.recv(1024).decode()
    print(f"[RECEIVED] {response}")
    
    message = "Smart Device: Encrypted message"
    trustedAppSocket.send(message.encode())

    response = trustedAppSocket.recv(1024).decode()
    print(f"[RECEIVED] {response}")
    
    trustedAppSocket.close()
    print(f"[CONNECTION END] Trusted Application socket has been closed")

if __name__ == "__main__":
    main()