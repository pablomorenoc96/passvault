"""Soporte de pantallas con escalado (DPI) de Windows.

Sin esto, Windows agranda la ventana como si fuera una imagen y todo el texto
se ve borroso en monitores al 125%, 150% o 4K. Al declararnos "DPI aware",
Windows nos entrega píxeles reales y Tk dibuja las fuentes nitidas; a cambio,
cualquier medida fija en píxeles hay que multiplicarla por ``px()``.
"""
from __future__ import annotations

import sys

_FACTOR = 1.0


def activar() -> float:
    """Declara la app consciente de DPI. Llamar ANTES de crear la ventana Tk."""
    global _FACTOR
    if sys.platform != "win32":
        return _FACTOR

    import ctypes

    try:  # Windows 8.1 en adelante
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:  # Vista - Windows 8
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            return _FACTOR

    try:
        dpi = ctypes.windll.user32.GetDpiForSystem()
        _FACTOR = max(1.0, dpi / 96.0)
    except Exception:
        _FACTOR = 1.0
    return _FACTOR


def factor() -> float:
    return _FACTOR


def area_trabajo(ventana) -> tuple[int, int, int, int]:
    """Rectángulo utilizable de la pantalla: ``(izq, arriba, der, abajo)``.

    Descuenta la barra de tareas. Sin esto, una ventana alta se coloca con su
    parte de abajo (los botones) escondida detrás de la barra de tareas.
    """
    ancho = ventana.winfo_screenwidth()
    alto = ventana.winfo_screenheight()

    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes

        rect = wintypes.RECT()
        SPI_GETWORKAREA = 0x0030
        try:
            if ctypes.windll.user32.SystemParametersInfoW(
                    SPI_GETWORKAREA, 0, ctypes.byref(rect), 0):
                if rect.right > rect.left and rect.bottom > rect.top:
                    return rect.left, rect.top, rect.right, rect.bottom
        except Exception:
            pass

    return 0, 0, ancho, alto


# Alto aproximado de la barra de título de una ventana de Windows.
ALTO_MARCO = 38


def px(valor: float) -> int:
    """Convierte una medida de diseño (a 96 dpi) en píxeles reales."""
    return int(round(valor * _FACTOR))
