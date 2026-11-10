"""Configuración resuelta respecto del proyecto, independiente del directorio actual."""
from pathlib import Path
from dotenv import load_dotenv
import os
ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env', override=False, interpolate=False)
USUARIO = os.getenv('ORACLE_USER')
CONTRASENIA = os.getenv('ORACLE_PASSWORD')
DSN = os.getenv('ORACLE_DSN')
