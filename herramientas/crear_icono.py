"""Genera assets/gestor.ico (el icono del programa y del .exe).

Se ejecuta una sola vez; el .ico queda versionado junto al proyecto.
    python herramientas/crear_icono.py
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

LADO = 512
FONDO_A = (36, 63, 148)     # azul profundo
FONDO_B = (79, 125, 243)    # azul del acento
CANDADO = (255, 255, 255)
OJO = (36, 63, 148)


def degradado(lado: int) -> Image.Image:
    base = Image.new("RGB", (lado, lado), FONDO_A)
    pintor = ImageDraw.Draw(base)
    for y in range(lado):
        t = y / (lado - 1)
        color = tuple(int(FONDO_A[i] + (FONDO_B[i] - FONDO_A[i]) * t) for i in range(3))
        pintor.line([(0, y), (lado, y)], fill=color)
    return base


def crear() -> Image.Image:
    lado = LADO
    fondo = degradado(lado).convert("RGBA")

    # Esquinas redondeadas al estilo de los iconos modernos de Windows.
    mascara = Image.new("L", (lado, lado), 0)
    ImageDraw.Draw(mascara).rounded_rectangle([0, 0, lado - 1, lado - 1],
                                              radius=int(lado * 0.22), fill=255)
    icono = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    icono.paste(fondo, (0, 0), mascara)

    pintor = ImageDraw.Draw(icono)

    centro_x = lado // 2
    grosor = int(lado * 0.075)
    radio_arco = int(lado * 0.16)
    centro_arco_y = int(lado * 0.40)
    tope_cuerpo = int(lado * 0.45)

    # Arco del candado: media circunferencia por encima del cuerpo.
    pintor.arc([centro_x - radio_arco, centro_arco_y - radio_arco,
                centro_x + radio_arco, centro_arco_y + radio_arco],
               start=180, end=360, fill=CANDADO, width=grosor)
    for x in (centro_x - radio_arco, centro_x + radio_arco):
        pintor.line([(x, centro_arco_y), (x, tope_cuerpo + grosor)],
                    fill=CANDADO, width=grosor)

    # Cuerpo del candado.
    pintor.rounded_rectangle([int(lado * 0.20), tope_cuerpo,
                              int(lado * 0.80), int(lado * 0.83)],
                             radius=int(lado * 0.10), fill=CANDADO)

    # Ojo de la cerradura.
    radio = int(lado * 0.062)
    cy = int(lado * 0.615)
    pintor.ellipse([centro_x - radio, cy - radio, centro_x + radio, cy + radio],
                   fill=OJO)
    pintor.rounded_rectangle([centro_x - int(radio * 0.42), cy,
                              centro_x + int(radio * 0.42), cy + int(lado * 0.10)],
                             radius=int(radio * 0.42), fill=OJO)
    return icono


def main() -> None:
    destino = Path(__file__).resolve().parent.parent / "assets"
    destino.mkdir(exist_ok=True)
    icono = crear()
    icono.save(destino / "gestor.png")
    icono.save(destino / "gestor.ico",
               sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64),
                      (128, 128), (256, 256)])
    print(f"Icono creado en {destino / 'gestor.ico'}")


if __name__ == "__main__":
    main()
