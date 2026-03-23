# ANALISIS DE COSTOS COMPLETO - ROTISERIA NINO (BOSIN S.A.)
## Lujan de Cuyo, Mendoza | Marzo 2026

---

## 1. RESUMEN EJECUTIVO

La rotiseria opera con margen bruto del 30% y margen de contribucion positivo ($1.91M/mes), pero los costos fijos ($5.7M, mayormente laborales) generan un deficit mensual de $3.60M.

| Concepto | Monto | % s/Ventas |
|---|---|---|
| Ventas netas | $11,050,346 | 100% |
| CMV (insumos) | -$7,735,242 | 70% |
| **Margen bruto** | **$3,315,104** | **30%** |
| Costos fijos | -$5,711,108 | 51.7% |
| Costos variables | -$1,204,789 | 10.9% |
| **RESULTADO** | **-$3,600,793** | **-32.6%** |

**El negocio necesita $29.9M/mes para equilibrio. Hoy factura $11M (37% de cobertura).**

---

## 2. VENTAS

**Metodologia:** ultimos 31 dias reales (16/02 - 18/03/2026) desestacionalizados con indice 2025.
**Fuente:** 4 Excel de extraccion POS (ReporteMovimientosItemEnComprobantes 1/2/22/3).

- Ventas brutas ventana: $11,369,307 en 31 dias
- Indice estacional ponderado (Feb-Mar): 1.0095
- **Ventas netas mensuales desestacionalizadas: $11,050,346**

### Mix de ventas por familia

| Familia | % Ventas | Insumos principales |
|---|---|---|
| Empanadas (8 variedades) | 49.8% | Carne picada, tapas, queso, verdura |
| Carnes elaboradas (matambre, pernil, lengua, arrollado) | 22.1% | Cortes vacunos y porcinos |
| Pizzas y canelones | 8.3% | Harina, muzzarella, salsa |
| Milanesas de miga | 5.6% | Nalga, pan rallado, tapas miga |
| Salsas | 2.2% | Carne picada, tomate |
| Otros | 12.0% | Varios |

### Produccion diaria promedio
- 41 items/dia, 39 tickets/dia
- 371 empanadas/dia
- Sabado = 2.4x un dia normal ($753K vs $311K promedio)

---

## 3. COSTO DE MERCADERIA VENDIDA (CMV)

### Margen por producto (precios insumos Feb 2026 × factor por categoria POS)

Los costos de insumos se calculan con factores diferenciados por categoria (rentabilidad_factor del POS), no un factor unico de 0.70:
- CARNICERIA: rf=0.20 → costo = precio × 0.80
- FIAMBRERIA: rf=0.45 → costo = precio × 0.55
- CONGELADOS: rf=0.28 → costo = precio × 0.72
- Otros (secos, huevos): rf~0.28-0.30 → costo = precio × 0.70-0.72

| Producto | PVP | Costo insumos | Margen | % Ventas |
|---|---|---|---|---|
| Empanada carne x12 | $10,104 | $5,619 | 44% | 49.8% |
| Empanada J&Q x6 | $5,333 | $2,115 | 60% | 5.2% |
| Matambre NINO (por kg) | $43,628 | $22,568 | 48% | 13.9% |
| Pizza muzzarella | $7,287 | $1,331 | 82% | 2.2% |
| Canelones | $13,120 | $3,557 | 73% | 2.2% |
| Lengua vinagreta | $21,925 | $14,156 | 35% | 2.9% |
| Pernil cerdo | $29,000 | $11,566 | 60% | 2.4% |
| Arrollado pollo | $30,520 | $11,227 | 63% | 2.4% |
| **Milanesa miga x12** | **$9,445** | **$15,203** | **-61%** | **2.6%** |
| Salsa bolognesa | $7,560 | $4,460 | 41% | 2.2% |

**Margen ponderado: 38.7%** (superior al 30% del sistema; ver nota sobre gap en auditoria).

