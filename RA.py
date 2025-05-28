import socket
from helper_functions import *
import time

if __name__ == "__main__":
    memory = dict()
    curr_id = 1

    RA_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    RA_socket.connect(("localhost", 65431))

    # Receive server's public key
    client_public_key_bytes = RA_socket.recv(1024)
    client_public_key = ec.EllipticCurvePublicKey.from_encoded_point(
        ec.SECP256R1(), client_public_key_bytes
    )
    memory[curr_id] = client_public_key

    # Send client's public key to server
    RA_socket.send(curr_id.to_bytes(4, byteorder='big'))    
    print(f"Id [{curr_id}], llave publica [{client_public_key}]")
    curr_id += 1

    time.sleep(1)
    
    client_id_bytes = RA_socket.recv(1024)
    client_id = int.from_bytes(client_id_bytes, byteorder='big')

    response = "good" if client_id in memory else "bad"
    RA_socket.send(response.encode("utf-8"))    

    RA_socket.close()


