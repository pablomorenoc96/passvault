@echo off
setlocal EnableExtensions
title Gestor de Contrasenas

rem ==========================================================================
rem  Arranca el Gestor de Contrasenas.
rem  Se puede ejecutar con doble clic desde cualquier sitio: siempre trabaja
rem  sobre la carpeta donde esta este .bat.
rem ==========================================================================

cd /d "%~dp0"

if not exist "gestor_passwords.py" goto :sin_programa

rem ---- 1. Localizar Python -------------------------------------------------
rem  PY  = interprete de consola (para comprobar e instalar librerias)
rem  PYW = interprete sin consola (para arrancar la ventana sin cuadro negro)
set "PY="
set "PYW="

where py.exe >nul 2>&1
if not errorlevel 1 set "PY=py.exe"
if defined PY goto :buscar_pyw

where python.exe >nul 2>&1
if not errorlevel 1 set "PY=python.exe"

:buscar_pyw
where pyw.exe >nul 2>&1
if not errorlevel 1 set "PYW=pyw.exe"
if defined PYW goto :comprobar_librerias

where pythonw.exe >nul 2>&1
if not errorlevel 1 set "PYW=pythonw.exe"

:comprobar_librerias
if not defined PY goto :sin_python

rem ---- 2. Comprobar las librerias -------------------------------------------
%PY% -c "import cryptography, argon2, openpyxl" >nul 2>&1
if not errorlevel 1 goto :arrancar

echo.
echo  Faltan librerias necesarias. Se instalaran una sola vez...
echo.
%PY% -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto :fallo_pip

%PY% -c "import cryptography, argon2, openpyxl" >nul 2>&1
if errorlevel 1 goto :fallo_pip

echo.
echo  Listo. Abriendo el gestor...

rem ---- 3. Arrancar ----------------------------------------------------------
:arrancar
if defined PYW (
    rem  start "" deja la ventana suelta y cierra esta consola al instante.
    start "" %PYW% "gestor_passwords.py"
) else (
    rem  Sin pythonw queda una consola detras: es feo pero funciona igual.
    %PY% "gestor_passwords.py"
)
exit /b 0

rem ---- Errores --------------------------------------------------------------
:sin_programa
echo.
echo  ERROR: no se encuentra "gestor_passwords.py".
echo  Este archivo .bat tiene que estar en la misma carpeta que el programa.
echo.
pause
exit /b 1

:sin_python
echo.
echo  ERROR: no se encuentra Python en este equipo.
echo.
echo  Instalalo desde https://www.python.org/downloads/
echo  y marca la casilla "Add Python to PATH" durante la instalacion.
echo.
pause
exit /b 1

:fallo_pip
echo.
echo  ERROR: no se pudieron instalar las librerias.
echo.
echo  Prueba a abrir una consola en esta carpeta y ejecutar:
echo      %PY% -m pip install -r requirements.txt
echo.
pause
exit /b 1
