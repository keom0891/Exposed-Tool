@echo off
setlocal
cd /d "%~dp0"
call "02_codigo\configurar_entorno.cmd"
if errorlevel 1 goto fallo
cd /d "%~dp002_codigo"
"%GAIA_ENV%\python.exe" -s analizar.py
if errorlevel 1 goto fallo
"%GAIA_ENV%\python.exe" -s sensibilidad.py
if errorlevel 1 goto fallo
"%GAIA_ENV%\python.exe" -s verificar.py
if errorlevel 1 goto fallo
"%GAIA_ENV%\python.exe" -s preparar_entrega.py
if errorlevel 1 goto fallo
echo.
echo Analisis completo. Abra index.html en la carpeta principal.
pause
exit /b 0
:fallo
echo El proceso se detuvo. Revise el mensaje anterior antes de usar las salidas.
pause
exit /b 1
