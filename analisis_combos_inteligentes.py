import pandas as pd

# Cargar datos
reglas = pd.read_parquet('data/app_dataset/reglas.parquet')
alcance = pd.read_parquet('data/app_dataset/alcance_dataset.parquet')

total_tickets = int(alcance['n_tickets'].iloc[0])
ventas_total = alcance['ventas_total'].iloc[0]
ticket_promedio = ventas_total / total_tickets

print('='*80)
print(' ANÁLISIS DE COMBOS INTELIGENTES PARA SUPERMERCADO NINO')
print('='*80)
print()
print('DATOS DEL NEGOCIO:')
print(f'  Total tickets/año: {total_tickets:,}')
print(f'  Ticket promedio: ${ticket_promedio:,.0f}')
print()

# Excluir fernet + coca
reglas_top = reglas[
    ~((reglas['antecedents'].str.contains('FERNET', case=False, na=False) &
       reglas['consequents'].str.contains('COCA', case=False, na=False)) |
      (reglas['antecedents'].str.contains('COCA', case=False, na=False) &
       reglas['consequents'].str.contains('FERNET', case=False, na=False)))
].copy()

reglas_top = reglas_top.sort_values('lift', ascending=False)

print('='*80)
print(' TOP 5 COMBOS INTELIGENTES (excluye Fernet + Coca)')
print('='*80)
print()

resultados = []

for i, (idx, row) in enumerate(reglas_top.head(5).iterrows(), 1):
    ant = row['antecedents']
    cons = row['consequents']
    lift = row['lift']
    confidence = row['confidence']
    support = row['support']
    ant_support = row['antecedent support']

    # Cálculos
    tickets_con_A = int(total_tickets * ant_support)
    tickets_con_AB = int(total_tickets * support)
    tickets_con_A_sin_B = tickets_con_A - tickets_con_AB

    # Potencial con promoción
    conversion = 0.20  # 20% conversión conservadora
    tickets_incrementales_ano = int(tickets_con_A_sin_B * conversion)
    tickets_incrementales_mes = tickets_incrementales_ano // 12

    # Valor estimado
    valor_por_combo = ticket_promedio * 0.25  # combo vale 25% de un ticket promedio
    ventas_incrementales_mes = tickets_incrementales_mes * valor_por_combo
    margen_mes = ventas_incrementales_mes * 0.28  # 28% margen

    print(f'COMBO #{i}')
    print('-'*80)
    print(f'  A: {ant}')
    print(f'  B: {cons}')
    print()
    print('  FUERZA DE ASOCIACIÓN:')
    print(f'    Lift: {lift:.2f}x')
    print(f'    Confidence: {confidence*100:.1f}%')
    print(f'    Support: {support*100:.2f}%')
    print()
    print('  SITUACIÓN ACTUAL:')
    print(f'    Clientes que compran A: {tickets_con_A:,}/año')
    print(f'    Ya compran A+B: {tickets_con_AB:,}/año ({(tickets_con_AB/tickets_con_A)*100:.0f}%)')
    print(f'    Compran solo A (oportunidad): {tickets_con_A_sin_B:,}/año')
    print()
    print('  IMPACTO DE PROMOCIÓN "PACK A+B 10% OFF":')
    print(f'    Conversión esperada: 20%')
    print(f'    Combos adicionales: +{tickets_incrementales_mes:,}/mes')
    print(f'    Ventas incrementales: +${ventas_incrementales_mes:,.0f}/mes')
    print(f'    Margen adicional: +${margen_mes:,.0f}/mes')
    print()

    resultados.append({
        'Combo': i,
        'Producto_A': ant,
        'Producto_B': cons,
        'Lift': lift,
        'Tickets_con_A': tickets_con_A,
        'Ya_compran_ambos': tickets_con_AB,
        'Oportunidad': tickets_con_A_sin_B,
        'Combos_mes': tickets_incrementales_mes,
        'Ventas_mes': ventas_incrementales_mes,
        'Margen_mes': margen_mes
    })

print('='*80)
print(' RESUMEN DE COMBOS')
print('='*80)
df_res = pd.DataFrame(resultados)
print()
print(df_res[['Combo', 'Lift', 'Combos_mes', 'Ventas_mes', 'Margen_mes']].to_string(index=False))
print()
print(f'TOTAL POTENCIAL MENSUAL:')
print(f'  Combos: +{df_res["Combos_mes"].sum():,}')
print(f'  Ventas: +${df_res["Ventas_mes"].sum():,.0f}')
print(f'  Margen: +${df_res["Margen_mes"].sum():,.0f}')
print()

# Ahora buscar combos NO CARNÍVOROS
print('='*80)
print(' BONUS: COMBOS SIN CARNICERÍA (para diversificar)')
print('='*80)
print()

reglas_sin_carne = reglas[
    ~(reglas['antecedents'].str.contains('VACIO|COSTILLA|CHORIZO|ASADO|MOLIDA|MILANESA|POLLO|MUSLO|CUADRADA', case=False, na=False) |
      reglas['consequents'].str.contains('VACIO|COSTILLA|CHORIZO|ASADO|MOLIDA|MILANESA|POLLO|MUSLO|CUADRADA', case=False, na=False))
].copy()

reglas_sin_carne = reglas_sin_carne[
    ~((reglas_sin_carne['antecedents'].str.contains('FERNET', case=False, na=False) &
       reglas_sin_carne['consequents'].str.contains('COCA', case=False, na=False)) |
      (reglas_sin_carne['antecedents'].str.contains('COCA', case=False, na=False) &
       reglas_sin_carne['consequents'].str.contains('FERNET', case=False, na=False)))
].sort_values('lift', ascending=False)

print('TOP 3 COMBOS NO CARNÍVOROS:')
print()

for i, (idx, row) in enumerate(reglas_sin_carne.head(3).iterrows(), 1):
    ant = row['antecedents']
    cons = row['consequents']
    lift = row['lift']
    confidence = row['confidence']
    support = row['support']

    print(f'{i}. {ant} + {cons}')
    print(f'   Lift: {lift:.2f}x | Confidence: {confidence*100:.0f}% | Support: {support*100:.2f}%')
    print()

print('='*80)
