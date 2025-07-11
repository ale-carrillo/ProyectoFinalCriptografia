# Protocolo de Comunicación Segura

Este proyecto implementa un protocolo de comunicación segura entre tres entidades:

- `RA.py`: Autoridad de registro
- `trustedApp.py`: Aplicación confiable
- `smartDevice.py`: Dispositivo inteligente

---

## Instrucciones de instalación y ejecución

### 1. Clonar o descargar el repositorio

Descarga este proyecto en la máquina local y ubica la terminal dentro del directorio del proyecto.

---

### 2. Crear entorno virtual, instalar dependencias y ejecutar script principal

#### Para Windows:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run_all.py --sistema windows
```
En caso de obtener un error al tratar de ejecutar el script activate, utilice los siguientes comandos:
```bash
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\venv\Scripts\activate
```


#### Para Linux y macOS:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

```bash
python run_all.py --sistema linux
```
#### ó
```bash
python run_all.py --sistema macos
```
