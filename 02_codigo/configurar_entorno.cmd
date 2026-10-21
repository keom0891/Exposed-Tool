@echo off
rem Configuracion compartida por los accesos de ejecucion.
rem GAIA_ENV puede definirse externamente o ajustarse en este archivo.
if not defined GAIA_ENV set "GAIA_ENV=C:\ProgramData\miniforge3\envs\climada_env"
if not exist "%GAIA_ENV%\python.exe" (
 echo No se encontro Python en GAIA_ENV. Revise 02_codigo/configurar_entorno.cmd.
 exit /b 1
)
set "PYTHONNOUSERSITE=1"
set "PYTHONDONTWRITEBYTECODE=1"
set "PATH=%GAIA_ENV%\Library\bin;%GAIA_ENV%;%PATH%"
if exist "%GAIA_ENV%\Library\share\gdal" set "GDAL_DATA=%GAIA_ENV%\Library\share\gdal"
if exist "%GAIA_ENV%\Library\share\proj" set "PROJ_DATA=%GAIA_ENV%\Library\share\proj"
exit /b 0
