"""Genera assets/banner.png para el README de GitHub con estética de estudio de ingeniería.

Diseño profesional sobrio: sin cuadrículas de neón de IA, sin píldoras de colores
tipo chicle, con tipografía nítida, paleta slate/obsidian y especificaciones unificadas.
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont


def generar_banner():
    ancho, alto = 1200, 400
    # Lienzo base obsidian/slate oscuro profesional (#0B0F19)
    base = Image.new("RGBA", (ancho, alto), (11, 15, 25, 255))

    # Gradiente sutil y elegante de estudio (luz suave proveniente del tercio izquierdo)
    luz = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
    luz_draw = ImageDraw.Draw(luz)

    # Resplandor muy suave y difuso (no neón agresivo)
    centro_x, centro_y = 280, 200
    for r in range(450, 50, -25):
        alpha = int((450 - r) * 0.05)
        luz_draw.ellipse(
            [centro_x - r, centro_y - r * 0.8, centro_x + r, centro_y + r * 0.8],
            fill=(30, 58, 110, alpha)
        )
    luz = luz.filter(ImageFilter.GaussianBlur(30))
    base = Image.alpha_composite(base, luz)
    draw = ImageDraw.Draw(base)

    # Marco exterior sutil tipo tarjeta de desarrollo (1px, #1E293B)
    draw.rounded_rectangle(
        [1, 1, ancho - 2, alto - 2],
        radius=14,
        outline=(30, 41, 59, 255),
        width=1,
    )

    # Cargar y posicionar el icono del proyecto
    ruta_icono = Path(__file__).resolve().parent.parent / "assets" / "gestor.png"
    if ruta_icono.exists():
        icono_orig = Image.open(ruta_icono).convert("RGBA")
        tam_icono = 164
        icono = icono_orig.resize((tam_icono, tam_icono), Image.Resampling.LANCZOS)

        # Sombra suave natural bajo el icono (drop shadow)
        sombra = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(sombra)
        ix, iy = 90, 118
        s_draw.rounded_rectangle(
            [ix + 4, iy + 12, ix + tam_icono - 4, iy + tam_icono + 14],
            radius=34,
            fill=(0, 0, 0, 140)
        )
        sombra = sombra.filter(ImageFilter.GaussianBlur(14))
        base = Image.alpha_composite(base, sombra)
        base.paste(icono, (ix, iy), icono)

    draw = ImageDraw.Draw(base)

    # Función auxiliar para fuentes de Windows con fallback seguro
    def obtener_fuente(nombres: list[str], tamano: int):
        for nombre in nombres:
            ruta = Path("C:/Windows/Fonts") / f"{nombre}.ttf"
            if ruta.exists():
                try:
                    return ImageFont.truetype(str(ruta), tamano)
                except Exception:
                    pass
        return ImageFont.load_default()

    fuente_eyebrow = obtener_fuente(["segoeuib", "arialbd"], 12)
    fuente_titulo = obtener_fuente(["segoeuib", "arialbd"], 54)
    fuente_version = obtener_fuente(["segoeuib", "arialbd"], 13)
    fuente_sub = obtener_fuente(["segoeui", "arial"], 20)
    fuente_pill = obtener_fuente(["consola", "segoeui", "arial"], 13)

    # Margen izquierdo alineado de texto
    x_texto = 300

    # 1. Eyebrow técnico (pequeño, sobrio, tracking espaciado)
    eyebrow = "OPEN SOURCE  ·  WINDOWS DESKTOP  ·  OFFLINE VAULT"
    draw.text((x_texto, 106), eyebrow, font=fuente_eyebrow, fill=(96, 165, 250, 230))

    # 2. Título principal "PassVault"
    draw.text((x_texto, 134), "PassVault", font=fuente_titulo, fill=(255, 255, 255, 255))

    # Badge de versión centrado matemáticamente con la altura visual del título
    bbox_tit = draw.textbbox((x_texto, 134), "PassVault", font=fuente_titulo)
    tit_top = bbox_tit[1]
    tit_bottom = bbox_tit[3]
    tit_center_y = (tit_top + tit_bottom) / 2

    alto_badge = 22
    pad_badge_x = 10
    bbox_ver = draw.textbbox((0, 0), "v2.0", font=fuente_version)
    ancho_badge = (bbox_ver[2] - bbox_ver[0]) + pad_badge_x * 2

    b_x = bbox_tit[2] + 14
    b_y = int(tit_center_y - alto_badge / 2)

    draw.rounded_rectangle(
        [b_x, b_y, b_x + ancho_badge, b_y + alto_badge],
        radius=alto_badge // 2,
        fill=(22, 34, 55, 255),
        outline=(56, 114, 195, 180),
        width=1,
    )
    draw.text(
        (b_x + ancho_badge / 2, b_y + alto_badge / 2),
        "v2.0",
        font=fuente_version,
        fill=(96, 195, 255, 255),
        anchor="mm",
    )

    # 3. Subtítulo conciso y claro
    subtitulo = "Lightweight local credential manager built with Python and Tkinter."
    draw.text((x_texto, 212), subtitulo, font=fuente_sub, fill=(148, 163, 184, 255))

    # 4. Ficha de especificaciones técnicas (badges unificados en paleta slate oscura)
    # Sin colores de chicle: diseño uniforme, técnico y profesional
    specs = [
        "AES-256-GCM",
        "Argon2id KDF",
        "100% Offline",
        "Zero Cloud",
        "No Telemetry",
    ]

    x_spec = x_texto
    y_spec = 262
    alto_spec = 30

    for item in specs:
        bbox = draw.textbbox((0, 0), item, font=fuente_pill)
        w_item = bbox[2] - bbox[0]
        pad_h = 14
        ancho_spec = w_item + pad_h * 2

        # Rectángulo con esquinas ligeramente redondeadas (estilo tag de desarrollo, no píldora de caramelo)
        rect = [x_spec, y_spec, x_spec + ancho_spec, y_spec + alto_spec]
        draw.rounded_rectangle(
            rect,
            radius=6,
            fill=(19, 26, 42, 255),
            outline=(45, 59, 85, 255),
            width=1,
        )

        cx = x_spec + ancho_spec / 2
        cy = y_spec + alto_spec / 2
        draw.text((cx, cy), item, font=fuente_pill, fill=(203, 213, 225, 255), anchor="mm")

        x_spec += ancho_spec + 10

    # Acento sutil en la parte superior: línea delgada degradada
    for x in range(ancho):
        dist = abs(x - ancho / 2) / (ancho / 2)
        alfa_linea = int(180 * (1 - dist ** 2))
        draw.point((x, 0), fill=(59, 130, 246, alfa_linea))

    destino = Path(__file__).resolve().parent.parent / "assets" / "banner.png"
    base.save(destino, "PNG", optimize=True)
    print(f"Banner generado exitosamente en {destino}")


if __name__ == "__main__":
    generar_banner()
