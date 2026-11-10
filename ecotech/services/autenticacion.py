"""El acceso crea una sesión local asociada a una cuenta y a un empleado."""
from ecotech.repositories.oracle import OracleRepository
from ecotech import validation as v


class AutenticacionService:
    def __init__(self, repository=None):
        self.repository = repository if repository is not None else OracleRepository()

    def autenticar(self, nombre_usuario, contrasena):
        nombre_usuario = v.usuario(nombre_usuario)
        with self.repository.transaccion() as cursor:
            cuenta = self.repository.obtener_cuenta(cursor, nombre_usuario)
            if cuenta is not None and cuenta.autenticar(contrasena):
                return cuenta
        return None
