"""Paleta de colores y estilos ttk de la aplicación."""
from __future__ import annotations

import tkinter.font as tkfont
from tkinter import ttk

from .escala import px

PALETAS = {
    "oscuro": {
        "fondo": "#14161b",
        "panel": "#1c1f26",
        "panel_alt": "#242832",
        "borde": "#333844",
        "texto": "#e7e9ee",
        "texto_tenue": "#98a0ad",
        "campo": "#0f1116",
        "acento": "#4f7df3",
        "acento_hover": "#6b93ff",
        "acento_texto": "#ffffff",
        "seleccion": "#2b3a5c",
        "peligro": "#e5484d",
        "peligro_hover": "#f0666a",
        "exito": "#3fa45b",
        "aviso": "#f5a524",
        "fila_alt": "#1f232b",
    },
    "claro": {
        "fondo": "#eef0f4",
        "panel": "#ffffff",
        "panel_alt": "#f5f6f9",
        "borde": "#d3d7e0",
        "texto": "#1b1f27",
        "texto_tenue": "#6a7280",
        "campo": "#ffffff",
        "acento": "#2f62e0",
        "acento_hover": "#4a79ef",
        "acento_texto": "#ffffff",
        "seleccion": "#d6e2ff",
        "peligro": "#d13b40",
        "peligro_hover": "#e04f54",
        "exito": "#2f8c4a",
        "aviso": "#c07d0a",
        "fila_alt": "#f7f8fb",
    },
}

FUENTE = "Segoe UI"


def fuentes() -> dict:
    return {
        "normal": (FUENTE, 10),
        "pequena": (FUENTE, 9),
        "mini": (FUENTE, 8),
        "negrita": (FUENTE, 10, "bold"),
        "titulo": (FUENTE, 16, "bold"),
        "subtitulo": (FUENTE, 12, "bold"),
        "mono": ("Consolas", 11),
        "mono_grande": ("Consolas", 15, "bold"),
    }


