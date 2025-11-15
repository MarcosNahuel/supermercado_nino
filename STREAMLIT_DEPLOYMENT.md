# Despliegue en Streamlit Cloud

## Configuración para Streamlit Cloud (share.streamlit.io)

### Datos requeridos:

1. **Main file path:** `dashboard_cientifico.py`
2. **Repository:** Tu repositorio de GitHub
3. **Branch:** `main`

### Estructura mínima del repositorio:

```
supermercado_nino definitivo claude/
├── dashboard_cientifico.py       (ARCHIVO PRINCIPAL)
├── requirements.txt              (DEPENDENCIAS)
├── data/
│   ├── app_dataset/              (DATOS NECESARIOS)
│   │   ├── kpi_categoria.parquet
│   │   ├── kpi_dia.parquet
│   │   ├── kpi_diario.parquet
│   │   ├── kpi_hora.parquet
│   │   ├── kpi_medio_pago.parquet
│   │   ├── kpi_periodo.parquet
│   │   ├── kpi_semana.parquet
│   │   ├── alcance_dataset.parquet
│   │   ├── kpis_base.parquet
│   │   ├── pareto_prod_global.parquet
│   │   ├── pareto_cat_global.parquet
│   │   ├── reglas.parquet
│   │   ├── combos_recomendados.parquet
│   │   ├── adjacency_pairs.parquet
│   │   ├── clusters_tickets.parquet
│   │   ├── clusters_departamento.parquet
│   │   ├── rentabilidad_ticket.parquet
│   │   └── comprobantes_ventas_horario.csv (si existe)
│   └── processed/                (OPCIONAL - no se sube)
├── .gitignore                    (CONFIGURADO)
└── STREAMLIT_DEPLOYMENT.md       (ESTE ARCHIVO)
```

### Pasos para desplegar:

1. **Ve a:** https://share.streamlit.io
2. **Inicia sesión** con tu cuenta de GitHub
3. **Haz clic en** "New app"
4. **Completa los campos:**
   - **Repository:** `user/supermercado_nino definitivo claude`
   - **Branch:** `main`
   - **Main file path:** `dashboard_cientifico.py`
5. **Haz clic en** "Deploy"

### Nota importante sobre .gitignore:

El archivo `.gitignore` está configurado para:
- ✅ **Incluir:** `data/app_dataset/` (datos necesarios para el dashboard)
- ❌ **Excluir:** `data/processed/`, `legacy/`, `docs/`, `scripts/`, etc.

Esto mantiene el repositorio limpio y solo sube lo necesario.

### Estructura de dependencias (requirements.txt):

```
streamlit>=1.28.0      # Framework web
pandas>=2.0.0          # Manipulación de datos
numpy>=1.24.0          # Operaciones numéricas
plotly>=5.17.0         # Gráficos interactivos
pyarrow>=14.0.0        # Lectura de archivos parquet
python-dateutil        # Manejo de fechas
scikit-learn           # Machine learning básico
scipy                  # Operaciones científicas
```

### Solución de problemas:

**Si falta módulo X:**
- Agregarlo a `requirements.txt`
- Hacer push a GitHub
- Streamlit Cloud redeployará automáticamente

**Si falta datos:**
- Verificar que `data/app_dataset/` esté en el repositorio
- Verificar que `.gitignore` no excluya esa carpeta
- Hacer commit y push

**Si tarda mucho en cargar:**
- Verificar tamaño total del repositorio
- Los archivos parquet pueden ser grandes
- Considerar comprimir datos si es necesario
