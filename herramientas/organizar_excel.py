"""Herramienta para ordenar y estructurar listas desorganizadas de contraseñas en Excel.

Uso:
    python herramientas/organizar_excel.py [archivo_origen.xlsx] [archivo_salida.xlsx]
"""
from __future__ import annotations

import os
import sys
import pandas as pd


def limpiar_texto(txt) -> str:
    if not isinstance(txt, str):
        return str(txt)
    prefijos = [
        "Usuario:", "User:", "Usuario ", "Contraseña:",
        "Password:", "Contrasena:", "Contrasena "
    ]
    for p in prefijos:
        if txt.lower().startswith(p.lower()):
            return txt[len(p):].strip()
    return txt


def organizar_y_guardar(origen: str = "cuentas_desorganizadas.xlsx",
                        salida: str = "cuentas_organizadas.xlsx") -> None:
    print(f"Leyendo '{origen}'...")

    if not os.path.exists(origen):
        print(f"ERROR: No se encuentra el archivo '{origen}'.")
        print("Indica un archivo existente como argumento:")
        print("  python herramientas/organizar_excel.py mi_archivo.xlsx")
        return

    try:
        df = pd.read_excel(origen, header=None)
    except Exception as e:
        print(f"Error al leer Excel: {e}")
        return

    raw_data = []
    for i in range(min(3, df.shape[1])):
        col_data = df.iloc[:, i].tolist()
        if pd.Series(col_data).dropna().count() > 10:
            raw_data = col_data
            break

    if not raw_data:
        print("No se encontró una columna con suficientes datos.")
        return

    records = []
    current_block = []

    for item in raw_data:
        if pd.isna(item) or str(item).strip() == "":
            if current_block:
                site = current_block[0]
                user = ""
                pw = ""
                if len(current_block) >= 3:
                    user = current_block[1]
                    pw = current_block[2]
                elif len(current_block) == 2:
                    segundo = str(current_block[1])
                    if "@" in segundo:
                        user = segundo
                    else:
                        pw = segundo

                records.append([site, limpiar_texto(user), limpiar_texto(pw)])
                current_block = []
        else:
            current_block.append(item)

    if current_block:
        site = current_block[0]
        user = "" if len(current_block) < 2 else current_block[1]
        pw = "" if len(current_block) < 3 else current_block[2]
        records.append([site, limpiar_texto(user), limpiar_texto(pw)])

    df_nuevo = pd.DataFrame(records, columns=["Sitio", "Usuario", "Contrasena"])
    df_nuevo.to_excel(salida, index=False)
    print(f"\n¡Éxito! Archivo '{salida}' creado con {len(df_nuevo)} cuentas.")


if __name__ == "__main__":
    archivo_in = sys.argv[1] if len(sys.argv) > 1 else "cuentas_desorganizadas.xlsx"
    archivo_out = sys.argv[2] if len(sys.argv) > 2 else "cuentas_organizadas.xlsx"
    organizar_y_guardar(archivo_in, archivo_out)
