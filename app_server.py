import socket
from cryptography.hazmat.primitives.asymmetric import ec
from helper_functions import *

# Server code
def server():    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", 65432))
    server_socket.listen(1)
    print("Server is listening...")

    server_public_key_bytes = server_socket.recv(1024)

    # Generate server's key pair
    server_private_key, server_public_key = generate_key_pair()

    # Send server's public key to client
    conn.send(server_public_key.public_bytes())

    # Receive client's public key
    client_public_key_bytes = conn.recv(1024)
    client_public_key = ec.EllipticCurvePublicKey.from_encoded_point(
        ec.SECP256R1(), client_public_key_bytes
    )



    ####### COMUNICACIÓN CLIENT-SERVER

    # Derive shared key
    shared_key = derive_shared_key(server_private_key, client_public_key)

    # Receive encrypted message from client
    nonce = conn.recv(12)
    ciphertext = conn.recv(1024)
    message = decrypt_message(shared_key, nonce, ciphertext)
    print(f"Received message: {message}")

    # Respond to client
    response = "Message received securely"
    nonce, ciphertext = encrypt_message(shared_key, response)
    conn.send(nonce)
    conn.send(ciphertext)

    conn.close()
