import socket
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
    client_id = ra_socket.recv(1024).decode()
    ra_socket.close()
    print(f"[SmartDevice] Registrado con ID: {client_id}")
    return client_id

def query_ra_for_key(trusted_app_id):
    ra_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ra_socket.connect((host, raPort))
    ra_socket.sendall(trusted_app_id.encode())
    public_key_pem = ra_socket.recv(8192).decode()
    ra_socket.close()
    return public_key_pem

def connect_to_trusted_app(client_id, private_key, public_key):
    ts_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ts_socket.connect((host, trustedAppPort))

    # Enviar JSON con id + llave pública PEM
    pub_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()
    data = json.dumps({"id": client_id, "public_key": pub_pem})
    ts_socket.sendall(data.encode())

    # Recibir JSON con id + llave pública Trusted Server
    response = ts_socket.recv(8192).decode()
    resp_json = json.loads(response)
    ts_id = resp_json["id"]
    ts_pub_pem = resp_json["public_key"]

    # Validar con RA
    ta_pub_from_ra = query_ra_for_key(ts_id)
    if "ERROR" in ta_pub_from_ra or ta_pub_from_ra != ts_pub_pem:
        ts_socket.sendall(b"ERROR: Trusted Server no autenticado")
        print("[SmartDevice] Trusted Server no autenticado")
        ts_socket.close()
        return

    # Cargar la llave pública del Trusted Server
    ts_pub_key = load_pem_public_key(ts_pub_pem.encode())

    # Derivar llave compartida
    shared_key = derive_shared_key(private_key, ts_pub_key)
    print("[SmartDevice] Llave compartida derivada con Trusted Server.")

    # Comunicación cifrada de prueba
    timestamp = struct.pack("d", time.time())
    nonce, ciphertext = encrypt_message(shared_key, "Hola TS este es un mensaje cifrado desde el SD")
    print("[SmartDevice] Mensaje enviado al Trusted Server: Hola TS este es un mensaje cifrado desde el SD")
    ts_socket.sendall(nonce + timestamp + ciphertext)


    # Recibir respuesta cifrada junto con validación de replay attack
    recv = ts_socket.recv(1024)
    nonce_r = recv[:12]
    timestamp_r = recv[12:20]
    ciphertext_r = recv[20:]

    # Validación timestamp
    tsTime = struct.unpack("d", timestamp_r)[0]
    now = time.time()
    if abs(now - tsTime) > 30:
        ts_socket.sendall(b"ERROR: Trusted Server, mensaje rechazado por posible replay attack")
        print("[SmartDevice] Posible replay attack")
        ts_socket.close()
        return

    decrypted = decrypt_message(shared_key, nonce_r, ciphertext_r)
    
    print("[SmartDevice] Mensaje cifrado del TrustedApp:", ciphertext_r)
    print("[SmartDevice] Mensaje descifrado con llave derivada:", decrypted)

    ts_socket.close()

def main():
    private_key, public_key = generate_key_pair()
    client_id = register_to_ra(public_key)
    connect_to_trusted_app(client_id, private_key, public_key)

if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
