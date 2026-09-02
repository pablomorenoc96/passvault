"""Punto de entrada del Gestor de Contrasenas.

Ejecutar con:  python gestor_passwords.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Permite ejecutar el script desde cualquier carpeta.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from gestorpass.app import main  # noqa: E402

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - red de seguridad de la GUI
        import traceback
        from tkinter import messagebox

        traceback.print_exc()
        try:
            messagebox.showerror("Gestor de Contrasenas",
                                 f"Error inesperado:\n\n{exc}")
        except Exception:
            pass
        sys.exit(1)
