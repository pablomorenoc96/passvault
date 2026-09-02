"""Genera assets/banner.png para el README de GitHub y Social Preview."""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def generar_banner():
    ancho, alto = 1200, 420
    base = Image.new("RGBA", (ancho, alto), (15, 20, 32, 255))
    draw = ImageDraw.Draw(base)

    # Fondo degradado horizontal suave
    c_izq = (12, 17, 29)
    c_der = (24, 34, 58)
    for x in range(ancho):
        t = x / (ancho - 1)
        r = int(c_izq[0] + (c_der[0] - c_izq[0]) * t)
        g = int(c_izq[1] + (c_der[1] - c_izq[1]) * t)
        b = int(c_izq[2] + (c_der[2] - c_izq[2]) * t)
        draw.line([(x, 0), (x, alto)], fill=(r, g, b, 255))

    # Rejilla sutil de fondo
    linea_color = (255, 255, 255, 8)
    for x in range(0, ancho, 40):
        draw.line([(x, 0), (x, alto)], fill=linea_color)
    for y in range(0, alto, 40):
        draw.line([(0, y), (ancho, y)], fill=linea_color)

    # Resplandor azul detrás del icono
    glow = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    for radio in range(160, 40, -10):
        alfa = int((160 - radio) * 0.4)
        glow_draw.ellipse([210 - radio, 210 - radio, 210 + radio, 210 + radio],
                          fill=(56, 114, 245, alfa))
    base = Image.alpha_composite(base, glow)
    draw = ImageDraw.Draw(base)

    # Pegar icono del proyecto
    ruta_icono = Path(__file__).resolve().parent.parent / "assets" / "gestor.png"
    if ruta_icono.exists():
        icono = Image.open(ruta_icono).convert("RGBA")
        icono = icono.resize((190, 190), Image.Resampling.LANCZOS)
        base.paste(icono, (115, 115), icono)

    # Intentar cargar fuentes del sistema o usar default
    def obtener_fuente(nombre, tamano):
        rutas = [
            Path("C:/Windows/Fonts") / f"{nombre}.ttf",
            Path("C:/Windows/Fonts/segoeuib.ttf"),
            Path("C:/Windows/Fonts/arialbd.ttf"),
        ]
        for r in rutas:
            if r.exists():
                try:
                    return ImageFont.truetype(str(r), tamano)
                except Exception:
                    pass
        return ImageFont.load_default()

    fuente_titulo = obtener_fuente("segoeuib", 66)
    fuente_sub = obtener_fuente("segoeui", 22)
    fuente_pill = obtener_fuente("segoeui", 14)

    # Coordenada X común para alineación perfecta a la izquierda
    x_comun = 360

    # Título "PassVault"
    draw.text((x_comun, 108), "PassVault", font=fuente_titulo, fill=(255, 255, 255, 255))

    # Badge de versión alineado al título
    bbox_titulo = draw.textbbox((x_comun, 108), "PassVault", font=fuente_titulo)
    draw.text((bbox_titulo[2] + 16, 126), "v2.0", font=obtener_fuente("segoeuib", 15),
              fill=(86, 154, 255, 255))

    # Subtítulo con alineación exacta
    draw.text((x_comun, 192), "Secure, Lightweight & Offline Desktop Password Manager",
              font=fuente_sub, fill=(185, 200, 225, 255))

    # Pills / Badges destacados (altura fija idéntica de 32px y radio completo)
    pills = [
        ("AES-256-GCM", (35, 65, 120)),
        ("Argon2id KDF", (25, 80, 100)),
        ("100% Offline", (30, 95, 55)),
        ("Zero Cloud", (75, 42, 105)),
        ("Windows", (40, 52, 75)),
    ]

    x_pill = x_comun
    y_pill = 244
    alto_pill = 32

    for texto, color_bg in pills:
        bbox = draw.textbbox((0, 0), texto, font=fuente_pill)
        w_txt = bbox[2] - bbox[0]
        pad_x = 16
        ancho_pill = w_txt + pad_x * 2

        pill_rect = [x_pill, y_pill, x_pill + ancho_pill, y_pill + alto_pill]
        # Borde y relleno con esquinas redondeadas
        draw.rounded_rectangle(pill_rect, radius=alto_pill // 2, fill=color_bg,
                               outline=(255, 255, 255, 50), width=1)

        # Centrado geométrico absoluto (middle-middle)
        cx = x_pill + ancho_pill / 2
        cy = y_pill + alto_pill / 2
        draw.text((cx, cy), texto, font=fuente_pill, fill=(240, 245, 255, 245),
                  anchor="mm")

        x_pill += ancho_pill + 10

    # Línea decorativa inferior
    for x in range(ancho):
        alfa = int(255 * (1 - abs(x - ancho / 2) / (ancho / 2)))
        draw.point((x, alto - 2), fill=(56, 125, 245, alfa))
        draw.point((x, alto - 1), fill=(30, 80, 200, alfa // 2))

    destino = Path(__file__).resolve().parent.parent / "assets" / "banner.png"
    base.save(destino, "PNG")
    print(f"Banner generado exitosamente en {destino}")


if __name__ == "__main__":
    generar_banner()
