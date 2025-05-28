import csv
import os

CSV_FILE = "registry.csv"

def register_public_key(pem_key: str) -> int:
    # Si no existe el archivo, créalo con encabezados
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["id", "public_key"])

    # Cargar claves existentes
    with open(CSV_FILE, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["public_key"] == pem_key:
                return int(row["id"])  # Clave ya existe, devolver su ID

    # Si no se encontró, asignar un nuevo ID y registrar
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        new_id = get_next_id()
        writer.writerow([new_id, pem_key])
        return new_id 
        
def get_next_id() -> int:
    if not os.path.exists(CSV_FILE):
        return 1
    with open(CSV_FILE, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        ids = [int(row["id"]) for row in reader]
        return max(ids) + 1 if ids else 1
