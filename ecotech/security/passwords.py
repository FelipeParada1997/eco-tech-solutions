"""PBKDF2 con sal aleatoria. Conserva la verificación del formato anterior."""
import hashlib
import hmac
import secrets


def validar_password(password):
    if not isinstance(password, str) or not 12 <= len(password) <= 128:
        raise ValueError('La contraseña debe tener de 12 a 128 caracteres.')
    if not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
        raise ValueError('La contraseña debe incluir letras y números.')


def generar_hash(contrasena, sal):
    # Formato original: solo para comprobar cuentas antiguas, no para altas nuevas.
    return hashlib.pbkdf2_hmac('sha256', contrasena.encode(), sal.encode(), 200000).hex()


def crear_hash(password):
    validar_password(password)
    sal = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), sal.encode(), 600000).hex()
    return f'pbkdf2_sha256$600000${sal}${digest}'


def verificar_password(password, guardado):
    if not isinstance(password, str) or len(password) > 128 or not isinstance(guardado, str):
        return False
    try:
        if '$' not in guardado:
            sal, esperado = guardado.split(':', 1)
            return hmac.compare_digest(generar_hash(password, sal), esperado)
        algoritmo, vueltas, sal, esperado = guardado.split('$')
        if algoritmo != 'pbkdf2_sha256' or not 100000 <= int(vueltas) <= 2000000:
            return False
        actual = hashlib.pbkdf2_hmac('sha256', password.encode(), sal.encode(), int(vueltas)).hex()
        return hmac.compare_digest(actual, esperado)
    except (ValueError, TypeError):
        return False
