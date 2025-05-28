import socket
from cryptography.hazmat.primitives import serialization
from helper_functions import *
import json

host = "127.0.0.1"
smartDevicePort = 65002
trustedAppPort = 65001
raPort = 65000

def main():
    # Genera par de claves, privada y publica del dispositivo
    client_private_key, client_public_key = generate_key_pair()
    print(client_public_key)

    #Coneccion al RA
    raSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    raSocket.connect((host, raPort))
    print(f"[SOCKET CONNECTION] Connected to RA")

    #Envio de llave al RA para registrarse
    public_key_pem = client_public_key.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)
    raSocket.sendall(public_key_pem)

    # Espera a que el RA le responda con su ID
    response = raSocket.recv(1024).decode()
    print(f"[RECEIVED] Id = {response}")
    raSocket.close()
    print(f"[CONNECTION END] RA socket has been closed")

    # Se conecta al Trusted App
    ''' Conexión Cliente - Servidor '''
    trustedAppSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    trustedAppSocket.connect((host, trustedAppPort))
    print(f"[SOCKET CONNECTION] Connected to Trusted Application")

    # 1 Mensaje de solicitud de comunicación
    message = "Smart Device: Communication request"
    trustedAppSocket.send(message.encode())

    # Recibe confirmación del Trusted App
    response = trustedAppSocket.recv(1024).decode()
    print(f"[RECEIVED] {response}")

    # 2 
    request = {
        'ID': id,
        'public_key': public_key_pem
    }
    request_bytes = json.dumps(request).encode('utf-8')
    trustedAppSocket.sendall(request_bytes)
    print(f"[RECEIVED] {response}")
    
    message = "Smart Device: Encrypted message"
    trustedAppSocket.send(message.encode())

    response = trustedAppSocket.recv(1024).decode()
    print(f"[RECEIVED] {response}")
    
    trustedAppSocket.close()
    print(f"[CONNECTION END] Trusted Application socket has been closed")

if __name__ == "__main__":
    main()