"""Aplicación: arranque, sesión, bloqueo automático y acciones globales."""
from __future__ import annotations

import time
import tkinter as tk
from tkinter import filedialog, messagebox

from . import config, escala, i18n, tema
from .boveda import (Boveda, BovedaCorrupta, ContrasenaIncorrecta, Entrada,
                     ErrorBoveda, buscar_excel_para_migrar)
from .escala import px
from .ui_acceso import VentanaAcceso
from .ui_dialogos import (DialogoAjustes, DialogoAuditoria, DialogoCambiarMaestra,
                          DialogoImportarTexto)
from .ui_entrada import DialogoEntrada
from .ui_generador import DialogoGenerador
from .ui_principal import VentanaPrincipal


class App:
    def __init__(self):
        escala.activar()  # antes de crear la ventana: evita el texto borroso
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title(f"{config.APP_NAME} {config.APP_VERSION}")

        icono = config.ruta_recurso("gestor.ico")
        if icono:
            try:
                self.root.iconbitmap(default=str(icono))
            except tk.TclError:
                pass  # Sin icono se ve el de Tk, pero la app funciona igual.

        self.prefs = config.cargar_preferencias()
        i18n.set_idioma(self.prefs.get("idioma", "auto"))
        self.colores = tema.aplicar(self.root, self.prefs.get("tema", "oscuro"))

        self.boveda: Boveda | None = None
        self.ventana: VentanaPrincipal | None = None
        self.bloqueada = True
        self._ultimo_uso = time.monotonic()
        self._tarea_bloqueo = None
        self._tarea_portapapeles = None
        self._tarea_aviso = None
        self._copiado = None

    # ================================================================= arranque
    def ejecutar(self) -> None:
        if not self._sesion_inicial():
            self.root.destroy()
            return

        self._construir_ventana()
        self.root.deiconify()
        self._vigilar_inactividad()
        self.root.protocol("WM_DELETE_WINDOW", self.salir)
        self.root.mainloop()

    def _sesion_inicial(self) -> bool:
        ruta = config.ruta_vault()

        if not ruta.exists():
            acceso = VentanaAcceso(self.root, self.colores, "crear", ruta)
            maestra = acceso.esperar()
            if not maestra:
                return False
            try:
                self.boveda = Boveda.crear(ruta, maestra)
            except ErrorBoveda as exc:
                messagebox.showerror(config.APP_NAME, str(exc))
                return False
            self._ofrecer_migracion()
            self.bloqueada = False
            return True

        estado = {"boveda": None}

        def verificar(contrasena):
            try:
                estado["boveda"] = Boveda.abrir(ruta, contrasena)
                return True
            except ContrasenaIncorrecta:
                return False
            except (BovedaCorrupta, ErrorBoveda) as exc:
                return str(exc)

        acceso = VentanaAcceso(self.root, self.colores, "abrir", ruta, verificar)
        if not acceso.esperar():
            return False

        self.boveda = estado["boveda"]
        self.bloqueada = False
        return True

    def _ofrecer_migracion(self) -> None:
        candidatos = buscar_excel_para_migrar()
        if not candidatos:
            return

        nombres = "\n".join(f"  •  {p.name}" for p in candidatos)
        if not messagebox.askyesno(
                config.APP_NAME,
                f"Se encontraron estos archivos de Excel con contraseñas:\n\n{nombres}\n\n"
                "Se pueden importar a la bóveda cifrada. Los archivos originales "
                "no se modifican.\n\n¿Importarlos ahora?"):
            return

        total = omitidas = 0
        for ruta in candidatos:
            try:
                agregadas, saltadas = self.boveda.importar_excel(ruta)
                total += agregadas
                omitidas += saltadas
            except Exception as exc:
                messagebox.showwarning(config.APP_NAME,
                                       f"No se pudo importar {ruta.name}:\n{exc}")

        if total:
            messagebox.showinfo(
                config.APP_NAME,
                f"Se importaron {total} cuentas ({omitidas} repetidas o vacías se omitieron).\n\n"
                "IMPORTANTE: los Excel originales siguen en texto plano. Cuando "
                "confirmes que todo está bien, bórralos o guárdalos en un lugar seguro.")

    def _construir_ventana(self) -> None:
        ancho = int(self.prefs.get("ancho_ventana", 1180))
        alto = int(self.prefs.get("alto_ventana", 720))
        if not self.prefs.get("geometria_escalada"):
            # La primera vez se convierten las medidas de diseño a píxeles reales;
            # después ya se guardan y se recuperan tal cual.
            ancho, alto = px(ancho), px(alto)
            self.prefs["geometria_escalada"] = True
        # El area de trabajo descuenta la barra de tareas.
        izq, arriba, der, abajo = escala.area_trabajo(self.root)
        marco = px(escala.ALTO_MARCO)
        ancho = min(ancho, der - izq - px(16))
        alto = min(alto, abajo - arriba - marco - px(8))
        self.root.minsize(min(px(940), ancho), min(px(560), alto))

        x = izq + (der - izq - ancho) // 2
        y = max(arriba, arriba + (abajo - arriba - marco - alto) // 2)
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")

        self._menu()
        self.ventana = VentanaPrincipal(self.root, self)

        for evento in ("<Any-KeyPress>", "<Any-Button>", "<Motion>", "<MouseWheel>"):
            self.root.bind_all(evento, self._marcar_actividad, add="+")

    def _menu(self) -> None:
        c = self.colores
        opciones = dict(tearoff=0, bg=c["panel"], fg=c["texto"], bd=0,
                        activebackground=c["seleccion"], activeforeground=c["texto"])
        barra = tk.Menu(self.root, **opciones)

        archivo = tk.Menu(barra, **opciones)
        archivo.add_command(label="Nueva cuenta...\tCtrl+N", command=self.nueva_entrada)
        archivo.add_separator()
        archivo.add_command(label="Carga masiva (pegar texto)...", command=self.importar_texto)
        archivo.add_command(label="Importar desde Excel...", command=lambda: self.importar_archivo("excel"))
        archivo.add_command(label="Importar desde CSV...", command=lambda: self.importar_archivo("csv"))
        archivo.add_separator()
        archivo.add_command(label="Exportar a Excel...", command=lambda: self.exportar("excel"))
        archivo.add_command(label="Exportar a CSV...", command=lambda: self.exportar("csv"))
        archivo.add_separator()
        archivo.add_command(label="Bloquear\tCtrl+L", command=self.bloquear)
        archivo.add_command(label="Salir", command=self.salir)
        barra.add_cascade(label="Archivo", menu=archivo)

        herramientas = tk.Menu(barra, **opciones)
        herramientas.add_command(label="Generador de contraseñas\tCtrl+G",
                                 command=self.abrir_generador)
        herramientas.add_command(label="Análisis de seguridad", command=self.abrir_auditoria)
        herramientas.add_separator()
        herramientas.add_command(label="Cambiar contraseña maestra...",
                                 command=self.cambiar_maestra)
        herramientas.add_command(label="Ajustes...", command=self.abrir_ajustes)
        barra.add_cascade(label="Herramientas", menu=herramientas)

        ayuda = tk.Menu(barra, **opciones)
        ayuda.add_command(label="Atajos de teclado", command=self._mostrar_atajos)
        ayuda.add_command(label="Acerca de", command=self._acerca_de)
        barra.add_cascade(label="Ayuda", menu=ayuda)

        self.root.configure(menu=barra)

    # =============================================================== inactividad
    def _marcar_actividad(self, _evento=None) -> None:
        self._ultimo_uso = time.monotonic()

    def _vigilar_inactividad(self) -> None:
        minutos = int(self.prefs.get("minutos_autobloqueo", 5))
        if minutos > 0 and not self.bloqueada:
            if time.monotonic() - self._ultimo_uso > minutos * 60:
                self.bloquear(automatico=True)
        self._tarea_bloqueo = self.root.after(15000, self._vigilar_inactividad)

    def bloquear(self, automatico: bool = False) -> None:
        if self.bloqueada or not self.boveda:
            return
        self.bloqueada = True
        self.limpiar_portapapeles()
        if self.ventana:
            self.ventana.mostrar_pass = False
            self.ventana.refrescar()
        self.root.withdraw()

        acceso = VentanaAcceso(self.root, self.colores, "desbloquear",
                               verificador=self.boveda.verificar_maestra)
        if acceso.esperar():
            self.bloqueada = False
            self._marcar_actividad()
            self.root.deiconify()
            self.root.lift()
        else:
            self.salir(forzar=True)

    # ============================================================= portapapeles
    def copiar(self, texto: str, etiqueta: str = "Dato") -> None:
        if not texto:
            self.aviso(f"{etiqueta}: no hay nada que copiar.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(texto)
        self.root.update_idletasks()
        self._copiado = texto

        segundos = int(self.prefs.get("segundos_portapapeles", 30))
        if self._tarea_portapapeles:
            self.root.after_cancel(self._tarea_portapapeles)
            self._tarea_portapapeles = None

        if segundos > 0:
            self._tarea_portapapeles = self.root.after(segundos * 1000,
                                                       self.limpiar_portapapeles)
            self.aviso(f"{etiqueta} copiada. Se borrará del portapapeles en {segundos}s.")
        else:
            self.aviso(f"{etiqueta} copiada al portapapeles.")

    def limpiar_portapapeles(self) -> None:
        self._tarea_portapapeles = None
        if not self._copiado:
            return
        try:
            if self.root.clipboard_get() == self._copiado:
                self.root.clipboard_clear()
                self.root.clipboard_append("")
        except tk.TclError:
            pass  # El portapapeles esta vacio o tiene otro formato.
        self._copiado = None

    # =================================================================== avisos
    def aviso(self, texto: str, error: bool = False) -> None:
        if not self.ventana:
            return
        color = self.colores["peligro"] if error else self.colores["texto_tenue"]
        self.ventana.lbl_aviso.configure(text=texto, foreground=color)
        if self._tarea_aviso:
            self.root.after_cancel(self._tarea_aviso)
        self._tarea_aviso = self.root.after(
            5000, lambda: self.ventana.lbl_aviso.configure(text=""))

    # ================================================================= entradas
    def nueva_entrada(self) -> None:
        dialogo = DialogoEntrada(self.root, self.colores, self.prefs,
                                 self.boveda.categorias(), None, self.copiar)
        dialogo.hacer_modal()
        if dialogo.resultado:
            try:
                self.boveda.agregar(Entrada(**dialogo.resultado))
            except ErrorBoveda as exc:
                messagebox.showerror(config.APP_NAME, str(exc))
                return
            self.ventana.refrescar()
            self.aviso("Cuenta guardada.")

    def editar_entrada(self, id_entrada: str) -> None:
        entrada = self.boveda.obtener(id_entrada)
        if not entrada:
            return
        dialogo = DialogoEntrada(self.root, self.colores, self.prefs,
                                 self.boveda.categorias(), entrada, self.copiar)
        dialogo.hacer_modal()
        if dialogo.resultado:
            try:
                self.boveda.actualizar(id_entrada, **dialogo.resultado)
            except ErrorBoveda as exc:
                messagebox.showerror(config.APP_NAME, str(exc))
                return
            self.ventana.refrescar()
            self.aviso("Cambios guardados.")

    def eliminar_entradas(self, ids: list[str]) -> None:
        if not ids:
            self.aviso("Selecciona al menos una cuenta.")
            return
        entrada = self.boveda.obtener(ids[0]) if len(ids) == 1 else None
        if entrada is not None:
            pregunta = f"¿Eliminar la cuenta de \"{entrada.sitio}\"?\n\nNo se puede deshacer."
        else:
            pregunta = f"¿Eliminar {len(ids)} cuentas seleccionadas?\n\nNo se puede deshacer."

        if not messagebox.askyesno(config.APP_NAME, pregunta, icon="warning"):
            return
        borradas = self.boveda.eliminar(ids)
        self.ventana.seleccion_actual = None
        self.ventana.refrescar()
        self.aviso(f"{borradas} cuenta(s) eliminada(s).")

    # ============================================================== herramientas
    def abrir_generador(self) -> None:
        dialogo = DialogoGenerador(self.root, self.colores, self.prefs, self.copiar)
        dialogo.hacer_modal()
        config.guardar_preferencias(self.prefs)

    def abrir_auditoria(self) -> None:
        dialogo = DialogoAuditoria(self.root, self.colores, self.boveda,
                                   al_editar=self.editar_entrada)
        dialogo.hacer_modal()
        self.ventana.refrescar()

    def cambiar_maestra(self) -> None:
        dialogo = DialogoCambiarMaestra(self.root, self.colores,
                                        self.boveda.verificar_maestra)
        dialogo.hacer_modal()
        if dialogo.resultado:
            try:
                self.boveda.cambiar_maestra(dialogo.resultado)
            except ErrorBoveda as exc:
                messagebox.showerror(config.APP_NAME, str(exc))
                return
            messagebox.showinfo(config.APP_NAME,
                                "Contraseña maestra actualizada.\n"
                                "La bóveda se volvio a cifrar con la nueva llave.")

    def abrir_ajustes(self) -> None:
        dialogo = DialogoAjustes(self.root, self.colores, self.prefs,
                                 str(config.ruta_vault()))
        dialogo.hacer_modal()
        if not dialogo.resultado:
            return

        tema_anterior = self.prefs.get("tema")
        idioma_anterior = self.prefs.get("idioma")
        self.prefs.update(dialogo.resultado)
        config.guardar_preferencias(self.prefs)

        cambio_tema = dialogo.resultado.get("tema") != tema_anterior
        cambio_idioma = dialogo.resultado.get("idioma") != idioma_anterior

        if cambio_idioma:
            i18n.set_idioma(self.prefs.get("idioma", "auto"))

        if cambio_tema or cambio_idioma:
            self._recargar_tema()
        self.aviso(i18n.t("success"))

    def _recargar_tema(self) -> None:
        self.colores = tema.aplicar(self.root, self.prefs.get("tema", "oscuro"))
        seleccion = self.ventana.seleccion_actual
        busqueda = self.ventana.var_busqueda.get()
        categoria, favoritos = self.ventana.filtro_categoria, self.ventana.solo_favoritos

        self.ventana.destroy()
        self._menu()
        self.ventana = VentanaPrincipal(self.root, self)
        self.ventana.filtro_categoria = categoria
        self.ventana.solo_favoritos = favoritos
        self.ventana.var_busqueda.set(busqueda)
        self.ventana.seleccion_actual = seleccion
        self.ventana.refrescar()

    # ============================================================ importar/exportar
    def importar_texto(self) -> None:
        dialogo = DialogoImportarTexto(self.root, self.colores)
        dialogo.hacer_modal()
        if not dialogo.resultado:
            return
        datos = dialogo.resultado
        try:
            agregadas, omitidas = self.boveda.importar_texto(
                datos["texto"], datos["separador"], datos["omitir"])
        except ErrorBoveda as exc:
            messagebox.showerror(config.APP_NAME, str(exc))
            return
        self.ventana.refrescar()
        messagebox.showinfo(config.APP_NAME,
                            f"Se importaron {agregadas} cuentas.\n"
                            f"Líneas omitidas o repetidas: {omitidas}")

    def importar_archivo(self, formato: str) -> None:
        tipos = ([("Libros de Excel", "*.xlsx *.xlsm")] if formato == "excel"
                 else [("Archivos CSV", "*.csv *.txt")])
        ruta = filedialog.askopenfilename(title="Selecciona el archivo",
                                          filetypes=tipos + [("Todos", "*.*")])
        if not ruta:
            return
        try:
            if formato == "excel":
                agregadas, omitidas = self.boveda.importar_excel(ruta)
            else:
                agregadas, omitidas = self.boveda.importar_csv(ruta)
        except Exception as exc:
            messagebox.showerror(config.APP_NAME, f"No se pudo importar:\n{exc}")
            return
        self.ventana.refrescar()
        messagebox.showinfo(config.APP_NAME,
                            f"Se importaron {agregadas} cuentas.\n"
                            f"Filas omitidas o repetidas: {omitidas}")

    def exportar(self, formato: str) -> None:
        if not messagebox.askyesno(
                config.APP_NAME,
                "El archivo exportado queda SIN CIFRAR: cualquiera que lo abra vera "
                "todas tus contraseñas.\n\nGuárdalo solo en un lugar seguro.\n\n¿Continuar?",
                icon="warning"):
            return

        extension = ".xlsx" if formato == "excel" else ".csv"
        ruta = filedialog.asksaveasfilename(
            title="Guardar copia sin cifrar", defaultextension=extension,
            initialfile=f"contraseñas_export{extension}",
            filetypes=[("Excel", "*.xlsx")] if formato == "excel" else [("CSV", "*.csv")])
        if not ruta:
            return
        try:
            total = (self.boveda.exportar_excel(ruta) if formato == "excel"
                     else self.boveda.exportar_csv(ruta))
        except Exception as exc:
            messagebox.showerror(config.APP_NAME, f"No se pudo exportar:\n{exc}")
            return
        messagebox.showinfo(config.APP_NAME, f"Se exportaron {total} cuentas a:\n{ruta}")

    # ==================================================================== ayuda
    def _mostrar_atajos(self) -> None:
        messagebox.showinfo(
            "Atajos de teclado",
            "Ctrl + N      Nueva cuenta\n"
            "Ctrl + E      Editar la cuenta seleccionada\n"
            "Ctrl + C      Copiar contraseña\n"
            "Ctrl + U      Copiar usuario\n"
            "Ctrl + F      Ir al buscador\n"
            "Ctrl + G      Generador de contraseñas\n"
            "Ctrl + L      Bloquear la bóveda\n"
            "Supr          Eliminar selección\n"
            "Doble clic    Editar\n"
            "Clic derecho  Menú de acciones\n"
            "F5            Refrescar")

    def _acerca_de(self) -> None:
        from .crypto import HAY_ARGON2
        kdf = "Argon2id" if HAY_ARGON2 else "scrypt"
        messagebox.showinfo(
            f"Acerca de {config.APP_NAME}",
            f"{config.APP_NAME} {config.APP_VERSION}\n\n"
            f"Cifrado:  AES-256-GCM\n"
            f"Derivación de llave:  {kdf}\n"
            f"Generador:  CSPRNG del sistema (secrets)\n\n"
            f"Bóveda:\n{config.ruta_vault()}\n\n"
            "La contraseña maestra no se guarda en ningún lado.")

    # ===================================================================== salir
    def salir(self, forzar: bool = False) -> None:
        self.limpiar_portapapeles()
        try:
            if self.root.state() == "normal":
                self.prefs["ancho_ventana"] = self.root.winfo_width()
                self.prefs["alto_ventana"] = self.root.winfo_height()
            config.guardar_preferencias(self.prefs)
        except tk.TclError:
            pass
        self.root.quit()
        self.root.destroy()


def main() -> None:
    App().ejecutar()
