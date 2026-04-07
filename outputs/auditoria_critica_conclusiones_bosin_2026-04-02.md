# AUDITORÍA CRÍTICA DE CONCLUSIONES
## BOSIN S.A. / Supermercado NIÑO
### Fecha: 2026-04-02

## Veredicto ejecutivo

La conclusión más fuerte del análisis no está demostrada.

El material sí sugiere que la rotisería, tomada como unidad aislada, pierde plata con la estructura actual. Pero el salto a afirmar que "cerrarla deja al supermercado peor" es prematuro y, en su formulación actual, metodológicamente incorrecto.

El problema central es simple: se mezcló ahorro de resultado con pérdida de facturación. Eso invalida la conclusión principal.

---

## 1. Validación metodológica

### 1.1. Desestacionalización

La desestacionalización sirve como primer ajuste descriptivo, pero no como base suficiente para una decisión de cierre.

Problemas:

- Está hecha sobre un solo mes y en pesos nominales, en un contexto argentino de alta inflación.
- Si el índice estacional se calculó sobre ventas en pesos y no sobre unidades, kilos o margen real, mezcla estacionalidad con inflación, cambios de precio y mix.
- Marzo 2026 no es perfectamente comparable con marzo 2025 por el calendario móvil de Semana Santa, que impacta fuerte en panadería y comida preparada.

Conclusión:

- En rotisería, el factor `1,024` es casi neutro, así que no cambia el diagnóstico standalone.
- En panadería, el ajuste puede ser más sensible. No lo descartaría, pero tampoco lo tomaría como verdad firme sin una serie más larga y depurada.

### 1.2. Estructura de costos por departamento

Como esquema gerencial, el enfoque es razonable: ventas, CMV, margen bruto, laboral, servicios, otros fijos y variables.

Lo débil no es la estructura. Lo débil es la calidad de algunos supuestos:

- `CMV 70%` para rotisería.
- `CMV 30%` para panadería.
- `Merma 5%`.
- `3 empleados` 100% imputados.
- Reparto de servicios sin submedición directa.

Si esos porcentajes no salen de costeo real por receta/SKU y de observación operativa, el análisis es una simulación, no una medición.

### 1.3. Basket analysis y cross-selling

Como análisis descriptivo de coexistencia en tickets, está bien.

Como prueba de causalidad, no alcanza.

Que el ticket con rotisería sea más alto no prueba que la rotisería cause ese ticket. También puede pasar esto:

- El cliente que compra rotisería ya es más valioso de base.
- La rotisería aparece en tickets de ocasión especial, fin de semana o cierre de jornada.
- La compra fuerte puede estar explicada por otra necesidad principal, no por la rotisería.

El cross-sell existe. La causalidad no está demostrada.

### 1.4. Chi-cuadrado, lift y Cramér's V

La interpretación de `Cramér's V = 0,046` como efecto pequeño está bien.

Eso implica exactamente lo contrario de lo que después hace el informe: estadísticamente hay señal, pero la magnitud del vínculo es débil.

Además:

- Con `25.144` tickets, un `p<0,001` puede salir por diferencias chicas. No dice nada sobre relevancia económica.
- Si el efecto es pequeño, no podés apoyar una conclusión causal fuerte solo en ese test.

También hay una inconsistencia numérica que hay que revisar:

- `P(Panadería | Rotisería) = 50,8%`
- `P(Rotisería | Panadería) = 6,1%`
- `Lift = 1,27`

Con los universos informados, esas tres cifras no parecen cerrar simultáneamente. Alguna está mal calculada, redondeada de forma grosera o tomada sobre un universo diferente.

### 1.5. Segmentación causal del cross-sell

Esta es una de las debilidades más grandes del trabajo.

Segmentar tickets según qué porcentaje del ticket representa la rotisería puede servir como heurística comercial. No sirve, por sí mismo, para inferir causalidad.

Los porcentajes de "riesgo real" asignados a cada tramo (`5%`, `15%`, `40%`, `70%`, `95%`) no son un hallazgo estadístico. Son una hipótesis subjetiva disfrazada de precisión cuantitativa.

Problemas:

- El share de rotisería en el ticket no identifica el verdadero motivo de visita.
- Un ticket donde rotisería es `8%` puede haber sido gatillado por la rotisería.
- Un ticket donde rotisería es `80%` puede ser una compra oportunista que no arrastra nada si se elimina.

Conclusión:

El número `$6.011.986` de "cross-sell en riesgo real" no es evidencia; es un escenario construido con supuestos discrecionales.

### 1.6. Cálculo del "resultado neto de cerrar"

Acá está el error conceptual más serio.

El cálculo presentado fue:

- Se ahorra la pérdida actual de rotisería: `$3.284.942`
- Se pierden `$6.011.986` de cross-sell
- Resultado neto: negativo

