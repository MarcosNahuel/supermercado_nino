# Respuesta a Presupuesto - Sistema Caribbean
**Supermercado Don Nino / PymeInside**
**Fecha:** 6 de Febrero de 2026
**Ref:** Presupuesto Bosin S.A. del 02/02/2026

---

## 1. GRUPO A — APROBADO

Agradecemos la propuesta. Vamos a avanzar con el **Grupo A** ($600.000 + IVA), que incluye:

- Ventas - Detalle de Comprobantes
- Precios - Histórico
- Maestro de Productos
- Maestro de Clientes

**Grupo B y C** no aplican por ahora dado que no se gestiona stock en el sistema.

Si las tablas del Grupo A vienen completas con todos los campos según lo propuesto, estamos de acuerdo. Solo necesitamos confirmar que cada comprobante de venta incluya también: **ID_CLIENTE, DNI, NOMBRE, TELÉFONO** y **HORA** (que hoy viene en un archivo separado). Sin la vinculación cliente-comprobante el Maestro de Clientes no tiene utilidad.

---

## 2. DISPONIBILIDAD DE LA INFORMACIÓN

Nuestro sistema de BI necesita consumir estos datos de forma **periódica y automática** (idealmente diaria). Necesitamos definir cómo accedemos a la información. Planteamos tres opciones:

**Opción 1 — Acceso directo a la base de datos (preferida)**
Conectarnos a la BD de Caribbean en modo lectura (ODBC, JDBC o driver nativo) para extraer los datos automáticamente. Si es viable, la extracción la resolvemos nosotros. ¿Es posible? ¿Qué conexión se requiere? ¿Hay restricciones de licencia?

**Opción 2 — Exportación automática programada**
Que el módulo genere los CSV automáticamente por tarea programada y los deposite en una carpeta configurada, sin intervención del operador. ¿El módulo lo soporta?

**Opción 3 — Exportación manual asistida**
El operador genera los archivos manualmente y nuestro sistema los detecta. Menos deseable por depender de intervención diaria. ¿Se pueden guardar en carpeta de red compartida?

---

## 3. PREGUNTAS FINALES

- ¿Cuál es el **plazo estimado de entrega**?
- ¿Incluye **soporte post-implementación**?

Quedamos a disposición para una reunión técnica si es necesario.

---

**Supermercado Don Nino / PymeInside**
Equipo de Business Intelligence
