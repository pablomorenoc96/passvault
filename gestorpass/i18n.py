"""Sistema de internacionalización (i18n): soporte para español e inglés."""
from __future__ import annotations

import locale
import sys

_IDIOMA_ACTUAL = "es"

TEXTS: dict[str, dict[str, str]] = {
    "es": {
        # App & General
        "app_title": "PassVault",
        "save": "Guardar",
        "cancel": "Cancelar",
        "close": "Cerrar",
        "copy": "Copiar",
        "copied": "¡Copiado!",
        "delete": "Eliminar",
        "edit": "Editar",
        "error": "Error",
        "success": "Éxito",
        "warning": "Aviso",
        "confirm": "Confirmar",
        "yes": "Sí",
        "no": "No",
        "search_placeholder": "Buscar por sitio, usuario, URL o notas...",
        "status_accounts": "{total} cuentas ({favs} favoritas)",
        "status_filtered": "{count} de {total} cuentas",

        # Menús y Barra Superior
        "btn_new": "+ Nueva cuenta",
        "btn_generator": "🔑 Generador",
        "btn_audit": "🛡️ Análisis de seguridad",
        "btn_settings": "⚙️ Ajustes",
        "btn_lock": "🔒 Bloquear",
        "filter_all": "Todas las categorías",
        "filter_favorites": "⭐ Favoritos",
        "filter_uncategorized": "Sin categoría",

        # Columnas de la tabla
        "col_fav": "★",
        "col_site": "Sitio o servicio",
        "col_user": "Usuario / Correo",
        "col_pass": "Contraseña",
        "col_cat": "Categoría",
        "col_notes": "Notas",

        # Menú contextual (clic derecho)
        "ctx_copy_pass": "Copiar contraseña",
        "ctx_copy_user": "Copiar usuario",
        "ctx_open_url": "Abrir sitio web",
        "ctx_edit": "Editar",
        "ctx_duplicate": "Duplicar",
        "ctx_delete": "Eliminar",

        # Pantalla de Acceso (ui_acceso)
        "access_create_title": "Crear nueva bóveda",
        "access_create_desc": "Establece una contraseña maestra segura para cifrar todos tus datos con AES-256-GCM.",
        "access_open_title": "Desbloquear PassVault",
        "access_open_desc": "Ingresa tu contraseña maestra para descifrar tu bóveda.",
        "access_master_label": "Contraseña maestra",
        "access_confirm_label": "Confirmar contraseña maestra",
        "access_btn_create": "Crear bóveda cifrada",
        "access_btn_unlock": "Desbloquear",
        "access_err_mismatch": "Las contraseñas no coinciden.",
        "access_err_empty": "La contraseña no puede estar vacía.",
        "access_err_short": "Por seguridad, la contraseña maestra debe tener al menos 8 caracteres.",
        "access_err_wrong": "Contraseña maestra incorrecta. Inténtalo de nuevo.",
        "access_err_corrupt": "El archivo de bóveda está dañado o no tiene un formato válido.",

        # Formulario de Entrada (ui_entrada)
        "entry_new_title": "Nueva cuenta",
        "entry_edit_title": "Editar cuenta",
        "entry_site_label": "SITIO O SERVICIO *",
        "entry_user_label": "USUARIO O CORREO",
        "entry_pass_label": "CONTRASEÑA",
        "entry_url_label": "SITIO WEB (URL)",
        "entry_cat_label": "CATEGORÍA",
        "entry_notes_label": "NOTAS",
        "entry_fav_label": "Marcar como favorita",
        "entry_err_site_required": "Por favor escribe al menos el sitio o servicio.",
        "entry_history_btn": "Historial de contraseñas",
        "entry_history_title": "Historial de contraseñas anteriores",
        "entry_history_empty": "No hay contraseñas anteriores registradas.",

        # Generador (ui_generador)
        "gen_title": "Generador de contraseñas",
        "gen_subtitle": "Criptográficamente seguras con el módulo secrets de Python.",
        "gen_tab_random": "Aleatoria",
        "gen_tab_word": "Desde palabra base",
        "gen_base_word_label": "PALABRA BASE O FRASE",
        "gen_base_word_placeholder": "Ej. guitarra, castillo, cafe...",
        "gen_opt_leet": "Sustituciones leet (@, 3, 1, 0, $)",
        "gen_opt_case": "Variar mayúsculas y minúsculas",
        "gen_opt_suffix": "Añadir sufijo seguro (números y símbolos)",
        "gen_length": "Longitud:",
        "gen_uppercase": "Mayúsculas (A-Z)",
        "gen_lowercase": "Minúsculas (a-z)",
        "gen_numbers": "Números (0-9)",
        "gen_symbols": "Símbolos (!@#$...)",
        "gen_no_ambiguous": "Evitar confusos (l, 1, I, O, 0)",
        "gen_copy_btn": "Copiar",
        "gen_use_btn": "Usar esta contraseña",
        "gen_copied_tooltip": "Contraseña copiada al portapapeles",

        # Fortaleza de contraseña (fortaleza)
        "warn_empty": "Sin contraseña",
        "strength_empty": "Vacía",
        "strength_very_weak": "Muy débil",
        "strength_weak": "Débil",
        "strength_fair": "Aceptable",
        "strength_strong": "Fuerte",
        "strength_very_strong": "Muy fuerte",
        "time_instant": "instantáneo",
        "time_seconds": "segundos",
        "time_minutes": "minutos",
        "time_hours": "horas",
        "time_days": "días",
        "time_years": "años",
        "time_thousand_years": "mil años",
        "time_million_years": "millones de años",
        "time_billion_years": "mil millones de años",
        "time_trillion_years": "billones de años",
        "time_eternal": "prácticamente eterno",

        # Diálogo de Ajustes (ui_dialogos)
        "settings_title": "Ajustes de PassVault",
        "settings_lang_label": "Idioma / Language",
        "settings_theme_label": "Tema visual",
        "settings_theme_dark": "Oscuro",
        "settings_theme_light": "Claro",
        "settings_autolock_label": "Bloqueo automático por inactividad",
        "settings_autolock_min": "{m} minutos",
        "settings_autolock_never": "Nunca",
        "settings_clipboard_label": "Limpieza del portapapeles",
        "settings_clipboard_sec": "{s} segundos",
        "settings_clipboard_never": "No limpiar",
        "settings_btn_change_master": "Cambiar contraseña maestra...",
        "settings_btn_export_csv": "Exportar cuentas a CSV...",
        "settings_btn_export_excel": "Exportar cuentas a Excel...",
        "settings_btn_import": "Importar desde archivo o texto...",

        # Cambio de Maestra
        "master_title": "Cambiar contraseña maestra",
        "master_current": "Contraseña maestra actual",
        "master_new": "Nueva contraseña maestra",
        "master_confirm": "Confirmar nueva contraseña",
        "master_success": "Contraseña maestra cambiada exitosamente.",

        # Auditoría de Seguridad
        "audit_title": "Análisis de seguridad",
        "audit_card_total": "Cuentas guardadas",
        "audit_card_weak": "Débiles",
        "audit_card_reused": "Reutilizadas",
        "audit_card_empty": "Sin contraseña",
        "audit_card_health": "Salud general",
        "audit_col_issue": "Problema",
        "audit_col_site": "Sitio",
        "audit_col_user": "Usuario",
        "audit_col_detail": "Detalle",
        "audit_hint_edit": "Doble clic en una fila para corregirla.",
        "audit_issue_empty": "Sin contraseña",
        "audit_detail_empty": "La entrada no guarda contraseña",
        "audit_issue_weak": "Contraseña {nivel}",
        "audit_issue_reused": "Contraseña repetida",
        "audit_detail_reused": "Se repite en: {sitios}",

        # Diálogos de Confirmación
        "confirm_delete_title": "Eliminar cuenta",
        "confirm_delete_msg": "¿Estás seguro de que deseas eliminar '{site}'?",
        "export_success_title": "Exportación completada",
        "export_success_msg": "Se exportaron {count} cuentas exitosamente a:\n{path}",
        "import_success_title": "Importación completada",
        "import_success_msg": "Se importaron {agregadas} cuentas nuevas ({omitidas} omitidas por duplicadas o vacías).",
    },
    "en": {
        # App & General
        "app_title": "PassVault",
        "save": "Save",
        "cancel": "Cancel",
        "close": "Close",
        "copy": "Copy",
        "copied": "Copied!",
        "delete": "Delete",
        "edit": "Edit",
        "error": "Error",
        "success": "Success",
        "warning": "Warning",
        "confirm": "Confirm",
        "yes": "Yes",
        "no": "No",
        "search_placeholder": "Search by site, username, URL or notes...",
        "status_accounts": "{total} accounts ({favs} favorites)",
        "status_filtered": "{count} of {total} accounts",

        # Menus and Top Bar
        "btn_new": "+ New Account",
        "btn_generator": "🔑 Generator",
        "btn_audit": "🛡️ Security Audit",
        "btn_settings": "⚙️ Settings",
        "btn_lock": "🔒 Lock",
        "filter_all": "All categories",
        "filter_favorites": "⭐ Favorites",
        "filter_uncategorized": "Uncategorized",

        # Table Columns
        "col_fav": "★",
        "col_site": "Site or Service",
        "col_user": "Username / Email",
        "col_pass": "Password",
        "col_cat": "Category",
        "col_notes": "Notes",

        # Context Menu
        "ctx_copy_pass": "Copy password",
        "ctx_copy_user": "Copy username",
        "ctx_open_url": "Open website",
        "ctx_edit": "Edit",
        "ctx_duplicate": "Duplicate",
        "ctx_delete": "Delete",

        # Access / Login Screen
        "access_create_title": "Create New Vault",
        "access_create_desc": "Set a strong master password to encrypt all your data with AES-256-GCM.",
        "access_open_title": "Unlock PassVault",
        "access_open_desc": "Enter your master password to decrypt your vault.",
        "access_master_label": "Master password",
        "access_confirm_label": "Confirm master password",
        "access_btn_create": "Create Encrypted Vault",
        "access_btn_unlock": "Unlock",
        "access_err_mismatch": "Passwords do not match.",
        "access_err_empty": "Password cannot be empty.",
        "access_err_short": "For security, master password must be at least 8 characters.",
        "access_err_wrong": "Incorrect master password. Please try again.",
        "access_err_corrupt": "The vault file is corrupted or not a valid format.",

        # Entry Form
        "entry_new_title": "New Account",
        "entry_edit_title": "Edit Account",
        "entry_site_label": "SITE OR SERVICE *",
        "entry_user_label": "USERNAME OR EMAIL",
        "entry_pass_label": "PASSWORD",
        "entry_url_label": "WEBSITE (URL)",
        "entry_cat_label": "CATEGORY",
        "entry_notes_label": "NOTES",
        "entry_fav_label": "Mark as favorite",
        "entry_err_site_required": "Please enter at least the site or service name.",
        "entry_history_btn": "Password history",
        "entry_history_title": "Previous password history",
        "entry_history_empty": "No previous passwords recorded.",

        # Generator
        "gen_title": "Password Generator",
        "gen_subtitle": "Cryptographically secure via Python's secrets CSPRNG.",
        "gen_tab_random": "Random",
        "gen_tab_word": "From base word",
        "gen_base_word_label": "BASE WORD OR PHRASE",
        "gen_base_word_placeholder": "E.g. guitar, castle, coffee...",
        "gen_opt_leet": "Leet substitutions (@, 3, 1, 0, $)",
        "gen_opt_case": "Vary uppercase & lowercase",
        "gen_opt_suffix": "Add secure suffix (numbers & symbols)",
        "gen_length": "Length:",
        "gen_uppercase": "Uppercase (A-Z)",
        "gen_lowercase": "Lowercase (a-z)",
        "gen_numbers": "Numbers (0-9)",
        "gen_symbols": "Symbols (!@#$...)",
        "gen_no_ambiguous": "Avoid ambiguous (l, 1, I, O, 0)",
        "gen_copy_btn": "Copy",
        "gen_use_btn": "Use this password",
        "gen_copied_tooltip": "Password copied to clipboard",

        # Password Strength
        "warn_empty": "No password",
        "strength_empty": "Empty",
        "strength_very_weak": "Very Weak",
        "strength_weak": "Weak",
        "strength_fair": "Fair",
        "strength_strong": "Strong",
        "strength_very_strong": "Very Strong",
        "time_instant": "instant",
        "time_seconds": "seconds",
        "time_minutes": "minutes",
        "time_hours": "hours",
        "time_days": "days",
        "time_years": "years",
        "time_thousand_years": "thousand years",
        "time_million_years": "million years",
        "time_billion_years": "billion years",
        "time_trillion_years": "trillion years",
        "time_eternal": "practically eternal",

        # Settings Dialog
        "settings_title": "PassVault Settings",
        "settings_lang_label": "Language / Idioma",
        "settings_theme_label": "Theme",
        "settings_theme_dark": "Dark",
        "settings_theme_light": "Light",
        "settings_autolock_label": "Auto-lock on inactivity",
        "settings_autolock_min": "{m} minutes",
        "settings_autolock_never": "Never",
        "settings_clipboard_label": "Clipboard clear timeout",
        "settings_clipboard_sec": "{s} seconds",
        "settings_clipboard_never": "Do not clear",
        "settings_btn_change_master": "Change master password...",
        "settings_btn_export_csv": "Export accounts to CSV...",
        "settings_btn_export_excel": "Export accounts to Excel...",
        "settings_btn_import": "Import from file or text...",

        # Change Master
        "master_title": "Change Master Password",
        "master_current": "Current master password",
        "master_new": "New master password",
        "master_confirm": "Confirm new master password",
        "master_success": "Master password changed successfully.",

        # Security Audit
        "audit_title": "Security Audit",
        "audit_card_total": "Stored Accounts",
        "audit_card_weak": "Weak",
        "audit_card_reused": "Reused",
        "audit_card_empty": "No Password",
        "audit_card_health": "Overall Health",
        "audit_col_issue": "Issue",
        "audit_col_site": "Site",
        "audit_col_user": "Username",
        "audit_col_detail": "Details",
        "audit_hint_edit": "Double-click a row to edit.",
        "audit_issue_empty": "No password",
        "audit_detail_empty": "This entry has no password stored",
        "audit_issue_weak": "{nivel} password",
        "audit_issue_reused": "Reused password",
        "audit_detail_reused": "Reused across: {sitios}",

        # Confirmation Dialogs
        "confirm_delete_title": "Delete Account",
        "confirm_delete_msg": "Are you sure you want to delete '{site}'?",
        "export_success_title": "Export Completed",
        "export_success_msg": "{count} accounts exported successfully to:\n{path}",
        "import_success_title": "Import Completed",
        "import_success_msg": "Imported {agregadas} new accounts ({omitidas} skipped duplicates or empty).",
    },
}


