"""Dialogos secundarios: importación, auditoria, maestra y ajustes."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from . import fortaleza, i18n
from .escala import px
from .widgets import BarraFortaleza, DialogoBase

UMBRAL_DEBIL = 1  # puntaje 0 y 1 se consideran contraseñas a cambiar


class DialogoImportarTexto(DialogoBase):
    """Carga masiva pegando líneas de texto."""

    def __init__(self, padre, colores: dict):
        super().__init__(padre, colores, "Carga masiva", 560, 520, redimensionable=True)
        self.var_separador = tk.StringVar(value=",")
        self.var_omitir = tk.BooleanVar(value=True)
        self._construir()

    def _construir(self) -> None:
        c = self.colores
        raiz = self.contenedor

        ttk.Label(raiz, text="Carga masiva", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(raiz, text="Pega una línea por cuenta con el formato:\n"
                             "Sitio , Usuario , Contraseña , URL , Categoría\n"
                             "Los últimos dos campos son opcionales.",
                  style="Tenue.TLabel", justify="left").pack(anchor="w", pady=(4, 12))

        # Botones y opciones se anclan abajo antes que el area de texto, que es
        # la que se estira; así nunca quedan fuera de la ventana.
        acciones = ttk.Frame(raiz)
        acciones.pack(side="bottom", fill="x", pady=(16, 0))
        ttk.Button(acciones, text="Importar", style="Acento.TButton",
                   command=self._aceptar).pack(side="right")
        ttk.Button(acciones, text="Cancelar",
                   command=self.cancelar).pack(side="right", padx=(0, 8))

        opciones = ttk.Frame(raiz)
        opciones.pack(side="bottom", fill="x", pady=(12, 0))
        ttk.Label(opciones, text="Separador:", style="Tenue.TLabel").pack(side="left")
        ttk.Combobox(opciones, textvariable=self.var_separador, width=10,
                     state="readonly",
                     values=[",", ";", "|", "TAB"]).pack(side="left", padx=(8, 20))
        ttk.Checkbutton(opciones, text="Omitir duplicados exactos",
                        variable=self.var_omitir,
                        style="Fondo.TCheckbutton").pack(side="left")

        marco = tk.Frame(raiz, bg=c["borde"])
        marco.pack(fill="both", expand=True)
        self.txt = tk.Text(marco, wrap="none", bd=0, bg=c["campo"], fg=c["texto"],
                           insertbackground=c["texto"], font=("Consolas", 10),
                           padx=10, pady=8, highlightthickness=0)
        self.txt.pack(side="left", fill="both", expand=True, padx=1, pady=1)
        barra = ttk.Scrollbar(marco, orient="vertical", command=self.txt.yview)
        barra.pack(side="right", fill="y")
        self.txt.configure(yscrollcommand=barra.set)
        self.txt.insert("1.0", "ejemplo.com, juan@correo.com, MiClaveSegura123!\n")

    def _aceptar(self) -> None:
        separador = self.var_separador.get()
        self.resultado = {
            "texto": self.txt.get("1.0", "end-1c"),
            "separador": "\t" if separador == "TAB" else separador,
            "omitir": self.var_omitir.get(),
        }
        self.destroy()


class DialogoAuditoria(DialogoBase):
    """Análisis de seguridad de todas las contraseñas guardadas."""

    def __init__(self, padre, colores: dict, boveda, al_editar=None):
        super().__init__(padre, colores, i18n.t("audit_title"), 820, 625,
                         redimensionable=True)
        self.boveda = boveda
        self.al_editar = al_editar
        self._construir()
        self._analizar()

    def _construir(self) -> None:
        c = self.colores
        raiz = self.contenedor

        ttk.Label(raiz, text=i18n.t("audit_title"), style="Titulo.TLabel").pack(anchor="w")
        self.lbl_resumen = ttk.Label(raiz, text="", style="Tenue.TLabel")
        self.lbl_resumen.pack(anchor="w", pady=(4, 12))

        self.tarjetas = ttk.Frame(raiz)
        self.tarjetas.pack(fill="x", pady=(0, 14))

        # El pie se reserva su espacio antes que la tabla, que es la que crece.
        acciones = ttk.Frame(raiz)
        acciones.pack(side="bottom", fill="x", pady=(14, 0))
        ttk.Label(acciones, text=i18n.t("audit_hint_edit"),
                  style="Tenue.TLabel").pack(side="left")
        ttk.Button(acciones, text=i18n.t("close"), command=self.cancelar).pack(side="right")

        marco = ttk.Frame(raiz, style="Panel.TFrame")
        marco.pack(fill="both", expand=True)

        columnas = ("problema", "sitio", "usuario", "detalle")
        self.tree = ttk.Treeview(marco, columns=columnas, show="headings", selectmode="browse")
        for col, titulo, ancho, estira in (("problema", i18n.t("audit_col_issue"), 145, False),
                                           ("sitio", i18n.t("audit_col_site"), 150, False),
                                           ("usuario", i18n.t("audit_col_user"), 175, False),
                                           ("detalle", i18n.t("audit_col_detail"), 250, True)):
            self.tree.heading(col, text=titulo, anchor="w")
            self.tree.column(col, width=px(ancho), minwidth=px(90), anchor="w",
                             stretch=estira)
        self.tree.pack(side="left", fill="both", expand=True)

        barra = ttk.Scrollbar(marco, orient="vertical", command=self.tree.yview)
        barra.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=barra.set)

        self.tree.tag_configure("critico", foreground=c["peligro"])
        self.tree.tag_configure("medio", foreground=c["aviso"])
        self.tree.bind("<Double-1>", self._abrir_entrada)

    def _tarjeta(self, texto: str, valor: str, color: str) -> None:
        caja = ttk.Frame(self.tarjetas, style="Panel.TFrame", padding=(14, 10))
        caja.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ttk.Label(caja, text=valor, style="Panel.TLabel",
                  font=("Segoe UI", 18, "bold"), foreground=color).pack(anchor="w")
        ttk.Label(caja, text=texto, style="PanelTenue.TLabel").pack(anchor="w")

    def _analizar(self) -> None:
        c = self.colores
        entradas = self.boveda.entradas
        repetidas = self.boveda.contrasenas_repetidas()
        ids_repetidos = {e.id for grupo in repetidas.values() for e in grupo}

        debiles = vacias = 0
        filas = []

        for entrada in entradas:
            if not entrada.contrasena:
                vacias += 1
                filas.append((i18n.t("audit_issue_empty"), entrada,
                              i18n.t("audit_detail_empty"), "medio"))
                continue
            info = fortaleza.evaluar(entrada.contrasena)
            if info["puntaje"] <= UMBRAL_DEBIL:
                debiles += 1
                motivo = info["avisos"][0] if info["avisos"] else f"{info['entropia']:.0f} bits"
                filas.append((i18n.t("audit_issue_weak", nivel=info['etiqueta'].lower()),
                              entrada, motivo,
                              "critico" if info["puntaje"] == 0 else "medio"))

        for grupo in repetidas.values():
            sitios = ", ".join(sorted({e.sitio for e in grupo}))
            for entrada in grupo:
                filas.append((i18n.t("audit_issue_reused"), entrada,
                              i18n.t("audit_detail_reused", sitios=sitios), "critico"))

        total = len(entradas)
        seguras = total - len({e.id for _, e, _, _ in filas})
        porcentaje = (seguras / total * 100) if total else 100

        for hijo in self.tarjetas.winfo_children():
            hijo.destroy()
        self._tarjeta(i18n.t("audit_card_total"), str(total), c["texto"])
        self._tarjeta(i18n.t("audit_card_weak"), str(debiles), c["peligro"] if debiles else c["exito"])
        self._tarjeta(i18n.t("audit_card_reused"), str(len(ids_repetidos)),
                      c["peligro"] if ids_repetidos else c["exito"])
        self._tarjeta(i18n.t("audit_card_empty"), str(vacias), c["aviso"] if vacias else c["exito"])
        self._tarjeta(i18n.t("audit_card_health"), f"{porcentaje:.0f}%",
                      c["exito"] if porcentaje >= 80 else c["aviso"])

        for hijo in self.tree.get_children():
            self.tree.delete(hijo)

        orden = {"critico": 0, "medio": 1}
        for problema, entrada, detalle, nivel in sorted(filas, key=lambda f: orden[f[3]]):
            self.tree.insert("", "end", iid=f"{entrada.id}|{problema}",
                             values=(problema, entrada.sitio, entrada.usuario, detalle),
                             tags=(nivel,))

        if not filas:
            self.lbl_resumen.configure(
                text="Sin problemas detectados. Todas tus contraseñas son fuertes y únicas.",
                foreground=c["exito"])
        else:
            self.lbl_resumen.configure(
                text=f"{len(filas)} avisos en {total} cuentas. "
                     "Las contraseñas repetidas son el riesgo más grave: "
                     "si filtran una, entran a todas.",
                foreground=c["texto_tenue"])

    def _abrir_entrada(self, _evento=None) -> None:
        seleccion = self.tree.selection()
        if seleccion and self.al_editar:
            id_entrada = seleccion[0].split("|", 1)[0]
            self.al_editar(id_entrada)
            self.grab_set()   # el formulario de edición se llevó el foco modal
            self._analizar()


class DialogoCambiarMaestra(DialogoBase):
    """Cambio de la contraseña maestra."""

    def __init__(self, padre, colores: dict, verificador):
        super().__init__(padre, colores, "Cambiar contraseña maestra", 460, 470)
        self.verificador = verificador
        self.var_actual = tk.StringVar()
        self.var_nueva = tk.StringVar()
        self.var_confirmar = tk.StringVar()
        self._construir()

    def _construir(self) -> None:
        c = self.colores
        raiz = self.contenedor

        ttk.Label(raiz, text="Cambiar contraseña maestra", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(raiz, text="La bóveda se volverá a cifrar con la nueva llave.",
                  style="Tenue.TLabel").pack(anchor="w", pady=(4, 18))

        for texto, variable, nombre in (("Contraseña actual", self.var_actual, "actual"),
                                        ("Nueva contraseña", self.var_nueva, "nueva"),
                                        ("Repite la nueva", self.var_confirmar, "confirmar")):
            ttk.Label(raiz, text=texto, style="Tenue.TLabel").pack(anchor="w", pady=(8, 4))
            entry = ttk.Entry(raiz, textvariable=variable, show="•", font=("Consolas", 11))
            entry.pack(fill="x", ipady=2)
            if nombre == "nueva":
                self.barra = BarraFortaleza(raiz, c, ancho=400, fondo=c["fondo"])
                self.barra.pack(fill="x", pady=(8, 2))
                self.lbl_fuerza = ttk.Label(raiz, text="", style="Tenue.TLabel")
                self.lbl_fuerza.pack(anchor="w")
                variable.trace_add("write", self._medir)

        self.lbl_error = ttk.Label(raiz, text="", style="Tenue.TLabel",
                                   foreground=c["peligro"], wraplength=px(400))
        self.lbl_error.pack(anchor="w", pady=(12, 0))

        acciones = ttk.Frame(raiz)
        acciones.pack(fill="x", pady=(16, 0))
        ttk.Button(acciones, text="Cambiar", style="Acento.TButton",
                   command=self._aceptar).pack(side="right")
        ttk.Button(acciones, text="Cancelar",
                   command=self.cancelar).pack(side="right", padx=(0, 8))

    def _medir(self, *_args) -> None:
        valor = self.var_nueva.get()
        if not valor:
            self.barra.limpiar()
            self.lbl_fuerza.configure(text="")
            return
        info = fortaleza.evaluar(valor)
        self.barra.actualizar(info["puntaje"], info["color"])
        self.lbl_fuerza.configure(text=info["etiqueta"], foreground=info["color"])

    def _aceptar(self) -> None:
        if not self.verificador(self.var_actual.get()):
            self.lbl_error.configure(text="La contraseña actual no es correcta.")
            return
        nueva = self.var_nueva.get()
        if len(nueva) < 8:
            self.lbl_error.configure(text="La nueva debe tener al menos 8 caracteres.")
            return
        if nueva != self.var_confirmar.get():
            self.lbl_error.configure(text="Las contraseñas nuevas no coinciden.")
            return
        self.resultado = nueva
        self.destroy()


class DialogoAjustes(DialogoBase):
    """Preferencias de la aplicación."""

    def __init__(self, padre, colores: dict, prefs: dict, ruta_vault: str):
        super().__init__(padre, colores, i18n.t("settings_title"), 500, 500)
        self.prefs = prefs
        self.ruta_vault = ruta_vault
        self.var_idioma = tk.StringVar(value=prefs.get("idioma", "auto"))
        self.var_tema = tk.StringVar(value=prefs.get("tema", "oscuro"))
        self.var_bloqueo = tk.IntVar(value=int(prefs.get("minutos_autobloqueo", 5)))
        self.var_portapapeles = tk.IntVar(value=int(prefs.get("segundos_portapapeles", 30)))
        self._construir()

    def _construir(self) -> None:
        raiz = self.contenedor
        ttk.Label(raiz, text=i18n.t("settings_title"), style="Titulo.TLabel").pack(anchor="w", pady=(0, 16))

        caja = ttk.Frame(raiz, style="Panel.TFrame", padding=16)
        caja.pack(fill="x")

        # Idioma / Language
        ttk.Label(caja, text=i18n.t("settings_lang_label").upper(), style="Seccion.TLabel").pack(anchor="w")
        fila_lang = ttk.Frame(caja, style="Panel.TFrame")
        fila_lang.pack(anchor="w", pady=(6, 14))
        combo_lang = ttk.Combobox(fila_lang, textvariable=self.var_idioma, state="readonly", width=14,
                                  values=["auto", "en", "es"])
        combo_lang.pack(side="left")
        ttk.Label(fila_lang, text="(auto · en: English · es: Español)",
                  style="PanelTenue.TLabel").pack(side="left", padx=8)

        # Tema
        ttk.Label(caja, text=i18n.t("settings_theme_label").upper(), style="Seccion.TLabel").pack(anchor="w")
        fila = ttk.Frame(caja, style="Panel.TFrame")
        fila.pack(anchor="w", pady=(6, 14))
        ttk.Radiobutton(fila, text=i18n.t("settings_theme_dark"), value="oscuro",
                        variable=self.var_tema).pack(side="left", padx=(0, 16))
        ttk.Radiobutton(fila, text=i18n.t("settings_theme_light"), value="claro",
                        variable=self.var_tema).pack(side="left")

        # Autobloqueo
        ttk.Label(caja, text=i18n.t("settings_autolock_label").upper(), style="Seccion.TLabel").pack(anchor="w")
        fila2 = ttk.Frame(caja, style="Panel.TFrame")
        fila2.pack(anchor="w", pady=(6, 14))
        ttk.Spinbox(fila2, from_=0, to=120, width=6,
                    textvariable=self.var_bloqueo).pack(side="left")
        ttk.Label(fila2, text=i18n.t("settings_autolock_min", m="min") + " (0 = off)",
                  style="PanelTenue.TLabel").pack(side="left", padx=8)

        # Portapapeles
        ttk.Label(caja, text=i18n.t("settings_clipboard_label").upper(), style="Seccion.TLabel").pack(anchor="w")
        fila3 = ttk.Frame(caja, style="Panel.TFrame")
        fila3.pack(anchor="w", pady=(6, 0))
        ttk.Spinbox(fila3, from_=0, to=300, width=6,
                    textvariable=self.var_portapapeles).pack(side="left")
        ttk.Label(fila3, text=i18n.t("settings_clipboard_sec", s="sec") + " (0 = off)",
                  style="PanelTenue.TLabel").pack(side="left", padx=8)

        ttk.Label(raiz, text="VAULT FILE", style="Seccion.TLabel").pack(
            anchor="w", pady=(16, 4))
        ttk.Label(raiz, text=self.ruta_vault, style="Tenue.TLabel",
                  wraplength=px(440), justify="left").pack(anchor="w")

        acciones = ttk.Frame(raiz)
        acciones.pack(fill="x", pady=(20, 0))
        ttk.Button(acciones, text=i18n.t("save"), style="Acento.TButton",
                   command=self._aceptar).pack(side="right")
        ttk.Button(acciones, text=i18n.t("cancel"),
                   command=self.cancelar).pack(side="right", padx=(0, 8))

    def _aceptar(self) -> None:
        try:
            bloqueo = max(0, min(120, self.var_bloqueo.get()))
            portapapeles = max(0, min(300, self.var_portapapeles.get()))
        except tk.TclError:
            bloqueo, portapapeles = 5, 30
        self.resultado = {
            "idioma": self.var_idioma.get(),
            "tema": self.var_tema.get(),
            "minutos_autobloqueo": bloqueo,
            "segundos_portapapeles": portapapeles,
        }
        self.destroy()
