"""Alias compatible con el nombre escrito en el guion del ejercicio 6."""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).with_name("tcp_cliente6_oche_len.py")), run_name="__main__")
