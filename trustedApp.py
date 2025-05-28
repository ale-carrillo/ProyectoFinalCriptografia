import socket
import threading
import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from helper_functions import *

host = "127.0.0.1"
ra_port = 65000
trusted_app_port = 65001

def handle_smart_device(client_socket, private_key, public_key, trusted_app_id):
    try:
        data = client_socket.recv(8192).decode()
        request = json.loads(data)
        smart_device_id = request.get("id")
        smart_device_public_pem = request.get("public_key")

        ra_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ra_socket.connect((host, ra_port))
        ra_socket.sendall(smart_device_id.encode())
        smart_device_public_from_ra = ra_socket.recv(8192).decode()
        ra_socket.close()
        if "ERROR" in smart_device_public_from_ra or smart_device_public_from_ra != smart_device_public_pem:
            client_socket.sendall(b"ERROR: Smart Device no autenticado")
            print("[TrustedApp] Smart Device no autenticado")
            client_socket.close()
            return

        ta_pub_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()

        resp = json.dumps({"id": trusted_app_id, "public_key": ta_pub_pem})
        client_socket.sendall(resp.encode())

        smart_device_public_key = load_pem_public_key(smart_device_public_pem.encode())
        shared_key = derive_shared_key(private_key, smart_device_public_key)
        print("[TrustedApp] Llave compartida derivada con Smart Device.")

        data_enc = client_socket.recv(1024)
        nonce = data_enc[:12]
        ciphertext = data_enc[12:]
        plaintext = decrypt_message(shared_key, nonce, ciphertext)
        print("[TrustedApp] Mensaje recibido:", plaintext)

        nonce_resp, ciphertext_resp = encrypt_message(shared_key, "Hola Smart Device, mensaje cifrado desde Trusted Server")
        client_socket.sendall(nonce_resp + ciphertext_resp)

    except Exception as e:
        print(f"[TrustedApp ERROR] {e}")
    finally:
        client_socket.close()

def main():
    private_key, public_key = generate_key_pair()
    
    ra_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ra_socket.connect((host, ra_port))
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()
    ra_socket.sendall(json.dumps({"public_key": pem}).encode())
    trusted_app_id = ra_socket.recv(1024).decode()
    ra_socket.close()
    print(f"[TrustedApp] Registrado con ID: {trusted_app_id}")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, trusted_app_port))
    server.listen()
    print(f"[TrustedApp] Escuchando conexiones en {host}:{trusted_app_port}")

    try:
        while True:
            client_socket, addr = server.accept()
            threading.Thread(target=handle_smart_device, args=(client_socket, private_key, public_key, trusted_app_id), daemon=True).start()
    except KeyboardInterrupt:
        print("\n[TrustedApp] Servidor detenido")
    finally:
        server.close()

if __name__ == "__main__":
    main()