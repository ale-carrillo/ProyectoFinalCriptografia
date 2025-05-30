import subprocess
import time

# Abrir RA 
subprocess.Popen(['start', 'cmd', '/k', 'python RA.py'], shell=True)
time.sleep(3)

# Abrir Trusted App 
subprocess.Popen(['start', 'cmd', '/k', 'python trustedApp.py'], shell=True)
time.sleep(3)

# Abrir Smart Device 
subprocess.Popen(['start', 'cmd', '/k', 'python smartDevice.py'], shell=True)
time.sleep(3)

print("\n\tPuede cerrar las ventanas cuando terminen o presionar Ctrl+C.\n\n")
