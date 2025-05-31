import socket
import threading
import json
import time
import struct
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from helper_functions import generate_key_pair, derive_shared_key, encrypt_message, decrypt_message

host = "127.0.0.1"
raPort = 65000
trustedAppPort = 65001

def register_to_ra(public_key):
    ra_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ra_socket.connect((host, raPort))
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()
    ra_socket.sendall(json.dumps({"public_key": pem}).encode())
    trusted_app_id = ra_socket.recv(1024).decode()
    ra_socket.close()
    print(f"[TrustedApp] Registrado con ID: {trusted_app_id}")
    return trusted_app_id

def query_ra_for_key(smart_device_id):
    ra_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ra_socket.connect((host, raPort))
    ra_socket.sendall(smart_device_id.encode())
    public_key_pem = ra_socket.recv(8192).decode()
    ra_socket.close()
    return public_key_pem

def handle_smart_device(client_socket, private_key, public_key, trusted_app_id):
    try:
        data = client_socket.recv(8192).decode()
        request = json.loads(data)
        sd_id = request.get("id")
        sd_pub_pem = request.get("public_key")

        # Validar con RA
        sd_pub_from_ra = query_ra_for_key(sd_id)
        if "ERROR" in sd_pub_from_ra or sd_pub_from_ra != sd_pub_pem:
            client_socket.sendall(b"ERROR: Smart Device no autenticado")
            print("[TrustedApp] Smart Device no autenticado")
            client_socket.close()
            return

        # Enviar id y llave pública Trusted App al Smart Device
        ta_pub_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()

        resp = json.dumps({"id": trusted_app_id, "public_key": ta_pub_pem})
        client_socket.sendall(resp.encode())

        # Derivar llave compartida
        sd_pub_key = load_pem_public_key(sd_pub_pem.encode())
        shared_key = derive_shared_key(private_key, sd_pub_key)
        print("[TrustedApp] Llave compartida derivada con Smart Device.")

        # Recibir mensaje cifrado (nonce + ciphertext)
        data_enc = client_socket.recv(1024)
        nonce = data_enc[:12]
        timestamp = data_enc[12:20]
        ciphertext = data_enc[20:]

        # Validación timestamp
        sDTime = struct.unpack("d", timestamp)[0]
        now = time.time()
        if abs(now - sDTime) > 30:
            client_socket.sendall(b"ERROR: Smart Device, mensaje rechazado por posible replay attack")
            print("[TrustedServer] Posible replay attack")
            client_socket.close()
            return

        decrypted = decrypt_message(shared_key, nonce, ciphertext)
        
        print("[TrustedServer] Mensaje cifrado del SmartDevice:", ciphertext)
        print("[TrustedServer] Mensaje descifrado con llave derivada:", decrypted)

        # Responder cifrado
        timestamp_resp = struct.pack("d", time.time())
        nonce_resp, ciphertext_resp = encrypt_message(shared_key, "Hola SD este es un mensaje cifrado como respuesta desde el TS")
        print("[TrustedServer] Respuesta enviada al SmartDevice: Hola SD este es un mensaje cifrado como respuesta desde el TS")
        client_socket.sendall(nonce_resp + timestamp_resp + ciphertext_resp)

    except Exception as e:
        print(f"[TrustedApp ERROR] {e}")
    finally:
        client_socket.close()

def main():
    private_key, public_key = generate_key_pair()
    trusted_app_id = register_to_ra(public_key)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, trustedAppPort))
    server.listen()
    print(f"[TrustedApp] Escuchando conexiones en {host}:{trustedAppPort}")

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

