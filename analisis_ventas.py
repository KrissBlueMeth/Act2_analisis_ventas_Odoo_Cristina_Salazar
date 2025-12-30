import pandas as pd  #nombramos a Pandas como "pd" para llamarlo así de ahora en adelante
import matplotlib.pyplot as plt

# =========================================================================
# 1. CARGA DE DATOS
# =========================================================================
# Leemos el archivo CSV. Pandas lo transforma en un DataFrame (una tabla).
df = pd.read_csv('ventas_odoo_simulado.csv')

# .head() muestra las primeras 5 filas para verificar que se leyó correctamente.
print("Primeras 5 filas del DataFrame:")
print(df.head())

# .info() nos dice cuántas filas hay, si hay nulos y el tipo de dato de cada columna.
print("\nInformación del DataFrame:")
df.info()

# =========================================================================
# 2. LIMPIEZA Y PREPROCESAMIENTO
# =========================================================================
# Convertimos la columna de fecha de 'texto' a formato DATETIME para poder operar con ella.
df['Fecha_Pedido'] = pd.to_datetime(df['Fecha_Pedido'])

# Extraemos el mes y el año en columnas nuevas para agrupar las ventas fácilmente después.
df['Mes_Pedido'] = df['Fecha_Pedido'].dt.month
df['Año_Pedido'] = df['Fecha_Pedido'].dt.year

# Convertimos columnas de dinero y cantidad a numeros (float). 
# 'errors=coerce' transforma cualquier texto extraño en un valor nulo (NaN) en lugar de dar error.
df['Cantidad'] = pd.to_numeric(df['Cantidad'], errors='coerce')
df['Precio_Unitario'] = pd.to_numeric(df['Precio_Unitario'], errors='coerce')
df['Total_Linea'] = pd.to_numeric(df['Total_Linea'], errors='coerce')

# Borramos filas que hayan quedado con valores vacios en las columnas críticas de dinero.
df.dropna(subset=['Cantidad', 'Precio_Unitario', 'Total_Linea'], inplace=True)

# Creamos un nuevo DataFrame solo con pedidos 'Confirmado'. 
# Es importante porque los pedidos 'Borradores' o 'Cancelados' no deben contar como ventas reales.
df_confirmados = df[df['Estado_Pedido'] == 'Confirmado'].copy()

# =========================================================================
# 3. ANÁLISIS EXPLORATORIO DE DATOS (EDA)
# =========================================================================

# A) Ventas por Mes/Año: Sumamos el 'Total_Linea' agrupando por tiempo.
ventas_mensuales = df_confirmados.groupby(['Año_Pedido', 'Mes_Pedido'])['Total_Linea'].sum().reset_index()

# Creamos una columna 'Periodo' (ej: "2024-05") para que el eje X del grafico sea legible.
# .str.zfill(2) asegura que el mes 5 aparezca como "05".
ventas_mensuales['Periodo'] = ventas_mensuales['Año_Pedido'].astype(str) + '-' + \
                             ventas_mensuales['Mes_Pedido'].astype(str).str.zfill(2)

# B) Top 5 Productos: Agrupamos por Producto y usamos .nlargest(5) para sacar los 5 más altos.
top_productos_valor = df_confirmados.groupby('Producto')['Total_Linea'].sum().nlargest(5).reset_index()

# C) Top 5 Clientes: Similar al anterior, sumamos el gasto por cada nombre de cliente.
top_clientes_gasto = df_confirmados.groupby('Cliente')['Total_Linea'].sum().nlargest(5).reset_index()

# D) Ventas por Comercial: Agrupamos por el nombre del vendedor.
ventas_comercial = df_confirmados.groupby('Comercial')['Total_Linea'].sum().reset_index()

# E) Estados de Pedido: .value_counts() cuenta n veces aparece cada estado (Confirmado, Cancelado, etc.)
estados_pedido_distribucion = df['Estado_Pedido'].value_counts().reset_index()
estados_pedido_distribucion.columns = ['Estado', 'Frecuencia']

# =========================================================================
# 4. VISUALIZACIÓN CON MATPLOTLIB
# =========================================================================
# Definimos un estilo visual para que los gráficos se vean chulos.
plt.style.use('seaborn-v0_8-darkgrid')

# --- Gráfico 1: Linea de Tendencia Mensual ---
plt.figure(figsize=(10, 6))
plt.plot(ventas_mensuales['Periodo'], ventas_mensuales['Total_Linea'], marker='o', linestyle='-')
plt.title('Tendencia de Ventas Mensuales (Solo Confirmados)')
plt.xlabel('Periodo')
plt.ylabel('Ventas Totales (€)')
plt.xticks(rotation=45) # Rotamos las fechas para que no se amontonen.
plt.tight_layout()      # Ajusta los margenes automáticamente.
plt.savefig('ventas_mensuales.png') # Guarda el archivo en la carpeta.
plt.close()             # Cierra el grafico para liberar memoria.

# --- Gráfico 2: Barras de Productos ---
plt.figure(figsize=(10, 6))
plt.bar(top_productos_valor['Producto'], top_productos_valor['Total_Linea'], color='skyblue')
plt.title('Top 5 Productos más Vendidos (por Valor)')
plt.ylabel('Ventas Totales (€)')
plt.savefig('top_productos_valor.png')
plt.close()

# --- Gráfico 3: Barras de Clientes ---
plt.figure(figsize=(10, 6))
plt.bar(top_clientes_gasto['Cliente'], top_clientes_gasto['Total_Linea'], color='lightcoral')
plt.title('Top 5 Clientes con Mayor Gasto')
plt.ylabel('Gasto Total (€)')
plt.savefig('top_clientes_gasto.png')
plt.close()

# --- Gráfico 4: Barras de Comerciales ---
plt.figure(figsize=(10, 6))
plt.bar(ventas_comercial['Comercial'], ventas_comercial['Total_Linea'], color='lightgreen')
plt.title('Ventas Totales por Comercial')
plt.ylabel('Ventas Totales (€)')
plt.savefig('ventas_comercial.png')
plt.close()

# --- Gráfico 5: Pastel (Pie Chart) de Estados ---
plt.figure(figsize=(8, 8))
# autopct='%1.1f%%' añade el porcentaje automáticamente dentro de cada porción.
plt.pie(estados_pedido_distribucion['Frecuencia'], 
        labels=estados_pedido_distribucion['Estado'], 
        autopct='%1.1f%%', 
        startangle=140, 
        colors=plt.cm.Paired.colors)
plt.title('Distribución de Estados de Pedido')
plt.axis('equal') # Esto es para100 cos que el grafico sea un circulo perfecto y no una elipse.
plt.savefig('estados_pedido_distribucion.png')
plt.close()

print("\nAnálisis completado. Los gráficos se han guardado como archivos PNG.")