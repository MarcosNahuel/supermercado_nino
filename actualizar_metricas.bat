@echo off
REM ============================================================================
REM Script de Actualización Automática de Métricas - Supermercado NINO
REM ============================================================================
REM
REM Este script ejecuta el pipeline completo cuando actualizas
REM SERIE_COMPROBANTES_COMPLETOS.csv
REM
REM Uso: Simplemente haz doble clic en este archivo
REM
REM ============================================================================

echo.
echo ============================================================================
echo   ACTUALIZACION AUTOMATICA DE METRICAS - SUPERMERCADO NINO
echo ============================================================================
echo.

REM Activar entorno virtual si existe
if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activando entorno virtual...
    call .venv\Scripts\activate.bat
) else (
    echo [ADVERTENCIA] No se encontro entorno virtual en .venv
    echo [INFO] Usando Python del sistema...
)

REM Ejecutar script de actualización
python actualizar_metricas.py

REM Verificar si hubo error
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] El proceso fallo con codigo de error %ERRORLEVEL%
    echo.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [EXITO] Proceso completado exitosamente
echo.
pause
