"""Formulario para crear o editar una entrada de la bóveda."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from . import fortaleza
from .boveda import Entrada
from .escala import px
from .ui_generador import DialogoGenerador
from .widgets import BarraFortaleza, CampoContrasena, DialogoBase


class DialogoEntrada(DialogoBase):
    """Alta y edición. Deja en ``self.resultado`` un dict con los campos."""

    def __init__(self, padre, colores: dict, prefs: dict, categorias: list[str],
                 entrada: Entrada | None = None, al_copiar=None):
        titulo = "Editar entrada" if entrada else "Nueva entrada"
        super().__init__(padre, colores, titulo, 520, 730)
        self.prefs = prefs
        self.entrada = entrada
        self.al_copiar = al_copiar
        self.categorias = categorias

        self.var_sitio = tk.StringVar(value=entrada.sitio if entrada else "")
        self.var_usuario = tk.StringVar(value=entrada.usuario if entrada else "")
        self.var_pass = tk.StringVar(value=entrada.contrasena if entrada else "")
        self.var_url = tk.StringVar(value=entrada.url if entrada else "")
        self.var_categoria = tk.StringVar(value=entrada.categoria if entrada else "")
        self.var_favorito = tk.BooleanVar(value=entrada.favorito if entrada else False)

        self._construir(titulo)
        self.var_pass.trace_add("write", self._medir)
        self._medir()
        self.after(120, lambda: self.entry_sitio.focus_set())

    # ------------------------------------------------------------------ interfaz
    def _construir(self, titulo: str) -> None:
        c = self.colores
        raiz = self.contenedor

        ttk.Label(raiz, text=titulo, style="Titulo.TLabel").pack(anchor="w", pady=(0, 16))

        # Los botones se reservan su sitio abajo ANTES que el formulario: así
        # nunca quedan fuera de la ventana aunque el contenido crezca.
        acciones = ttk.Frame(raiz)
        acciones.pack(side="bottom", fill="x", pady=(16, 0))

        caja = ttk.Frame(raiz, style="Panel.TFrame", padding=16)
        caja.pack(fill="both", expand=True)

        def etiqueta(texto, arriba=12):
            ttk.Label(caja, text=texto, style="Seccion.TLabel").pack(anchor="w",
                                                                    pady=(arriba, 4))

        etiqueta("SITIO O SERVICIO *", 0)
        self.entry_sitio = ttk.Entry(caja, textvariable=self.var_sitio)
        self.entry_sitio.pack(fill="x", ipady=2)

        etiqueta("USUARIO O CORREO")
        ttk.Entry(caja, textvariable=self.var_usuario).pack(fill="x", ipady=2)

        etiqueta("CONTRASEÑA")
        self.campo_pass = CampoContrasena(
            caja, c, self.var_pass,
            al_generar=self._abrir_generador,
            al_copiar=(lambda: self.al_copiar(self.var_pass.get())) if self.al_copiar else None,
            style="Panel.TFrame")
        self.campo_pass.pack(fill="x")

        self.barra = BarraFortaleza(caja, c, ancho=420, fondo=c["panel"],
                                    style="Panel.TFrame")
        self.barra.pack(fill="x", pady=(8, 3))
        self.lbl_fuerza = ttk.Label(caja, text="", style="PanelTenue.TLabel",
                                    wraplength=px(430), justify="left")
        self.lbl_fuerza.pack(anchor="w")

        etiqueta("SITIO WEB (URL)")
        ttk.Entry(caja, textvariable=self.var_url).pack(fill="x", ipady=2)

        etiqueta("CATEGORÍA")
        combo = ttk.Combobox(caja, textvariable=self.var_categoria,
                             values=self.categorias)
        combo.pack(fill="x")

        etiqueta("NOTAS")
        marco_notas = tk.Frame(caja, bg=c["borde"], bd=0)
        marco_notas.pack(fill="both", expand=True)
        self.txt_notas = tk.Text(marco_notas, height=4, wrap="word", bd=0,
                                 bg=c["campo"], fg=c["texto"], insertbackground=c["texto"],
                                 font=("Segoe UI", 10), padx=8, pady=6,
                                 highlightthickness=0)
        self.txt_notas.pack(fill="both", expand=True, padx=1, pady=1)
        if self.entrada and self.entrada.notas:
            self.txt_notas.insert("1.0", self.entrada.notas)

        ttk.Checkbutton(caja, text="Marcar como favorito",
                        variable=self.var_favorito).pack(anchor="w", pady=(12, 0))

        if self.entrada:
            pie = f"Creada: {self.entrada.creado[:16].replace('T', ' ')}"
            if self.entrada.modificado != self.entrada.creado:
                pie += f"   ·   Modificada: {self.entrada.modificado[:16].replace('T', ' ')}"
            if self.entrada.historial:
                pie += f"   ·   {len(self.entrada.historial)} cambio(s) de contraseña"
            ttk.Label(caja, text=pie, style="PanelTenue.TLabel").pack(anchor="w", pady=(10, 0))

        # --- acciones (el contenedor ya se creó arriba) -----------------------
        ttk.Button(acciones, text="Guardar", style="Acento.TButton",
                   command=self._guardar).pack(side="right")
        ttk.Button(acciones, text="Cancelar",
                   command=self.cancelar).pack(side="right", padx=(0, 8))

        self.lbl_error = ttk.Label(acciones, text="", style="Tenue.TLabel",
                                   foreground=c["peligro"])
        self.lbl_error.pack(side="left")

        self.bind("<Control-Return>", lambda _e: self._guardar())

    # -------------------------------------------------------------------- lógica
    def _medir(self, *_args) -> None:
        contrasena = self.var_pass.get()
        if not contrasena:
            self.barra.limpiar()
            self.lbl_fuerza.configure(text="Sin contraseña",
                                      foreground=self.colores["texto_tenue"])
            return
        info = fortaleza.evaluar(contrasena)
        self.barra.actualizar(info["puntaje"], info["color"])
        texto = f"{info['etiqueta']} · {info['entropia']:.0f} bits · se descifraría en " \
                f"{fortaleza.formatear_tiempo(info['segundos'])}"
        self.lbl_fuerza.configure(text=texto, foreground=info["color"])

    def _abrir_generador(self) -> None:
        dialogo = DialogoGenerador(self, self.colores, self.prefs,
                                   al_copiar=self.al_copiar, modo_seleccion=True)
        dialogo.hacer_modal()
        if dialogo.resultado:
            self.var_pass.set(dialogo.resultado)
            self.campo_pass.mostrar(True)

    def _guardar(self) -> None:
        sitio = self.var_sitio.get().strip()
        if not sitio:
            self.lbl_error.configure(text="El sitio es obligatorio.")
            self.entry_sitio.focus_set()
            return

        self.resultado = {
            "sitio": sitio,
            "usuario": self.var_usuario.get().strip(),
            "contrasena": self.var_pass.get(),
            "url": self.var_url.get().strip(),
            "categoria": self.var_categoria.get().strip(),
            "notas": self.txt_notas.get("1.0", "end-1c").strip(),
            "favorito": self.var_favorito.get(),
        }
        self.destroy()
