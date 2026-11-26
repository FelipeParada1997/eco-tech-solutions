"""Excepción de persistencia utilizada por la interfaz."""
from sqlite3 import Error as DatabaseError
__all__ = ['DatabaseError']
