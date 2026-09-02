"""Ventana principal del gestor."""
from __future__ import annotations

import tkinter as tk
import webbrowser
from tkinter import ttk

from . import fortaleza
from .escala import px
from .widgets import Tooltip

OCULTO = "••••••••••"


class VentanaPrincipal(ttk.Frame):
    """Barra superior, lateral de categorías, tabla y panel de detalle."""

    def __init__(self, padre, app):
        super().__init__(padre)
        self.app = app
        self.colores = app.colores
        self.pack(fill="both", expand=True)

        self.var_busqueda = tk.StringVar()
        self.filtro_categoria: str | None = None
        self.solo_favoritos = False
        self.mostrar_pass = False
        self.orden_columna = "sitio"
        self.orden_inverso = False
        self.seleccion_actual: str | None = None
        self._visibles = []

        self._construir()
        self.refrescar()

    # ================================================================== interfaz
    def _construir(self) -> None:
        self._barra_superior()

        cuerpo = ttk.Frame(self)
        cuerpo.pack(fill="both", expand=True, padx=px(12), pady=(0, px(8)))

        # El orden importa: los paneles de ancho fijo se empaquetan antes que la
        # tabla, que es la única que se estira con la ventana.
        self._lateral(cuerpo)
        self._detalle(cuerpo)
        self._tabla(cuerpo)
        self._barra_estado()
        self._atajos()

    # ------------------------------------------------------------ barra superior
    def _barra_superior(self) -> None:
        barra = ttk.Frame(self, style="Barra.TFrame", padding=(px(14), px(10)))
        barra.pack(fill="x", padx=px(12), pady=px(12))

        ttk.Label(barra, text="\U0001F510", style="Panel.TLabel",
                  font=("Segoe UI Emoji", 16)).pack(side="left")
        ttk.Label(barra, text="Mis contraseñas", style="PanelTitulo.TLabel").pack(
            side="left", padx=(8, 24))

        contenedor_busqueda = ttk.Frame(barra, style="Panel.TFrame")
        contenedor_busqueda.pack(side="left", fill="x", expand=True)
        self.entry_busqueda = ttk.Entry(contenedor_busqueda, textvariable=self.var_busqueda,
                                        style="Busqueda.TEntry")
        self.entry_busqueda.pack(fill="x")
        self.entry_busqueda.insert(0, "")
        self.var_busqueda.trace_add("write", lambda *_: self.refrescar())
        Tooltip(self.entry_busqueda, "Buscar por sitio, usuario, URL, categoría o notas (Ctrl+F)")

        derecha = ttk.Frame(barra, style="Panel.TFrame")
        derecha.pack(side="right", padx=(20, 0))

        botones = [
            ("＋  Nueva", self.nueva_entrada, "Acento.TButton", "Agregar una cuenta (Ctrl+N)"),
            ("✨  Generador", self.abrir_generador, "Panel.TButton", "Generar contraseña (Ctrl+G)"),
            ("\U0001F6E1  Analizar", self.abrir_auditoria, "Panel.TButton", "Análisis de seguridad"),
        ]
        for texto, comando, estilo, ayuda in botones:
            boton = ttk.Button(derecha, text=texto, command=comando, style=estilo)
            boton.pack(side="left", padx=(0, 8))
            Tooltip(boton, ayuda)

        for texto, comando, ayuda in (("⚙", self.app.abrir_ajustes, "Ajustes"),
                                      ("\U0001F512", self.app.bloquear, "Bloquear ahora (Ctrl+L)")):
            boton = ttk.Button(derecha, text=texto, width=3, style="Icono.TButton",
                               command=comando)
            boton.pack(side="left", padx=(0, 4))
            Tooltip(boton, ayuda)

    # ------------------------------------------------------------------- lateral
    def _lateral(self, padre) -> None:
        self.lateral = ttk.Frame(padre, style="Panel.TFrame", width=px(178),
                                 padding=(px(10), px(12)))
        self.lateral.pack(side="left", fill="y")
        self.lateral.pack_propagate(False)
        self._pintar_lateral()

    def _pintar_lateral(self) -> None:
        boveda = self.app.boveda
        contador = {}
        for entrada in boveda.entradas:
            clave = entrada.categoria.strip() or "Sin categoría"
            contador[clave] = contador.get(clave, 0) + 1
        favoritos = sum(1 for e in boveda.entradas if e.favorito)

        # Repintar en cada tecla del buscador provoca parpadeo; solo se rehace
        # cuando cambia algo que se ve aquí.
        firma = (tuple(sorted(contador.items())), favoritos,
                 self.filtro_categoria, self.solo_favoritos)
        if firma == getattr(self, "_firma_lateral", None):
            return
        self._firma_lateral = firma

        for hijo in self.lateral.winfo_children():
            hijo.destroy()
        ttk.Label(self.lateral, text="BIBLIOTECA", style="Seccion.TLabel").pack(
            anchor="w", pady=(0, 6))

        def agregar(texto, activo, comando):
            estilo = "LateralActivo.TButton" if activo else "Lateral.TButton"
            ttk.Button(self.lateral, text=texto, style=estilo,
                       command=comando).pack(fill="x", pady=1)

        activo_todas = self.filtro_categoria is None and not self.solo_favoritos
        agregar(f"  Todas   ({len(boveda.entradas)})", activo_todas,
                lambda: self._filtrar(None, False))

        agregar(f"  ★ Favoritos   ({favoritos})", self.solo_favoritos,
                lambda: self._filtrar(None, True))

        categorias = boveda.categorias()
        sin_categoria = contador.get("Sin categoría", 0)
        if categorias or sin_categoria:
            ttk.Separator(self.lateral, orient="horizontal").pack(fill="x", pady=10)
            ttk.Label(self.lateral, text="CATEGORÍAS", style="Seccion.TLabel").pack(
                anchor="w", pady=(0, 6))

        for nombre in categorias + (["Sin categoría"] if sin_categoria else []):
            activo = self.filtro_categoria == nombre and not self.solo_favoritos
            agregar(f"  {nombre}   ({contador.get(nombre, 0)})", activo,
                    lambda n=nombre: self._filtrar(n, False))

    # Proporción del ancho disponible que ocupa cada columna. Suman menos de 1
    # para dejar holgura y que nunca aparezca barra horizontal.
    PROPORCIONES = {"sitio": 0.225, "usuario": 0.255, "contrasena": 0.145,
                    "fuerza": 0.205, "categoria": 0.13}

    def _repartir_columnas(self, _evento=None) -> None:
        disponible = self.tree.winfo_width() - px(4)
        if disponible < px(300) or disponible == self._ancho_previo:
            return
        self._ancho_previo = disponible
        for clave, proporcion in self.PROPORCIONES.items():
            self.tree.column(clave, width=max(px(70), int(disponible * proporcion)))

    def _filtrar(self, categoria, favoritos) -> None:
        self.filtro_categoria = categoria
        self.solo_favoritos = favoritos
        self._pintar_lateral()
        self.refrescar()

    # --------------------------------------------------------------------- tabla
    def _tabla(self, padre) -> None:
        c = self.colores
        marco = ttk.Frame(padre, style="Panel.TFrame")
        marco.pack(side="left", fill="both", expand=True, padx=px(12))

        columnas = ("sitio", "usuario", "contrasena", "fuerza", "categoria")
        self.tree = ttk.Treeview(marco, columns=columnas, show="headings",
                                 selectmode="extended")

        for clave, titulo in (("sitio", "Sitio"), ("usuario", "Usuario"),
                              ("contrasena", "Contraseña"), ("fuerza", "Fortaleza"),
                              ("categoria", "Categoría")):
            self.tree.heading(clave, text=titulo, anchor="w",
                              command=lambda k=clave: self._ordenar_por(k))
            self.tree.column(clave, width=px(140), minwidth=px(70), anchor="w",
                             stretch=False)

        self.tree.pack(side="left", fill="both", expand=True)
        # El ancho de las columnas se reparte a lo ancho de la tabla para que
        # nunca quede texto cortado, sea cual sea el tamaño de la ventana.
        self._ancho_previo = 0
        self.tree.bind("<Configure>", self._repartir_columnas)
        barra = ttk.Scrollbar(marco, orient="vertical", command=self.tree.yview)
        barra.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=barra.set)

        self.tree.tag_configure("par", background=c["fila_alt"])
        self.tree.tag_configure("impar", background=c["panel"])

        self.tree.bind("<<TreeviewSelect>>", self._cambio_seleccion)
        self.tree.bind("<Double-1>", lambda _e: self.editar_entrada())
        self.tree.bind("<Return>", lambda _e: self.editar_entrada())
        self.tree.bind("<Delete>", lambda _e: self.eliminar_entradas())
        self.tree.bind("<Button-3>", self._menu_contextual)

        self.menu = tk.Menu(self, tearoff=0, bg=c["panel"], fg=c["texto"],
                            activebackground=c["seleccion"], activeforeground=c["texto"],
                            bd=0)
        self.menu.add_command(label="Copiar contraseña     Ctrl+C", command=self.copiar_pass)
        self.menu.add_command(label="Copiar usuario        Ctrl+U", command=self.copiar_usuario)
        self.menu.add_command(label="Abrir sitio web", command=self.abrir_web)
        self.menu.add_separator()
        self.menu.add_command(label="Editar...             Enter", command=self.editar_entrada)
        self.menu.add_command(label="Duplicar", command=self.duplicar_entrada)
        self.menu.add_command(label="Marcar favorito", command=self.alternar_favorito)
        self.menu.add_separator()
        self.menu.add_command(label="Eliminar              Supr", command=self.eliminar_entradas)

    # -------------------------------------------------------------------- detalle
    def _detalle(self, padre) -> None:
        self.panel = ttk.Frame(padre, style="Panel.TFrame", width=px(285),
                               padding=px(16))
        self.panel.pack(side="right", fill="y")
        self.panel.pack_propagate(False)
        self._pintar_detalle(None)

    def _pintar_detalle(self, entrada) -> None:
        c = self.colores
        for hijo in self.panel.winfo_children():
            hijo.destroy()

        if entrada is None:
            ttk.Label(self.panel, text="\U0001F5C2", style="Panel.TLabel",
                      font=("Segoe UI Emoji", 28), foreground=c["borde"]).pack(pady=(60, 10))
            ttk.Label(self.panel, text="Selecciona una cuenta\npara ver sus datos",
                      style="PanelTenue.TLabel", justify="center").pack()
            return

        encabezado = ttk.Frame(self.panel, style="Panel.TFrame")
        encabezado.pack(fill="x")
        estrella = "★" if entrada.favorito else "☆"
        boton_fav = ttk.Button(encabezado, text=estrella, width=3, style="Icono.TButton",
                               command=self.alternar_favorito)
        boton_fav.pack(side="right")
        Tooltip(boton_fav, "Marcar o quitar de favoritos")
        ttk.Label(encabezado, text=entrada.sitio or "(sin nombre)", style="PanelTitulo.TLabel",
                  wraplength=px(210), justify="left").pack(side="left", anchor="w")

        if entrada.categoria:
            ttk.Label(self.panel, text=entrada.categoria.upper(),
                      style="Seccion.TLabel").pack(anchor="w", pady=(2, 0))

        ttk.Separator(self.panel, orient="horizontal").pack(fill="x", pady=14)

        def campo(titulo, valor, copiar=None, mono=False, secreto=False):
            ttk.Label(self.panel, text=titulo, style="Seccion.TLabel").pack(anchor="w")
            fila = ttk.Frame(self.panel, style="Panel.TFrame")
            fila.pack(fill="x", pady=(2, 12))
            texto = valor if valor else "—"
            if secreto and not self.mostrar_pass:
                texto = OCULTO
            etiqueta = ttk.Label(fila, text=texto, style="Mono.TLabel" if mono else "Panel.TLabel",
                                 wraplength=px(190), justify="left")
            etiqueta.pack(side="left", anchor="w")
            if copiar and valor:
                boton = ttk.Button(fila, text="\U0001F4CB", width=3, style="Icono.TButton",
                                   command=copiar)
                boton.pack(side="right")
                Tooltip(boton, "Copiar")
            return etiqueta

        campo("USUARIO", entrada.usuario, self.copiar_usuario)

        ttk.Label(self.panel, text="CONTRASEÑA", style="Seccion.TLabel").pack(anchor="w")
        fila_pass = ttk.Frame(self.panel, style="Panel.TFrame")
        fila_pass.pack(fill="x", pady=(2, 6))
        texto_pass = entrada.contrasena if self.mostrar_pass else OCULTO
        ttk.Label(fila_pass, text=texto_pass or "—", style="Mono.TLabel",
                  wraplength=px(170), justify="left").pack(side="left", anchor="w")
        boton_ojo = ttk.Button(fila_pass, text="\U0001F441", width=3, style="Icono.TButton",
                               command=self.alternar_visibilidad)
        boton_ojo.pack(side="right")
        Tooltip(boton_ojo, "Mostrar u ocultar contraseñas")
        if entrada.contrasena:
            boton_copiar = ttk.Button(fila_pass, text="\U0001F4CB", width=3,
                                      style="Icono.TButton", command=self.copiar_pass)
            boton_copiar.pack(side="right", padx=(0, 4))
            Tooltip(boton_copiar, "Copiar contraseña (Ctrl+C)")

        if entrada.contrasena:
            info = fortaleza.evaluar(entrada.contrasena)
            ttk.Label(self.panel, text=f"{info['etiqueta']} · {info['entropia']:.0f} bits",
                      style="PanelTenue.TLabel",
                      foreground=info["color"]).pack(anchor="w", pady=(0, 12))
        else:
            ttk.Label(self.panel, text="", style="PanelTenue.TLabel").pack(pady=(0, 6))

        if entrada.url:
            ttk.Label(self.panel, text="SITIO WEB", style="Seccion.TLabel").pack(anchor="w")
            enlace = ttk.Label(self.panel, text=entrada.url, style="PanelTenue.TLabel",
                               foreground=c["acento"], wraplength=px(250), justify="left",
                               cursor="hand2")
            enlace.pack(anchor="w", pady=(2, 12))
            enlace.bind("<Button-1>", lambda _e: self.abrir_web())

        if entrada.notas:
            ttk.Label(self.panel, text="NOTAS", style="Seccion.TLabel").pack(anchor="w")
            ttk.Label(self.panel, text=entrada.notas, style="Panel.TLabel",
                      wraplength=px(250), justify="left").pack(anchor="w", pady=(2, 12))

        acciones = ttk.Frame(self.panel, style="Panel.TFrame")
        acciones.pack(side="bottom", fill="x")
        ttk.Button(acciones, text="Editar", style="Acento.TButton",
                   command=self.editar_entrada).pack(side="left", fill="x", expand=True)
        ttk.Button(acciones, text="Eliminar", style="Peligro.TButton",
                   command=self.eliminar_entradas).pack(side="left", padx=(8, 0))

        fechas = f"Modificada: {entrada.modificado[:10]}"
        ttk.Label(self.panel, text=fechas, style="PanelTenue.TLabel").pack(
            side="bottom", anchor="w", pady=(0, 10))

    # ---------------------------------------------------------------- barra baja
    def _barra_estado(self) -> None:
        barra = ttk.Frame(self, style="Barra.TFrame", padding=(14, 6))
        barra.pack(fill="x", side="bottom")
        self.lbl_estado = ttk.Label(barra, text="", style="PanelTenue.TLabel")
        self.lbl_estado.pack(side="left")
        self.lbl_aviso = ttk.Label(barra, text="", style="PanelTenue.TLabel")
        self.lbl_aviso.pack(side="right")

    def _atajos(self) -> None:
        raiz = self.winfo_toplevel()
        raiz.bind("<Control-n>", lambda _e: self.nueva_entrada())
        raiz.bind("<Control-g>", lambda _e: self.abrir_generador())
        raiz.bind("<Control-f>", lambda _e: self.entry_busqueda.focus_set())
        raiz.bind("<Control-c>", lambda _e: self.copiar_pass())
        raiz.bind("<Control-u>", lambda _e: self.copiar_usuario())
        raiz.bind("<Control-l>", lambda _e: self.app.bloquear())
        raiz.bind("<Control-e>", lambda _e: self.editar_entrada())
        raiz.bind("<F5>", lambda _e: self.refrescar())

    # =================================================================== datos
    def _entradas_visibles(self) -> list:
        entradas = self.app.boveda.filtrar(self.var_busqueda.get().strip(),
                                           self.filtro_categoria, self.solo_favoritos)
        clave = {
            "sitio": lambda e: e.sitio.lower(),
            "usuario": lambda e: e.usuario.lower(),
            "contrasena": lambda e: e.contrasena.lower(),
            "categoria": lambda e: e.categoria.lower(),
            "fuerza": lambda e: fortaleza.evaluar(e.contrasena)["entropia"],
        }[self.orden_columna]
        return sorted(entradas, key=clave, reverse=self.orden_inverso)

    def refrescar(self, mantener_seleccion: bool = True) -> None:
        seleccion = self.seleccion_actual if mantener_seleccion else None
        for hijo in self.tree.get_children():
            self.tree.delete(hijo)

        self._visibles = self._entradas_visibles()
        for indice, entrada in enumerate(self._visibles):
            info = fortaleza.evaluar(entrada.contrasena)
            puntos = "●" * (info["puntaje"] + 1) + "○" * (4 - info["puntaje"])
            self.tree.insert(
                "", "end", iid=entrada.id,
                values=(("★ " if entrada.favorito else "") + entrada.sitio,
                        entrada.usuario,
                        entrada.contrasena if self.mostrar_pass else OCULTO,
                        f"{puntos}  {info['etiqueta']}",
                        entrada.categoria),
                tags=("par" if indice % 2 else "impar",))

        if seleccion and self.tree.exists(seleccion):
            self.tree.selection_set(seleccion)
            self.tree.see(seleccion)
        else:
            self.seleccion_actual = None
            self._pintar_detalle(None)

        self._pintar_lateral()
        self._actualizar_estado()

    def _actualizar_estado(self) -> None:
        total = len(self.app.boveda.entradas)
        visibles = len(self._visibles)
        texto = f"{total} cuentas guardadas"
        if visibles != total:
            texto = f"Mostrando {visibles} de {total} cuentas"
        self.lbl_estado.configure(text=texto)

    def _ordenar_por(self, columna: str) -> None:
        if self.orden_columna == columna:
            self.orden_inverso = not self.orden_inverso
        else:
            self.orden_columna, self.orden_inverso = columna, False
        self.refrescar()

    def _cambio_seleccion(self, _evento=None) -> None:
        seleccion = self.tree.selection()
        self.seleccion_actual = seleccion[0] if len(seleccion) == 1 else None
        entrada = self.app.boveda.obtener(self.seleccion_actual) if self.seleccion_actual else None
        self._pintar_detalle(entrada)

    def _menu_contextual(self, evento) -> None:
        fila = self.tree.identify_row(evento.y)
        if fila:
            if fila not in self.tree.selection():
                self.tree.selection_set(fila)
            self.menu.tk_popup(evento.x_root, evento.y_root)

    def _seleccionadas(self) -> list:
        return [self.app.boveda.obtener(i) for i in self.tree.selection()
                if self.app.boveda.obtener(i)]

    def _una_seleccionada(self):
        elegidas = self._seleccionadas()
        if len(elegidas) != 1:
            self.app.aviso("Selecciona una sola cuenta.")
            return None
        return elegidas[0]

    # ================================================================= acciones
    def nueva_entrada(self) -> None:
        self.app.nueva_entrada()

    def editar_entrada(self) -> None:
        entrada = self._una_seleccionada()
        if entrada:
            self.app.editar_entrada(entrada.id)

    def duplicar_entrada(self) -> None:
        entrada = self._una_seleccionada()
        if entrada:
            copia = self.app.boveda.duplicar(entrada.id)
            self.refrescar()
            if copia:
                self.seleccion_actual = copia.id
                self.refrescar()
                self.app.aviso("Cuenta duplicada.")

    def eliminar_entradas(self) -> None:
        self.app.eliminar_entradas([e.id for e in self._seleccionadas()])

    def alternar_favorito(self) -> None:
        entrada = self._una_seleccionada()
        if entrada:
            self.app.boveda.actualizar(entrada.id, favorito=not entrada.favorito)
            self.refrescar()

    def alternar_visibilidad(self) -> None:
        self.mostrar_pass = not self.mostrar_pass
        self.refrescar()
        if self.mostrar_pass:
            self.app.aviso("Contraseñas visibles.")

    def copiar_pass(self) -> None:
        entrada = self._una_seleccionada()
        if entrada:
            self.app.copiar(entrada.contrasena, "Contraseña")

    def copiar_usuario(self) -> None:
        entrada = self._una_seleccionada()
        if entrada:
            self.app.copiar(entrada.usuario, "Usuario")

    def abrir_web(self) -> None:
        entrada = self._una_seleccionada()
        if not entrada:
            return
        url = entrada.url.strip() or entrada.sitio.strip()
        if not url:
            return
        if not url.startswith(("http://", "https://")):
            if "." not in url:
                self.app.aviso("Esta cuenta no tiene una URL válida.")
                return
            url = "https://" + url
        webbrowser.open(url)

    def abrir_generador(self) -> None:
        self.app.abrir_generador()

    def abrir_auditoria(self) -> None:
        self.app.abrir_auditoria()
