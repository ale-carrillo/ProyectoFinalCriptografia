import socket
import json
from helper_functions import *

if __name__ == "__main__":
    id = None
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", 65431))

    # Generate client's key pair
    client_private_key, client_public_key = generate_key_pair()

    # Receive server's public key
    server_public_key_bytes = client_socket.recv(1024)
    server_public_key = ec.EllipticCurvePublicKey.from_encoded_point(
        ec.SECP256R1(), server_public_key_bytes
    )

    # Send client's public key to server
    client_socket.send(client_public_key.public_bytes())
    
    client_id_bytes = client_socket.recv(1024)
    id = int.from_bytes(client_id_bytes, byteorder = "big")

    client_socket.close()


    ####### COMUNICACIÓN CLIENT-SERVER

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", 65432))
    request = {
        'ID': id,
        'public_key': client_public_key
    }

    request_bytes = json.dumps(request).encode('utf-8')
    client_socket.send(request_bytes)

# Convertir bytes de vuelta a un objeto
#objeto_recuperado_json = json.loads(bytes_objeto_json.decode('utf-8'))


    # Derive shared key
    shared_key = derive_shared_key(client_private_key, server_public_key)

    # Send encrypted message to server
    message = "Hello, secure server!"
    nonce, ciphertext = encrypt_message(shared_key, message)
    client_socket.send(nonce)
    client_socket.send(ciphertext)

    # Receive server's response
    nonce = client_socket.recv(12)
    ciphertext = client_socket.recv(1024)
    response = decrypt_message(shared_key, nonce, ciphertext)
    print(f"Server response: {response}")

    client_socket.close()

