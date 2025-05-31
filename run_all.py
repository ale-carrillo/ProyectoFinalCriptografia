import subprocess
import time
import argparse
import os

# Configuraciòn argumento de lìnea de comandos, se debe de especificar el sistema operativo con el que se trabajará
parser = argparse.ArgumentParser(description="Ejecución del protocolo de comunicación acuerdo con el sistema operativo seleccionado")
parser.add_argument("--sistema", type=str, choices=["windows", "linux", "macos"], required=True)
args = parser.parse_args()

# En caso de usar Windows
if args.sistema == "windows":
    # Abrir RA
    subprocess.Popen(['start', 'cmd', '/k', 'venv\\Scripts\\activate && python RA.py'], shell=True)
    time.sleep(3)

    # Abrir Trusted App
    subprocess.Popen(['start', 'cmd', '/k', 'venv\\Scripts\\activate && python trustedApp.py'], shell=True)
    time.sleep(3)

    # Abrir Smart Device
    subprocess.Popen(['start', 'cmd', '/k', 'venv\\Scripts\\activate && python smartDevice.py'], shell=True)
    time.sleep(3)

    print("\n\tPuedes cerrar las ventanas cuando terminen o presionar Alt+F4.\n\n")

# En caso de usar Linux
elif args.sistema == "linux":
    print(f"Instalación de gnome-terminal para abrir múltiples ventanas. Favor de ingresar la contraseña solicitada por la terminal.")
    os.system("sudo apt update")
    os.system("sudo apt install -y gnome-terminal")
    
    subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', 'source venv/bin/activate && python RA.py; exec bash'])
    time.sleep(3)
    
    subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', 'source venv/bin/activate && python trustedApp.py; exec bash'])
    time.sleep(3)

    subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', 'source venv/bin/activate && python smartDevice.py; exec bash'])
    time.sleep(3)

    print("\n\tPuedes cerrar las ventanas cuando terminen o presionar Ctrl+D.\n\n")

# En caso de usar macOS
elif args.sistema == "macos":
    directorioActual = os.getcwd()
    
    subprocess.Popen(['osascript', '-e', f'tell application "Terminal" to do script "cd \\"{directorioActual}\\"; source venv/bin/activate; python3 RA.py"'])
    time.sleep(3)

    subprocess.Popen(['osascript', '-e', f'tell application "Terminal" to do script "cd \\"{directorioActual}\\"; source venv/bin/activate; python3 trustedApp.py"'])
    time.sleep(3)

    subprocess.Popen(['osascript', '-e', f'tell application "Terminal" to do script "cd \\"{directorioActual}\\"; source venv/bin/activate; python3 smartDevice.py"'])
    time.sleep(3)

    print("\n\tPuedes cerrar las ventanas cuando terminen o presionar Cmd+W.\n\n")
