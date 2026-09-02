"""Widgets y utilidades de interfaz reutilizables."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .escala import ALTO_MARCO, area_trabajo, px


def centrar(ventana, ancho: int | None = None, alto: int | None = None,
            padre=None) -> None:
    """Centra una ventana sobre su padre (o sobre la pantalla).

    ``ancho`` y ``alto`` se dan en medidas de diseño y se escalan según el DPI.
    La ventana se ajusta al área de trabajo, así que nunca queda con la parte
    de abajo (donde están los botones) escondida tras la barra de tareas.
    """
    ventana.update_idletasks()
    ancho = px(ancho) if ancho else ventana.winfo_width()
    alto = px(alto) if alto else ventana.winfo_height()

    izq, arriba, der, abajo = area_trabajo(ventana)
    marco = px(ALTO_MARCO)
    ancho = min(ancho, der - izq - px(16))
    alto = min(alto, abajo - arriba - marco - px(8))

    if padre is not None and padre.winfo_viewable():
        x = padre.winfo_rootx() + (padre.winfo_width() - ancho) // 2
        y = padre.winfo_rooty() + (padre.winfo_height() - alto) // 3
    else:
        x = izq + (der - izq - ancho) // 2
        y = arriba + (abajo - arriba - alto) // 3

    x = max(izq, min(x, der - ancho))
    y = max(arriba + marco, min(y, abajo - alto))
    ventana.geometry(f"{ancho}x{alto}+{x}+{y - marco}")


class BarraFortaleza(ttk.Frame):
    """Barra segmentada de 5 tramos que refleja la fortaleza de una contraseña."""

    SEGMENTOS = 5

    def __init__(self, padre, colores: dict, ancho: int = 240, alto: int = 7,
                 fondo: str | None = None, **kwargs):
        super().__init__(padre, **kwargs)
        self.colores = colores
        ancho, alto = px(ancho), px(alto)
        self.ancho = ancho
        self.alto = alto
        fondo = fondo or colores["panel"]
        self.canvas = tk.Canvas(self, width=ancho, height=alto, highlightthickness=0,
                                bd=0, bg=fondo)
        self.canvas.pack(fill="x")
        self._barras = []
        hueco = px(4)
        util = (ancho - hueco * (self.SEGMENTOS - 1)) / self.SEGMENTOS
        for i in range(self.SEGMENTOS):
            x0 = i * (util + hueco)
            self._barras.append(
                self.canvas.create_rectangle(x0, 0, x0 + util, alto,
                                             fill=colores["borde"], width=0)
            )

    def actualizar(self, puntaje: int, color: str) -> None:
        """``puntaje`` va de 0 a 4; se pintan ``puntaje + 1`` segmentos."""
        activos = 0 if puntaje < 0 else puntaje + 1
        for i, barra in enumerate(self._barras):
            self.canvas.itemconfig(barra, fill=color if i < activos else self.colores["borde"])

    def limpiar(self) -> None:
        for barra in self._barras:
            self.canvas.itemconfig(barra, fill=self.colores["borde"])


class CampoContrasena(ttk.Frame):
    """Entry de contraseña con botón de ojo, generador y copiar."""

    def __init__(self, padre, colores: dict, variable: tk.StringVar,
                 al_generar=None, al_copiar=None, ancho: int = 30, **kwargs):
        super().__init__(padre, **kwargs)
        self.colores = colores
        self.variable = variable
        self._visible = False

        self.entry = ttk.Entry(self, textvariable=variable, show="•", width=ancho,
                               font=("Consolas", 10))
        self.entry.pack(side="left", fill="x", expand=True)

        self.btn_ojo = ttk.Button(self, text="\U0001F441", width=3, style="Icono.TButton",
                                  command=self.alternar, takefocus=False)
        self.btn_ojo.pack(side="left", padx=(4, 0))
        Tooltip(self.btn_ojo, "Mostrar u ocultar")

        if al_copiar:
            btn = ttk.Button(self, text="\U0001F4CB", width=3, style="Icono.TButton",
                             command=al_copiar, takefocus=False)
            btn.pack(side="left", padx=(4, 0))
            Tooltip(btn, "Copiar al portapapeles")

        if al_generar:
            btn = ttk.Button(self, text="✨", width=3, style="Icono.TButton",
                             command=al_generar, takefocus=False)
            btn.pack(side="left", padx=(4, 0))
            Tooltip(btn, "Generar contraseña segura")

    def alternar(self) -> None:
        self._visible = not self._visible
        self.entry.configure(show="" if self._visible else "•")

    def mostrar(self, visible: bool) -> None:
        self._visible = visible
        self.entry.configure(show="" if visible else "•")


class Tooltip:
    """Globo de ayuda al pasar el cursor."""

    def __init__(self, widget, texto: str, retardo: int = 500):
        self.widget = widget
        self.texto = texto
        self.retardo = retardo
        self._id = None
        self._ventana = None
        widget.bind("<Enter>", self._programar, add="+")
        widget.bind("<Leave>", self._ocultar, add="+")
        widget.bind("<ButtonPress>", self._ocultar, add="+")

    def _programar(self, _evento=None):
        self._cancelar()
        self._id = self.widget.after(self.retardo, self._mostrar)

    def _cancelar(self):
        if self._id:
            self.widget.after_cancel(self._id)
            self._id = None

    def _mostrar(self):
        if self._ventana or not self.texto:
            return
        x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        self._ventana = tk.Toplevel(self.widget)
        self._ventana.wm_overrideredirect(True)
        etiqueta = tk.Label(self._ventana, text=self.texto, background="#2b2f3a",
                            foreground="#e7e9ee", relief="solid", borderwidth=1,
                            font=("Segoe UI", 8), padx=8, pady=4)
        etiqueta.pack()
        self._ventana.update_idletasks()
        ancho = self._ventana.winfo_width()
        self._ventana.wm_geometry(f"+{max(0, x - ancho // 2)}+{y}")

    def _ocultar(self, _evento=None):
        self._cancelar()
        if self._ventana:
            self._ventana.destroy()
            self._ventana = None


class DialogoBase(tk.Toplevel):
    """Ventana modal con título, cuerpo y cierre con Escape."""

    def __init__(self, padre, colores: dict, titulo: str, ancho: int = 480,
                 alto: int = 360, redimensionable: bool = False):
        super().__init__(padre)
        self.colores = colores
        self.resultado = None
        self.title(titulo)
        self.configure(bg=colores["fondo"])
        self.resizable(redimensionable, redimensionable)

        # transient() sobre un padre oculto esconde también este diálogo, así
        # que solo se enlaza cuando el padre se está viendo.
        if padre is not None and padre.winfo_viewable():
            self.transient(padre)

        self.contenedor = ttk.Frame(self, padding=20)
        self.contenedor.pack(fill="both", expand=True)

        self.bind("<Escape>", lambda _e: self.cancelar())
        self.protocol("WM_DELETE_WINDOW", self.cancelar)
        centrar(self, ancho, alto, padre)

    def hacer_modal(self) -> None:
        self.deiconify()
        self.lift()
        self.grab_set()
        self.focus_force()
        self.wait_window(self)

    def cancelar(self) -> None:
        self.resultado = None
        self.destroy()
