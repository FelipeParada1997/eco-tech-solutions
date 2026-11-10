"""Validaciones pequeñas que se reutilizan desde las clases y los servicios."""
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import re


def texto(valor, campo, maximo=150):
    if not isinstance(valor, str) or not valor.strip() or len(valor.strip()) > maximo:
        raise ValueError(f'{campo}: ingrese entre 1 y {maximo} caracteres.')
    return valor.strip()


def identificador(valor):
    if isinstance(valor, bool):
        raise ValueError('El ID debe ser un entero positivo.')
    try:
        numero = int(str(valor))
    except (ValueError, TypeError):
        raise ValueError('El ID debe ser un entero positivo.') from None
    if numero <= 0:
        raise ValueError('El ID debe ser un entero positivo.')
    return numero


def fecha(valor):
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    for formato in ('%d/%m/%Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(str(valor), formato).date()
        except ValueError:
            pass
    raise ValueError('Fecha inválida. Use DD/MM/AAAA.')


def cantidad(valor, campo, minimo=Decimal('0'), maximo=Decimal('999999999999.99')):
    try:
        numero = Decimal(str(valor))
    except InvalidOperation:
        raise ValueError(f'{campo}: ingrese un número válido.') from None
    if not numero.is_finite() or not minimo <= numero <= maximo:
        raise ValueError(f'{campo}: debe estar entre {minimo} y {maximo}.')
    if numero != numero.quantize(Decimal('0.01')):
        raise ValueError(f'{campo}: use como máximo dos decimales.')
    return numero


def correo(valor):
    valor = texto(valor, 'Correo', 254).casefold()
    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', valor):
        raise ValueError('Correo electrónico inválido.')
    return valor


def telefono(valor):
    valor = texto(valor, 'Teléfono', 50)
    if not re.fullmatch(r'[+\d ()-]{6,50}', valor):
        raise ValueError('Teléfono inválido: use números, espacios, +, - o paréntesis.')
    return valor


def usuario(valor):
    valor = texto(valor, 'Usuario', 50).casefold()
    if not re.fullmatch(r'[a-z0-9_]{3,50}', valor):
        raise ValueError('Usuario: use de 3 a 50 letras, números o guion bajo.')
    return valor
