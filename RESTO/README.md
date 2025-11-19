# Carpeta RESTO - Archivos Archivados

Esta carpeta contiene archivos y versiones anteriores que no son necesarios para el funcionamiento del sistema principal, pero se conservan por motivos históricos o de referencia.

## Contenido

### 📂 Carpetas Principales

- **`app/`** - Versión anterior del dashboard (Oct 2024)
  - Contiene `dashboard.py` (versión previa a la reorganización)

- **`final/`** - Versión anterior de la aplicación
  - `streamlit_app/dashboard_cientifico.py` (reemplazado por el archivo en raíz)

- **`legacy/`** - Archivos y código legacy
  - `apps/` - Aplicaciones antiguas (incluyendo versión con Supabase)
  - `data/` - Datasets de prueba y desarrollo
  - `outputs/` - Salidas y reportes históricos
  - `pipelines/` - Pipelines antiguos (FASE1_ANALISIS_COMPLETO.py)
  - `scripts/` - Scripts de desarrollo y construcción
  - `tests/` - Tests antiguos

- **`docs/`** - Documentación archivada
  - `archivados/` - Documentos históricos
  - `entregables/` - Reportes y entregables anteriores
  - `estrategias/` - Documentación de estrategias implementadas
  - `guias/` - Guías técnicas antiguas
  - `validacion/` - Documentos de validación de fases anteriores

- **`archivos_misc/`** - Scripts y archivos diversos
  - `analisis_combos_inteligentes.py`
  - `generar_pdf_chrome.py`
  - `generar_pdf_informe.py`
  - `COMBOS_INTELIGENTES_FINAL.md`
  - `COMBOS_INTELIGENTES_PARA_PROMOVER.md`
  - `INICIAR_DASHBOARD.bat` (versión antigua)
  - `Análisis del Supermercado en Chacras (Mendoza) y Estrategias de Mejora.docx`

- **`.claude/`** - Configuraciones de Claude Code
- **`.devcontainer/`** - Configuraciones de contenedor de desarrollo
- **`__pycache__/`** - Archivos de cache de Python

## ⚠️ Importante

**NO elimines esta carpeta** sin antes revisar su contenido. Contiene:
- Versiones históricas del código
- Documentación de decisiones técnicas
- Scripts de análisis exploratorio
- Datos de prueba y desarrollo

Si necesitas recuperar alguna funcionalidad o referencia histórica, búscala aquí primero.

## 🗑️ Limpieza Futura

Archivos que pueden eliminarse de forma segura en el futuro:
- `__pycache__/` - Cache de Python (regenerable)
- `.claude/`, `.devcontainer/` - Configuraciones de IDE (si no se usan)

Archivos a conservar permanentemente:
- `legacy/` - Código histórico con lógica importante
- `docs/` - Documentación de decisiones y validaciones
- `final/` - Última versión estable antes de la reorganización
