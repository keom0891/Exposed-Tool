@echo off
setlocal
cd /d "%~dp0"
call "02_codigo\configurar_entorno.cmd"
if errorlevel 1 goto fallo
cd /d "%~dp002_codigo"
"%GAIA_ENV%\python.exe" -s preparar_entrega.py
if errorlevel 1 goto fallo
echo.
echo Dashboard actualizado. Abra index.html en la carpeta principal.
pause
exit /b 0
:fallo
echo El proceso se detuvo. Revise el mensaje anterior antes de usar las salidas.
pause
exit /b 1
