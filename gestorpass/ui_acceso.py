"""Ventanas de acceso: crear bóveda, iniciar sesión y desbloquear."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from . import fortaleza, i18n
from .escala import px
from .widgets import BarraFortaleza, centrar

LONGITUD_MINIMA_MAESTRA = 8


class VentanaAcceso(tk.Toplevel):
    """Pantalla de acceso.

    Modos:
      ``crear``       define la contraseña maestra de una bóveda nueva.
      ``abrir``       pide la maestra para descifrar la bóveda existente.
      ``desbloquear`` re-autentica tras el bloqueo automático.
    """

    def __init__(self, padre, colores: dict, modo: str, ruta_vault=None,
                 verificador=None):
        super().__init__(padre)
        self.colores = colores
        self.modo = modo
        self.ruta_vault = ruta_vault
        self.verificador = verificador   # callable(contraseña) -> bool | str
        self.resultado: str | None = None
        self.cancelado = False
        self._intentos = 0

        self.title(i18n.t("app_title"))
        self.configure(bg=colores["fondo"])
        self.resizable(False, False)

        # OJO: transient() sobre una ventana padre oculta esconde TAMBIÉN esta
        # ventana. Al arrancar, la raíz está oculta (withdraw) hasta que se
        # abre la bóveda, así que solo se enlaza si el padre se está viendo.
        if padre is not None and padre.winfo_viewable():
            self.transient(padre)

        self.var_pass = tk.StringVar()
        self.var_pass2 = tk.StringVar()
        self.var_ver = tk.BooleanVar(value=False)

        self._construir()
        alto = 555 if modo == "crear" else 400
        centrar(self, 440, alto, None)
        self.protocol("WM_DELETE_WINDOW", self._cerrar)
        self.bind("<Escape>", lambda _e: self._cerrar())

        self.deiconify()
        self.lift()
        self.after(120, self._tomar_foco)

    def _tomar_foco(self) -> None:
        """Trae la ventana al frente y pone el cursor en el campo."""
        try:
            self.lift()
            self.focus_force()
            self.entry_pass.focus_set()
        except tk.TclError:
            pass  # La ventana se cerró antes de que llegara este aviso.

    # ------------------------------------------------------------------ interfaz
    def _construir(self) -> None:
        c = self.colores
        marco = ttk.Frame(self, padding=32)
        marco.pack(fill="both", expand=True)

        ttk.Label(marco, text="\U0001F510", font=("Segoe UI Emoji", 34)).pack()

        titulos = {
            "crear": (i18n.t("access_create_title"), i18n.t("access_create_desc")),
            "abrir": (i18n.t("access_open_title"), i18n.t("access_open_desc")),
            "desbloquear": (i18n.t("access_open_title"), i18n.t("access_open_desc")),
        }
        titulo, subtitulo = titulos[self.modo]

        ttk.Label(marco, text=titulo, style="Titulo.TLabel").pack(pady=(10, 4))
        ttk.Label(marco, text=subtitulo, style="Tenue.TLabel",
                  justify="center").pack(pady=(0, 20))

        ttk.Label(marco, text=i18n.t("access_master_label"), style="Tenue.TLabel").pack(anchor="w")
        self.entry_pass = ttk.Entry(marco, textvariable=self.var_pass, show="•",
                                    font=("Consolas", 11))
        self.entry_pass.pack(fill="x", pady=(4, 10), ipady=3)
        self.entry_pass.bind("<Return>", self._al_pulsar_enter)

        if self.modo == "crear":
            self.barra = BarraFortaleza(marco, c, ancho=376, fondo=c["fondo"])
            self.barra.pack(fill="x")
            self.lbl_fuerza = ttk.Label(marco, text=i18n.t("access_err_short"),
                                        style="Tenue.TLabel")
            self.lbl_fuerza.pack(anchor="w", pady=(6, 12))
            self.var_pass.trace_add("write", self._medir)

            ttk.Label(marco, text=i18n.t("access_confirm_label"), style="Tenue.TLabel").pack(anchor="w")
            self.entry_pass2 = ttk.Entry(marco, textvariable=self.var_pass2, show="•",
                                         font=("Consolas", 11))
            self.entry_pass2.pack(fill="x", pady=(4, 10), ipady=3)
            self.entry_pass2.bind("<Return>", self._al_pulsar_enter)

        ttk.Checkbutton(marco, text="Show password" if i18n.get_idioma() == "en" else "Mostrar contraseña",
                        variable=self.var_ver,
                        style="Fondo.TCheckbutton",
                        command=self._alternar_ver).pack(anchor="w")

        self.lbl_error = ttk.Label(marco, text="", style="Tenue.TLabel",
                                   foreground=c["peligro"], wraplength=px(376),
                                   justify="left")
        self.lbl_error.pack(anchor="w", pady=(10, 0))

        texto_boton = {"crear": i18n.t("access_btn_create"), "abrir": i18n.t("access_btn_unlock"),
                       "desbloquear": i18n.t("access_btn_unlock")}[self.modo]
        self.boton = ttk.Button(marco, text=texto_boton, style="Acento.TButton",
                                command=self._aceptar)
        self.boton.pack(fill="x", pady=(16, 0), ipady=4)

        if self.modo == "crear":
            ttk.Label(marco, text="⚠  Si la olvidas no hay forma de recuperar tus datos:\n"
                                  "no se guarda en ningún servidor ni en el programa.",
                      style="Tenue.TLabel", justify="left",
                      foreground=c["aviso"], wraplength=px(376)).pack(anchor="w", pady=(14, 0))
        elif self.ruta_vault:
            ttk.Label(marco, text=f"Bóveda: {self.ruta_vault}", style="Tenue.TLabel",
                      wraplength=px(376), justify="left").pack(anchor="w", pady=(14, 0))

    def _alternar_ver(self) -> None:
        mostrar = "" if self.var_ver.get() else "•"
        self.entry_pass.configure(show=mostrar)
        if self.modo == "crear":
            self.entry_pass2.configure(show=mostrar)

    def _medir(self, *_args) -> None:
        info = fortaleza.evaluar(self.var_pass.get())
        self.barra.actualizar(info["puntaje"] if self.var_pass.get() else -1, info["color"])
        if not self.var_pass.get():
            self.lbl_fuerza.configure(text="Mínimo 8 caracteres", foreground=self.colores["texto_tenue"])
            return
        detalle = info["avisos"][0] if info["avisos"] else "Buena elección"
        self.lbl_fuerza.configure(text=f"{info['etiqueta']} · {detalle}",
                                 foreground=info["color"])

    # -------------------------------------------------------------------- lógica
    def _al_pulsar_enter(self, _evento=None):
        """Enter válida el formulario.

        Tk puede disparar este binding sin evento mientras la ventana se está
        destruyendo, así que el argumento es opcional y se comprueba que la
        ventana siga viva.
        """
        try:
            if not self.winfo_exists():
                return "break"
        except tk.TclError:
            return "break"
        self._aceptar()
        return "break"

    def _error(self, mensaje: str) -> None:
        self.lbl_error.configure(text=mensaje)
        self.bell()

    def _aceptar(self) -> None:
        contrasena = self.var_pass.get()
        if not contrasena:
            self._error(i18n.t("access_err_empty"))
            return

        if self.modo == "crear":
            if len(contrasena) < LONGITUD_MINIMA_MAESTRA:
                self._error(i18n.t("access_err_short"))
                return
            if contrasena != self.var_pass2.get():
                self._error(i18n.t("access_err_mismatch"))
                return
            self.resultado = contrasena
            self.destroy()
            return

        # Modos "abrir" y "desbloquear": la verificación la hace quien nos llamó.
        self.boton.configure(state="disabled", text="...")
        self.lbl_error.configure(text="")
        self.update_idletasks()

        resultado = self.verificador(contrasena) if self.verificador else True
        self.boton.configure(state="normal", text=i18n.t("access_btn_unlock"))

        if resultado is True:
            self.resultado = contrasena
            self.destroy()
            return

        self._intentos += 1
        mensaje = resultado if isinstance(resultado, str) else i18n.t("access_err_wrong")
        if self._intentos >= 3:
            mensaje += f"  (#{self._intentos})"
        self._error(mensaje)
        self.var_pass.set("")
        self.entry_pass.focus_set()

    def _cerrar(self) -> None:
        self.cancelado = True
        self.resultado = None
        self.destroy()

    def esperar(self) -> str | None:
        self.grab_set()
        self.wait_window(self)
        return self.resultado
