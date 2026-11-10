"""Excepción de persistencia utilizada por la interfaz."""
from oracledb import Error as DatabaseError
__all__ = ['DatabaseError']
