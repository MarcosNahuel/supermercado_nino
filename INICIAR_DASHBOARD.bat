@echo off
REM ============================================================================
REM Iniciar Dashboard Científico - Supermercado NINO
REM ============================================================================

echo.
echo ============================================================================
echo   DASHBOARD CIENTIFICO - SUPERMERCADO NINO
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

REM Iniciar Streamlit
echo [INFO] Iniciando dashboard en http://localhost:8501
echo.
streamlit run dashboard_cientifico.py

pause
