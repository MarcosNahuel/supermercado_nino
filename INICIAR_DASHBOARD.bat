@echo off
echo ========================================
echo Dashboard Supermercado NINO
echo Instalacion e Inicio Automatico
echo ========================================
echo.

REM Navegar a la carpeta del proyecto
cd /d "%~dp0"

echo [1/3] Verificando instalacion de Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado
    echo Por favor instala Python 3.8+ desde python.org
    pause
    exit /b 1
)
echo OK - Python instalado
echo.

echo [2/3] Instalando dependencias...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron instalar las dependencias
    pause
    exit /b 1
)
echo OK - Dependencias instaladas
echo.

echo [3/3] Iniciando Dashboard Streamlit...
echo.
echo ========================================
echo Dashboard disponible en:
echo http://localhost:8501
echo ========================================
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

streamlit run dashboard_cientifico.py

pause
