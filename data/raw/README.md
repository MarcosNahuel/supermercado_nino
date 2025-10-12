# 📄 Raw Data Files

## Archivos Finales (Producción)

### ✅ SERIE_COMPROBANTES_COMPLETOS2.csv
- **Periodo:** Octubre 2024 - Octubre 2025 (13 meses)
- **Registros:** 2,993,041 líneas
- **Tamaño:** 395 MB
- **Formato:** CSV delimitado por `;`, decimal con `,`
- **Columnas:**
  - Fecha, Comprobante, Código, Código barras
  - Marca, Departamento, Nombre
  - Cantidad, Importe, Unitario, TIPO FACTURA

### ✅ RENTABILIDAD.csv
- **Registros:** 45 departamentos
- **Formato:** CSV con encoding UTF-8
- **Columnas:**
  - Departamento
  - % Rentabilidad
  - Clasificación

## Notas

- Estos archivos **NO** se versionan en Git (están en `.gitignore`)
- Son requeridos para ejecutar `FASE1_ANALISIS_COMPLETO.py`
- Para producción, los datos están migrados a **Supabase**