def detectar_idioma_sistema() -> str:
    """Detecta si el sistema operativo está en español o inglés."""
    try:
        if sys.platform == "win32":
            import ctypes
            lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0xFF
            if lang_id == 0x0A:  # Español (es-ES, es-MX, etc.)
                return "es"
            return "en"
        loc = locale.getdefaultlocale()[0]
        if loc and loc.lower().startswith("es"):
            return "es"
    except Exception:
        pass
    return "en"


def set_idioma(idioma: str) -> None:
    """Establece el idioma activo ('es', 'en' o 'auto')."""
    global _IDIOMA_ACTUAL
    if idioma == "auto":
        _IDIOMA_ACTUAL = detectar_idioma_sistema()
    elif idioma in TEXTS:
        _IDIOMA_ACTUAL = idioma
    else:
        _IDIOMA_ACTUAL = "en"


def get_idioma() -> str:
    """Devuelve el código del idioma activo ('es' o 'en')."""
    return _IDIOMA_ACTUAL


def t(clave: str, **kwargs) -> str:
    """Obtiene la traducción de ``clave`` en el idioma activo."""
    idioma = _IDIOMA_ACTUAL if _IDIOMA_ACTUAL in TEXTS else "en"
    dicc = TEXTS.get(idioma, TEXTS["en"])
    texto = dicc.get(clave, TEXTS["en"].get(clave, clave))
    if kwargs:
        try:
            return texto.format(**kwargs)
        except Exception:
            return texto
    return texto