Eso está mal planteado.

No se puede comparar:

- un ahorro de resultado
- contra una pérdida de facturación

Si cerrás la rotisería y perdés ventas de otros rubros, no perdés el 100% de esas ventas como resultado. Perdés el margen de contribución de esas ventas.

La forma correcta sería:

`Impacto neto = ahorro de costos evitables + margen perdido de rotisería eliminado - margen de contribución perdido del cross-sell afectado - costos hundidos que sigan existiendo`

Con los datos disponibles, esa cuenta no está hecha.

Por lo tanto:

La conclusión "cerrar la rotisería deja al supermercado peor" no está demostrada.

---

## 2. Supuestos cuestionables

### 2.1. Margen bruto de rotisería

`CMV 70%` y margen bruto `30%` pueden ser razonables para una rotisería mal gestionada, pero si no salen de costeo real por receta/SKU, son débiles.

Sensibilidad:

- Cada 5 puntos de CMV en rotisería mueven aproximadamente medio millón de pesos por mes.
- Eso no arregla el negocio por sí solo, pero sí cambia el tamaño del problema.

### 2.2. Margen bruto de panadería

`CMV 30%` y margen `70%` en panadería pueden ser posibles en productos elaborados de alto valor agregado, pero el dato es demasiado bueno como para aceptarlo sin abrirlo por mix.

Preguntas obligatorias:

- ¿Incluye desperdicio real?
- ¿Incluye devoluciones?
- ¿Incluye horas improductivas?
- ¿Está medido por receta o por promedio del POS?

Si panadería realmente sostiene esos niveles, entonces es una unidad muy rentable. Si no, está sobreestimada.

### 2.3. Dotación laboral

El supuesto de `3 empleados` dedicados íntegramente a cada sector es demasiado fuerte para una decisión estructural.

La pregunta correcta no es cuántos empleados "tiene" el sector, sino cuántas horas son efectivamente evitables si se cierra.

Escenarios posibles:

- Un empleado se reubica.
- Dos comparten tareas con panadería.
- Parte de la producción se terceriza.

Eso cambia drásticamente la evaluación.

### 2.4. Merma

`5%` puede ser razonable como supuesto central para rotisería. El problema no es el número en sí, sino si ya quedó absorbido de otra forma en el costo observado.

Si el margen del POS ya refleja pérdidas operativas o diferencias de compra/venta, agregar merma encima puede duplicar castigo.

### 2.5. Costos fiscales y financieros

Hay dos riesgos:

- Que algunas alícuotas no estén perfectamente alineadas con el encuadre real de la empresa.
- Que se estén aplicando porcentajes sobre bases distintas entre sí.

Puntos a revisar:

- Ventas con IVA versus costos netos de IVA.
- IIBB según actividad real y umbral provincial.
- Impuesto al cheque y posibilidades de cómputo según encuadre MiPyME.
- Costo financiero real según mix y plazo de acreditación actual.

### 2.6. Cross-sell "en riesgo"

Es el supuesto más flojo de todos y el que más cambia la conclusión final.

No hay evidencia empírica sólida de que esos porcentajes de riesgo sean correctos.

Con otros parámetros de riesgo perfectamente plausibles, la conclusión puede darse vuelta.

---

## 3. Lo que falta para decidir con confianza

Antes de decidir cierre, continuidad o rediseño, faltan datos críticos.

### 3.1. Margen de contribución real del cross-sell en riesgo

No alcanza con saber cuánta venta acompaña a la rotisería.

Hay que saber:

- qué rubros componen ese cross-sell;
- cuánto margen aportan;
- cuánto de ese margen se perdería realmente si se cierra;
- cuánto se sustituiría por otras categorías del mismo negocio.

Sin eso, el "resultado neto de cerrar" no existe.

### 3.2. Costos evitables versus costos hundidos

Hay que separar:

- costo que desaparece si cerrás;
- costo que queda igual;
- costo que puede reubicarse;
- costo que aparece por la transición.

Ejemplos:

- indemnizaciones;
- reubicación de personal;
- limpieza/mantenimiento que sigue existiendo;
- depreciación de equipos;
- costo de oportunidad del espacio liberado.

### 3.3. Serie histórica más larga y limpia

Se necesita al menos:

- `12-24` meses diarios;
- unidades;
- tickets;
- margen;
- horas trabajadas;
- estacionalidad por calendario móvil.

Un solo mes completo sirve para diagnosticar. No sirve para una decisión irreversible.

### 3.4. Costeo por receta/SKU

Hace falta validar:

- productos rentables;
- productos destruyentes;
- dispersión de márgenes;
- peso de promociones y descuentos.

Es posible que el problema no sea "la rotisería" sino el mix y la ejecución.

