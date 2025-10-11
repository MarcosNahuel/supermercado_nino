Data folders
===========

- `raw/`: coloca aqui los archivos originales exportados del POS (se ignoran en Git).
- `processed/`: contiene la carpeta `FASE1_OUTPUT/` generada por `FASE1_ANALISIS_COMPLETO.py`. Se ignora por defecto porque puede pesar cientos de MB.
- `sample/`: incluye `FASE1_OUTPUT_SAMPLE/`, un set chico de datos sinteticos pensado para demos y despliegues en la nube.

El dashboard detecta automaticamente los datos disponibles en `processed/`. Si la carpeta no existe se utiliza la muestra incluida en `sample/`.
