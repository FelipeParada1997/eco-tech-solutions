"""Una clave Fernet externa cifra el conjunto de datos personales de cada empleado."""
import json
import os
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken
from ecotech.config import ROOT


def ruta_clave():
    ruta = Path(os.getenv('ECOTECH_KEY_FILE', 'datos/clave.key')).expanduser()
    return ruta if ruta.is_absolute() else ROOT / ruta


def crear_clave(ruta=None):
    ruta = Path(ruta) if ruta else ruta_clave()
    ruta.parent.mkdir(parents=True, exist_ok=True)
    # Nunca reemplazar una clave: se perdería acceso a los datos ya cifrados.
    fd = os.open(ruta, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as archivo:
        archivo.write(Fernet.generate_key())
    return ruta


class Cifrado:
    def __init__(self, clave=None):
        try:
            self._fernet = Fernet(clave if clave is not None else ruta_clave().read_bytes().strip())
        except (OSError, ValueError, TypeError):
            raise ValueError('No se pudo cargar la clave de cifrado. Configure ECOTECH_KEY_FILE; no reemplace claves de una base existente.') from None

    def cifrar(self, datos):
        contenido = json.dumps(datos, ensure_ascii=False).encode('utf-8')
        return self._fernet.encrypt(contenido).decode('ascii')

    def descifrar(self, valor):
        try:
            if hasattr(valor, 'read'):  # Oracle puede devolver un objeto CLOB.
                valor = valor.read()
            return json.loads(self._fernet.decrypt(valor.encode('ascii')))
        except (InvalidToken, ValueError, TypeError, AttributeError):
            raise ValueError('No se pudieron descifrar los datos. Revise la clave y su respaldo.') from None