### 3.5. Evidencia causal real

La única forma seria de estimar impacto causal es observar o testear:

- días con quiebre o cierre parcial;
- franjas sin producción;
- faltantes operativos;
- prueba controlada de reducción de surtido o cierre temporal.

Sin eso, todo lo causal sigue siendo inferencia débil.

### 3.6. Valor alternativo del espacio

Cerrar una unidad no solo elimina ventas. También libera metros, equipamiento y foco operativo.

Falta evaluar:

- expansión de panadería;
- freezer/comidas tercerizadas;
- elaborados de carnicería;
- góndola fría lista para llevar;
- alquiler/concesión interna del espacio.

---

## 4. Opinión sobre la conclusión principal

La conclusión "cerrar la rotisería deja al supermercado peor" es prematura.

No digo que sea falsa. Digo que hoy no está demostrada.

Lo que sí parece bastante probable con los datos disponibles es esto:

- La rotisería, bajo la estructura actual, parece deficitaria como unidad independiente.
- El cross-sell existe, pero su efecto causal está sobreafirmado.
- El cálculo del impacto neto de cierre está mal formulado.

Mi posición profesional sería:

1. No firmar el cierre solo con este análisis.
2. Tampoco defender la continuidad "como está".
3. Pasar a una segunda fase con foco en costos evitables, margen del cross-sell y test causal.

En otras palabras:

El informe justifica revisar la rotisería en serio. No justifica todavía concluir que cerrarla empeora el negocio.

---

## 5. Riesgos no contemplados

### 5.1. Error de base fiscal

Si ventas están expresadas con IVA y varios costos están netos de IVA, los ratios están distorsionados.

### 5.2. Calidad de datos POS

Riesgos típicos:

- mala clasificación de departamentos;
- anulaciones;
- devoluciones;
- promos mal imputadas;
- consumo interno no depurado;
- tickets con carga parcial.

### 5.3. Calendario y contexto

Marzo puede estar afectado por:

- vísperas de feriado;
- cierres de mes;
- clima;
- fechas especiales;
- cobro de salarios o planes.

### 5.4. Rigidez laboral

Cerrar un sector no implica ahorro inmediato pleno si:

- no se puede reducir dotación;
- hay costo indemnizatorio;
- el personal debe reubicarse;
- hay restricciones sindicales u operativas.

### 5.5. Sustitución interna de demanda

Parte de la venta actual de rotisería podría migrar a:

- panadería;
- fiambres;
- bebidas;
- carnes elaboradas;
- productos listos para consumir;
- congelados.

Ese efecto no fue modelado.

### 5.6. Factores competitivos y de posicionamiento

El POS no mide:

- imagen del local;
- percepción de surtido;
- valor de conveniencia;
- capacidad de atraer flujo;
- pérdida de clientes por deterioro de propuesta.

Un cierre puede ahorrar caja y erosionar marca. También puede pasar lo contrario. Hoy eso no está medido.

### 5.7. Concentración de dependencia en panadería

Si panadería es efectivamente el gran motor, también aparece un riesgo:

- dependencia excesiva de una sola unidad;
- vulnerabilidad ante merma, personal clave o cambios de hábito.

---

## 6. Qué sí está bien encaminado

No todo está mal. Hay cosas valiosas en el trabajo:

- Separar análisis standalone del análisis de arrastre comercial.
- No quedarse solo con margen bruto.
- Medir tickets con y sin ancla.
- Usar métricas de afinidad como lift y probabilidades condicionales.
- Intentar estimar el daño de segundo orden del cierre.

El problema no es la dirección del análisis. El problema es que varias conclusiones van más lejos que lo que los datos permiten sostener.

---

## 7. Conclusión final

Mi lectura brutal es esta:

El trabajo alcanza para decir que la rotisería, así como está planteada hoy, probablemente sea un mal negocio operativo. No alcanza para decir que cerrarla empeora el supermercado.

La conclusión principal está inflada por:

- una inferencia causal débil;
- una segmentación subjetiva convertida en pseudo-medición;
- y un error conceptual en el cálculo del resultado neto de cierre.

Si yo tuviera que decidir con responsabilidad, no cerraría todavía con esta evidencia. Pero tampoco aceptaría seguir igual.

La decisión correcta no es "cerrar sí o no" con este memo. La decisión correcta es abrir una fase 2 corta, dura y cuantitativa para responder tres preguntas:

1. ¿Cuánto costo de rotisería es realmente evitable?
2. ¿Cuánto margen de otros rubros se perdería de verdad?
3. ¿Qué alternativa de rediseño, reducción o reemplazo genera mejor resultado?

Hasta que eso no esté medido, cualquier conclusión tajante sobre el cierre sigue siendo más relato que evidencia.