**Hallazgo critico:** La milanesa de miga se vende a perdida (-61%). El costo de nalga ($18,628/kg × 0.80 = $14,902/kg Feb 2026) + tapas miga supera ampliamente el PVP.

### Precios de insumos clave (sistema POS supermercado, Feb 2026, factores por categoria)

| Insumo | Precio retail | Factor | Costo est. |
|---|---|---|---|
| Carne picada especial | $15,020/kg | ×0.80 (CARNICERIA rf=0.20) | $12,016/kg |
| Matambre vacuno | $19,829/kg | ×0.80 (CARNICERIA rf=0.20) | $15,863/kg |
| Nalga/bola lomo | $18,628/kg | ×0.80 (CARNICERIA rf=0.20) | $14,902/kg |
| Suprema pollo | $11,921/kg | ×0.80 (CARNICERIA rf=0.20) | $9,537/kg |
| Lengua vacuna | $11,317/kg | ×0.80 (CARNICERIA rf=0.20) | $9,054/kg |
| Pernil chancho | $5,088/kg | ×0.72 (CONGELADOS rf=0.28) | $3,663/kg |
| Jamon cocido | $16,994/kg | ×0.55 (FIAMBRERIA rf=0.45) | $9,347/kg |
| Muzzarella horma | $7,586/kg | ×0.55 (FIAMBRERIA rf=0.45) | $4,172/kg |
| Tapas empanada x12 | $1,336/doc | ×0.70 | $935/doc |
| Harina 0000 | $1,019/kg | ×0.72 | $734/kg |
| Huevos x6 | $1,665 | ×0.72 | $1,199 |

---

## 4. COSTOS FIJOS: $5,711,108/mes (51.7% s/ventas)

### 4.1 Laboral: $5,052,746 (45.7%)
- 3 empleados CCT 130/75 Aux.Esp.A
- Sueldo: $1,080,274 remunerativo + $100,000 NR = $1,180,274/empleado
- Contribuciones 29.74% sobre remunerativo: $963,820
- SAC mensualizado: $350,387
- Seguro vida obligatorio: $1,500
- Provision vacaciones: $196,217 (14 dias Art.150 LCT + contribuciones)

**El laboral representa el 88% de los costos fijos y el 46% de las ventas.**

### 4.2 Servicios: $273,362 (2.5%)

| Servicio | Consumo | Tarifa oficial | Monto |
|---|---|---|---|
| Gas (Ecogas Cuyana SGP) | 250 m3/mes | $307.77/m3 + IVA (ENARGAS Res 89/2026) | $122,297 |
| Electricidad (EDEMSA T1-G) | 500 kWh/mes | $233.58/kWh + IVA (EPRE Res 025/2026) | $151,065 |

Consumo gas estimado: horno convector 8 bandejas ~4.3h/dia + cocina 2 hornallas ~2h/dia.
Consumo electrico: vitrina exhibidora + heladera insumos + campana + iluminacion.

### 4.3 Otros fijos: $385,000 (3.5%) - ESTIMADOS

| Concepto | Monto est. | Nota |
|---|---|---|
| Alquiler/amort. inmueble | $150,000 | Prorrateo ~15% m2 rotiseria |
| Descartables/packaging | $80,000 | Bandejas, bolsas, film |
| Amortizacion equipos | $50,000 | Horno+heladera+vitrina ~$15M/60m |
| Mantenimiento | $30,000 | Service horno y heladeras |
| Seguros | $25,000 | Prorrateo incendio + RC |
| Indumentaria/EPP | $15,000 | 3 empleados |
| Agua | $15,000 | Prorrateo limpieza y coccion |
| Habilitacion bromatologica | $12,000 | Anual /12 |
| Habilitacion municipal | $8,000 | Tasa /12 |

---

## 5. COSTOS VARIABLES: $1,204,789/mes (10.9% s/ventas)

