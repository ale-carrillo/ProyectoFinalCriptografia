import socket
import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from helper_functions import *

host = "127.0.0.1"
ra_port = 65000
trusted_app_port = 65001

def main():
    private_key, public_key = generate_key_pair()
    
    ra_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ra_socket.connect((host, ra_port))
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()
    ra_socket.sendall(json.dumps({"public_key": pem}).encode())
    client_id = ra_socket.recv(1024).decode()
    ra_socket.close()
    print(f"[SmartDevice] Registered with ID: {client_id}")

    trusted_app_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    trusted_app_socket.connect((host, trusted_app_port))

    pub_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()
    data = json.dumps({"id": client_id, "public_key": pub_pem})
    trusted_app_socket.sendall(data.encode())

    response = trusted_app_socket.recv(8192).decode()
    resp_json = json.loads(response)
    ts_id = resp_json["id"]
    ts_pub_pem = resp_json["public_key"]

    ts_pub_key = load_pem_public_key(ts_pub_pem.encode())

    shared_key = derive_shared_key(private_key, ts_pub_key)
    print("[SmartDevice] Shared key derived with Trusted Server.")

    nonce, ciphertext = encrypt_message(shared_key, "Hello Trusted Server, encrypted message from Smart Device")
    trusted_app_socket.sendall(nonce + ciphertext)

    recv = trusted_app_socket.recv(1024)
    nonce_r = recv[:12]
    ciphertext_r = recv[12:]
    plaintext = decrypt_message(shared_key, nonce_r, ciphertext_r)
    print("[SmartDevice] Message received from Trusted Server:", plaintext)

    trusted_app_socket.close()

if __name__ == "__main__":
    main()