def aplicar(root, nombre: str) -> dict:
    """Aplica la paleta indicada a todos los estilos ttk. Devuelve la paleta."""
    c = PALETAS.get(nombre, PALETAS["oscuro"])
    f = fuentes()

    estilo = ttk.Style(root)
    try:
        estilo.theme_use("clam")  # el único tema ttk realmente personalizable
    except Exception:
        pass

    root.configure(bg=c["fondo"])
    for nombre_fuente in ("TkDefaultFont", "TkTextFont", "TkMenuFont"):
        try:
            tkfont.nametofont(nombre_fuente).configure(family=FUENTE, size=10)
        except Exception:
            pass

    estilo.configure(".", background=c["fondo"], foreground=c["texto"],
                     fieldbackground=c["campo"], bordercolor=c["borde"],
                     font=f["normal"])

    # --- contenedores -------------------------------------------------------
    estilo.configure("TFrame", background=c["fondo"])
    estilo.configure("Panel.TFrame", background=c["panel"])
    estilo.configure("PanelAlt.TFrame", background=c["panel_alt"])
    estilo.configure("Barra.TFrame", background=c["panel"])

    # --- etiquetas ----------------------------------------------------------
    estilo.configure("TLabel", background=c["fondo"], foreground=c["texto"])
    estilo.configure("Panel.TLabel", background=c["panel"], foreground=c["texto"])
    estilo.configure("Tenue.TLabel", background=c["fondo"], foreground=c["texto_tenue"],
                     font=f["pequena"])
    estilo.configure("PanelTenue.TLabel", background=c["panel"],
                     foreground=c["texto_tenue"], font=f["pequena"])
    estilo.configure("Titulo.TLabel", background=c["fondo"], foreground=c["texto"],
                     font=f["titulo"])
    estilo.configure("PanelTitulo.TLabel", background=c["panel"], foreground=c["texto"],
                     font=f["subtitulo"])
    estilo.configure("Seccion.TLabel", background=c["panel"], foreground=c["texto_tenue"],
                     font=(FUENTE, 8, "bold"))
    estilo.configure("Mono.TLabel", background=c["panel"], foreground=c["texto"],
                     font=f["mono"])

    # --- botones ------------------------------------------------------------
    estilo.configure("TButton", background=c["panel_alt"], foreground=c["texto"],
                     bordercolor=c["borde"], focuscolor=c["acento"],
                     padding=(px(12), px(7)), relief="flat", font=f["normal"])
    estilo.map("TButton",
               background=[("pressed", c["borde"]), ("active", c["borde"]),
                           ("disabled", c["panel"])],
               foreground=[("disabled", c["texto_tenue"])])

    estilo.configure("Acento.TButton", background=c["acento"],
                     foreground=c["acento_texto"], font=f["negrita"])
    estilo.map("Acento.TButton",
               background=[("pressed", c["acento"]), ("active", c["acento_hover"]),
                           ("disabled", c["borde"])])

    estilo.configure("Peligro.TButton", background=c["peligro"], foreground="#ffffff")
    estilo.map("Peligro.TButton",
               background=[("active", c["peligro_hover"]), ("disabled", c["borde"])])

    estilo.configure("Panel.TButton", background=c["panel"], foreground=c["texto"])
    estilo.map("Panel.TButton", background=[("active", c["panel_alt"])])

    estilo.configure("Icono.TButton", padding=(px(7), px(4)), background=c["panel"],
                     foreground=c["texto_tenue"])
    estilo.map("Icono.TButton", background=[("active", c["panel_alt"])],
               foreground=[("active", c["acento"])])

    estilo.configure("Lateral.TButton", background=c["panel"], foreground=c["texto"],
                     padding=(px(10), px(8)), anchor="w", font=f["normal"])
    estilo.map("Lateral.TButton", background=[("active", c["panel_alt"])])

    estilo.configure("LateralActivo.TButton", background=c["seleccion"],
                     foreground=c["texto"], padding=(px(10), px(8)), anchor="w",
                     font=f["negrita"])
    estilo.map("LateralActivo.TButton", background=[("active", c["seleccion"])])

    # --- campos -------------------------------------------------------------
    estilo.configure("TEntry", fieldbackground=c["campo"], foreground=c["texto"],
                     insertcolor=c["texto"], bordercolor=c["borde"],
                     lightcolor=c["borde"], darkcolor=c["borde"], padding=px(6))
    estilo.map("TEntry", bordercolor=[("focus", c["acento"])],
               lightcolor=[("focus", c["acento"])])

    estilo.configure("Busqueda.TEntry", fieldbackground=c["panel_alt"], padding=px(7))
    estilo.map("Busqueda.TEntry", bordercolor=[("focus", c["acento"])])

    estilo.configure("TCombobox", fieldbackground=c["campo"], background=c["panel_alt"],
                     foreground=c["texto"], arrowcolor=c["texto_tenue"],
                     bordercolor=c["borde"], padding=px(5))
    estilo.map("TCombobox", fieldbackground=[("readonly", c["campo"])],
               selectbackground=[("readonly", c["campo"])],
               selectforeground=[("readonly", c["texto"])])

    estilo.configure("TCheckbutton", background=c["panel"], foreground=c["texto"],
                     indicatorcolor=c["campo"], focuscolor=c["panel"])
    estilo.map("TCheckbutton",
               background=[("active", c["panel"])],
               indicatorcolor=[("selected", c["acento"]), ("active", c["panel_alt"])])

    estilo.configure("Fondo.TCheckbutton", background=c["fondo"], foreground=c["texto"])
    estilo.map("Fondo.TCheckbutton", background=[("active", c["fondo"])],
               indicatorcolor=[("selected", c["acento"])])

    estilo.configure("TRadiobutton", background=c["panel"], foreground=c["texto"])
    estilo.map("TRadiobutton", background=[("active", c["panel"])],
               indicatorcolor=[("selected", c["acento"])])

    estilo.configure("Horizontal.TScale", background=c["panel"],
                     troughcolor=c["campo"], bordercolor=c["borde"])

    estilo.configure("TSeparator", background=c["borde"])

    # --- tabla --------------------------------------------------------------
    estilo.configure("Treeview", background=c["panel"], fieldbackground=c["panel"],
                     foreground=c["texto"], bordercolor=c["panel"], borderwidth=0,
                     lightcolor=c["panel"], darkcolor=c["panel"], relief="flat",
                     rowheight=px(30), font=f["normal"])
    estilo.map("Treeview", background=[("selected", c["seleccion"])],
               foreground=[("selected", c["texto"])])
    estilo.configure("Treeview.Heading", background=c["panel_alt"],
                     foreground=c["texto_tenue"], relief="flat",
                     padding=(px(8), px(8)), font=(FUENTE, 9, "bold"))
    estilo.map("Treeview.Heading", background=[("active", c["borde"])])

    estilo.configure("Vertical.TScrollbar", background=c["panel_alt"],
                     troughcolor=c["fondo"], bordercolor=c["fondo"],
                     arrowcolor=c["texto_tenue"], relief="flat")
    estilo.map("Vertical.TScrollbar", background=[("active", c["borde"])])

    estilo.configure("TNotebook", background=c["fondo"], bordercolor=c["borde"])
    estilo.configure("TNotebook.Tab", background=c["panel_alt"], foreground=c["texto_tenue"],
                     padding=(px(16), px(8)), font=f["normal"])
    estilo.map("TNotebook.Tab", background=[("selected", c["panel"])],
               foreground=[("selected", c["texto"])])

    estilo.configure("TLabelframe", background=c["panel"], bordercolor=c["borde"],
                     relief="solid", borderwidth=1)
    estilo.configure("TLabelframe.Label", background=c["panel"],
                     foreground=c["texto_tenue"], font=(FUENTE, 9, "bold"))

    return c
