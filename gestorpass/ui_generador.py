"""Ventana del generador de contraseñas aleatorias."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from . import fortaleza, generador, i18n
from .widgets import BarraFortaleza, DialogoBase, Tooltip


class DialogoGenerador(DialogoBase):
    """Generador estilo Avast: longitud, tipos de caracter y medidor en vivo.

    Si se abre con ``modo_seleccion=True`` muestra el botón "Usar esta
    contraseña" y deja el resultado en ``self.resultado``.
    """

    def __init__(self, padre, colores: dict, prefs: dict, al_copiar=None,
                 modo_seleccion: bool = False):
        super().__init__(padre, colores, i18n.t("gen_title"), 520,
                         560 if modo_seleccion else 520)
        self.prefs = prefs
        self.al_copiar = al_copiar
        self.modo_seleccion = modo_seleccion

        self.var_pass = tk.StringVar()
        self.var_longitud = tk.IntVar(value=int(prefs.get("gen_longitud", 20)))
        self.var_may = tk.BooleanVar(value=bool(prefs.get("gen_mayusculas", True)))
        self.var_min = tk.BooleanVar(value=bool(prefs.get("gen_minusculas", True)))
        self.var_num = tk.BooleanVar(value=bool(prefs.get("gen_numeros", True)))
        self.var_sim = tk.BooleanVar(value=bool(prefs.get("gen_simbolos", True)))
        self.var_amb = tk.BooleanVar(value=bool(prefs.get("gen_sin_ambiguos", False)))

        self._construir()
        self.regenerar()

    # ------------------------------------------------------------------ interfaz
    def _construir(self) -> None:
        c = self.colores
        raiz = self.contenedor

        ttk.Label(raiz, text=i18n.t("gen_title"), style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(raiz, text=i18n.t("gen_subtitle"),
                  style="Tenue.TLabel").pack(anchor="w", pady=(2, 16))

        # --- resultado ------------------------------------------------------
        caja = ttk.Frame(raiz, style="Panel.TFrame", padding=14)
        caja.pack(fill="x")

        fila = ttk.Frame(caja, style="Panel.TFrame")
        fila.pack(fill="x")

        self.entry = tk.Entry(fila, textvariable=self.var_pass, font=("Consolas", 14, "bold"),
                              bg=c["panel"], fg=c["texto"], relief="flat",
                              insertbackground=c["texto"], readonlybackground=c["panel"],
                              state="readonly", justify="center")
        self.entry.pack(side="left", fill="x", expand=True, ipady=6)

        btn_regen = ttk.Button(fila, text="↻", width=3, style="Icono.TButton",
                               command=self.regenerar, takefocus=False)
        btn_regen.pack(side="left", padx=(8, 0))
        Tooltip(btn_regen, "Generar otra (Ctrl+R)")

        btn_copiar = ttk.Button(fila, text="\U0001F4CB", width=3, style="Icono.TButton",
                                command=self.copiar, takefocus=False)
        btn_copiar.pack(side="left", padx=(4, 0))
        Tooltip(btn_copiar, "Copiar al portapapeles")

        self.barra = BarraFortaleza(caja, c, ancho=440, fondo=c["panel"],
                                    style="Panel.TFrame")
        self.barra.pack(fill="x", pady=(14, 6))

        self.lbl_nivel = ttk.Label(caja, text="", style="Panel.TLabel",
                                   font=("Segoe UI", 10, "bold"))
        self.lbl_nivel.pack(anchor="w")
        self.lbl_tiempo = ttk.Label(caja, text="", style="PanelTenue.TLabel")
        self.lbl_tiempo.pack(anchor="w", pady=(2, 0))

        # --- longitud -------------------------------------------------------
        opciones = ttk.Frame(raiz, style="Panel.TFrame", padding=14)
        opciones.pack(fill="x", pady=(12, 0))

        cabecera = ttk.Frame(opciones, style="Panel.TFrame")
        cabecera.pack(fill="x")
        ttk.Label(cabecera, text="LONGITUD", style="Seccion.TLabel").pack(side="left")
        self.lbl_longitud = ttk.Label(cabecera, text="20", style="Panel.TLabel",
                                      font=("Consolas", 12, "bold"))
        self.lbl_longitud.pack(side="right")

        self.escala = ttk.Scale(opciones, from_=generador.LONGITUD_MINIMA,
                                to=generador.LONGITUD_MAXIMA, orient="horizontal",
                                command=self._cambio_longitud)
        self.escala.set(self.var_longitud.get())
        self.escala.pack(fill="x", pady=(6, 12))

        # --- tipos de caracter ----------------------------------------------
        ttk.Label(opciones, text="INCLUIR" if i18n.get_idioma() == "es" else "INCLUDE", style="Seccion.TLabel").pack(anchor="w")
        rejilla = ttk.Frame(opciones, style="Panel.TFrame")
        rejilla.pack(fill="x", pady=(6, 0))
        rejilla.columnconfigure(0, weight=1)
        rejilla.columnconfigure(1, weight=1)

        casillas = [
            (i18n.t("gen_uppercase"), self.var_may, 0, 0),
            (i18n.t("gen_numbers"), self.var_num, 0, 1),
            (i18n.t("gen_lowercase"), self.var_min, 1, 0),
            (i18n.t("gen_symbols"), self.var_sim, 1, 1),
        ]
        for texto, variable, fila_i, col in casillas:
            ttk.Checkbutton(rejilla, text=texto, variable=variable,
                            command=self.regenerar).grid(row=fila_i, column=col,
                                                         sticky="w", pady=3)

        ttk.Checkbutton(opciones, text=i18n.t("gen_no_ambiguous"),
                        variable=self.var_amb,
                        command=self.regenerar).pack(anchor="w", pady=(8, 0))

        self.lbl_error = ttk.Label(raiz, text="", style="Tenue.TLabel",
                                   foreground=c["peligro"])
        self.lbl_error.pack(anchor="w", pady=(8, 0))

        # --- acciones -------------------------------------------------------
        acciones = ttk.Frame(raiz)
        acciones.pack(fill="x", pady=(14, 0))

        if self.modo_seleccion:
            ttk.Button(acciones, text=i18n.t("gen_use_btn"), style="Acento.TButton",
                       command=self.usar).pack(side="right")
            ttk.Button(acciones, text=i18n.t("cancel"),
                       command=self.cancelar).pack(side="right", padx=(0, 8))
        else:
            ttk.Button(acciones, text=i18n.t("copy"), style="Acento.TButton",
                       command=self.copiar).pack(side="right")
            ttk.Button(acciones, text=i18n.t("close"),
                       command=self.cancelar).pack(side="right", padx=(0, 8))

        self.bind("<Control-r>", lambda _e: self.regenerar())
        self.bind("<Return>", lambda _e: self.usar() if self.modo_seleccion else self.copiar())

    # -------------------------------------------------------------------- lógica
    def _cambio_longitud(self, valor) -> None:
        longitud = int(float(valor))
        if longitud != self.var_longitud.get():
            self.var_longitud.set(longitud)
            self.lbl_longitud.configure(text=str(longitud))
            self.regenerar()
        else:
            self.lbl_longitud.configure(text=str(longitud))

    def regenerar(self, _evento=None) -> None:
        longitud = self.var_longitud.get()
        try:
            contrasena = generador.generar(
                longitud=longitud,
                mayusculas=self.var_may.get(), minusculas=self.var_min.get(),
                numeros=self.var_num.get(), simbolos=self.var_sim.get(),
                sin_ambiguos=self.var_amb.get(),
            )
        except generador.ErrorGenerador as exc:
            self.lbl_error.configure(text=str(exc))
            self.var_pass.set("")
            self.barra.limpiar()
            self.lbl_nivel.configure(text="")
            self.lbl_tiempo.configure(text="")
            return

        self.lbl_error.configure(text="")
        self.var_pass.set(contrasena)
        self._actualizar_medidor(len(contrasena))
        self._guardar_prefs()

    def _actualizar_medidor(self, longitud: int) -> None:
        alfabeto = generador.tamano_alfabeto(
            self.var_may.get(), self.var_min.get(), self.var_num.get(),
            self.var_sim.get(), self.var_amb.get())
        bits = generador.entropia_generada(longitud, alfabeto)
        etiqueta, color, puntaje = fortaleza.nivel_por_entropia(bits)
        segundos = fortaleza._segundos_para_romper(bits)

        self.barra.actualizar(puntaje, color)
        self.lbl_nivel.configure(text=f"{etiqueta}   ·   {bits:.0f} bits de entropía",
                                 foreground=color)
        self.lbl_tiempo.configure(
            text=f"Tiempo estimado para descifrarla: {fortaleza.formatear_tiempo(segundos)}"
                 f"  ({alfabeto} caracteres posibles)")

    def _guardar_prefs(self) -> None:
        self.prefs.update({
            "gen_longitud": self.var_longitud.get(),
            "gen_mayusculas": self.var_may.get(),
            "gen_minusculas": self.var_min.get(),
            "gen_numeros": self.var_num.get(),
            "gen_simbolos": self.var_sim.get(),
            "gen_sin_ambiguos": self.var_amb.get(),
        })

    def copiar(self) -> None:
        if self.al_copiar and self.var_pass.get():
            self.al_copiar(self.var_pass.get())

    def usar(self) -> None:
        self.resultado = self.var_pass.get()
        self.destroy()