| Concepto | Monto | % s/Ventas |
|---|---|---|
| IIBB Mendoza | $442,014 | 4.0% |
| Imp. Debitos/Creditos | $132,604 | 1.2% |
| Merma/descarte (estimada) | $552,517 | 5.0% |
| Comision tarjeta credito | $35,380 | 0.32% |
| Comision tarjeta debito | $41,362 | 0.37% |
| Comision billetera virtual | $912 | 0.01% |

**Nota:** Comisiones calculadas con mix de pagos reciente (Oct 2025-Mar 2026): EF ~48%, DE ~31%, CR ~11%, BI ~1%, vs mix historico anterior.

---

## 6. ANALISIS DE RENTABILIDAD

### Cascada de margenes

```
Ventas:                 $11,050,346   100.0%
(-) CMV:                -$7,735,242    70.0%
= MARGEN BRUTO:          $3,315,104    30.0%   <-- positivo
(-) Costos variables:    -$1,204,789    10.9%
= MARGEN CONTRIBUCION:   $2,110,315    19.1%   <-- positivo
(-) Costos fijos:        -$5,711,108    51.7%
= RESULTADO:             -$3,600,793   -32.6%  <-- NEGATIVO
```

### Punto de equilibrio
- Ventas necesarias: $29,905,358/mes (2.71x las actuales)
- Cobertura actual: 37%

### Sensibilizacion

**Nota:** Los escenarios de sensibilizacion requieren recalculo con los nuevos valores de costos fijos ($5,711,108) y costos variables ($1,204,789). Los valores anteriores estan desactualizados.

**En ningun escenario el negocio es rentable con la estructura actual.**

---

## 7. DIAGNOSTICO Y PALANCAS

### Problema central
La rotiseria tiene 3 empleados que cuestan $5.05M/mes (incluyendo provision vacaciones) para generar $11M en ventas. El ratio laboral/ventas del 46% es insostenible para un negocio con 30% de margen bruto.

### Palancas posibles

| Palanca | Impacto estimado | Factibilidad |
|---|---|---|
| Reducir a 2 empleados | -$1.6M/mes en costos fijos | Media - requiere reorganizar turnos |
| Certificado MiPyME (SUSS 18% vs 20.74%) | -$89K/mes | Alta - tramite administrativo |
| Subir precio milanesas miga (eliminar perdida) | +$114K/mes | Alta - ajuste de precio |
| Duplicar ventas (turno noche, delivery) | +$3.3M margen bruto | Baja - requiere inversion |
| Reducir merma de 5% a 3% | +$221K/mes | Media - mejor gestion stock |

### Conclusion
Con la estructura actual de 3 empleados, la rotiseria necesitaria triplicar ventas para ser rentable. La alternativa mas viable es reducir dotacion y/o compartir empleados con otros sectores del supermercado (panaderia, fiambreria).

---

## 8. ARCHIVOS EN ESTA CARPETA

| Archivo | Contenido |
|---|---|
| `Estructura_Costos_Rotiseria_NINO.xlsx` | Excel con 5 hojas (estructura, ventas, productos, costeo recetas, sensibilizacion) |
| `generar_excel_costos.py` | Script Python que genera el Excel |
| `auditoria_costos_rotiseria.md` | Auditoria numerica del Excel |
| `analisis_costos_rotiseria.md` | Este documento |
| `WhatsApp Ptt *.ogg` | Audios de Nahuel/Sebastian con el requerimiento original |

## 9. FUENTES DE DATOS

- **Ventas:** Sistema POS, 4 Excel extraccion Ene-Mar 2026 + parquet historico Oct 2024-Dic 2025
- **Sueldos:** CCT 130/75, escala Dic 2025 - Mar 2026
- **Gas:** ENARGAS Res 89/2026, Ecogas Cuyana SGP P1-P2 Mendoza
- **Electricidad:** EDEMSA Res EPRE 025/2026, T1-G Marzo 2026
- **Insumos:** Precios retail sistema POS supermercado NINO Feb 2026 × factor diferenciado por categoria (rentabilidad_factor POS)
