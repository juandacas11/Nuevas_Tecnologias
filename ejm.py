# Importaciones necesarias
import requests
import pandas as pd
import matplotlib.pyplot as plt
from requests.auth import HTTPBasicAuth


#Urls compras y productos
url = "http://localhost:8080/api/purchases"
url2="http://localhost:8080/api/products"


#Credenciales administrador
usuario = "admin"
contraseña = "admin123"

# Obtener datos de compras
response = requests.get(url, auth=HTTPBasicAuth(usuario, contraseña))


#Aplico este if para identificar si la respuesta fue exitosa, y utilizo el
#comando .explode para desglosar los items de cada compra en filas separadas
if response.status_code == 200:
    data = response.json()
    df = pd.DataFrame(data)

    df_exploded = df.explode("items", ignore_index=True)
    df_items = df_exploded["items"].apply(pd.Series)
    df_items = df_items.add_prefix("item_")

#concateno los elementos, primero elimino la columna items original,
#ya que contiene la lista completa de items por compra
    df_exploded = pd.concat(
        [df_exploded.drop(columns=["items"]),
         df_items],
        axis=1
    )

    #  El formato de la fecha que trae la API incluye hora y zona horaria, solo me interesa la fecha
    df_exploded['purchaseDate'] = df_exploded['purchaseDate'].str.split('T').str[0]
    # Convertir item_quantity a enteros desde el principio, esto para poder realizar operaciones matematicas
    #en este punto nos encontramos con muchos problemas a l hora de trabajar con ploty
    #y debimos migrar a matplotlib
    df_exploded['item_quantity'] = pd.to_numeric(df_exploded['item_quantity'], errors='coerce').astype('Int64')
    
    # Obtener datos de productos URL 2
    response_products = requests.get(url2, auth=HTTPBasicAuth(usuario, contraseña))
    if response_products.status_code == 200:
        data_products = response_products.json()
        df_products = pd.DataFrame(data_products)
    else:
        print(f"Error al obtener productos {response_products.status_code}: {response_products.text}")
        df_products = pd.DataFrame()

    # Genero un cruce de datos con el fin de determinar el nombre del producto
    df_final = pd.merge(df_exploded, df_products, left_on='item_productId', right_on='id', how='left')

   
    
    #Limpieza de datos, elimino datos vacios y duplicados en el dataframe
    df_final = df_final.dropna(subset=['item_quantity', 'city', 'name', 'purchaseDate'])
    df_final.drop_duplicates(inplace=True)


    # Agrupacion por ciudad y cantidad de productos vendidos
    ventas_por_ciudad = df_final.groupby('city')['item_quantity'].sum().reset_index()
    ventas_por_ciudad.columns = ['city', 'total_vendido']

    # Agrupacion por producto
    productos_vendidos = df_final.groupby('name')['item_quantity'].sum().reset_index()
    productos_vendidos.columns = ['name', 'total_vendido']
    #Lo ordeno ascendentemente para obtener el mas y menos vendido
    productos_vendidos = productos_vendidos.sort_values('total_vendido', ascending=False)
   

    most_sold = productos_vendidos.iloc[0] if len(productos_vendidos) > 0 else None
    least_sold = productos_vendidos.iloc[-1] if len(productos_vendidos) > 0 else None

    # Convertir purchaseDate a datetime primero
    df_final['purchaseDate'] = pd.to_datetime(df_final['purchaseDate'])
    
    # Agrupación por mes
    df_final['month'] = df_final['purchaseDate'].dt.to_period('M').astype(str)
    # Agregación correcta por mes
    ventas_por_mes = df_final.groupby('month')['item_quantity'].sum().reset_index()
    ventas_por_mes.columns = ['month', 'total_vendido']
    ventas_por_mes = ventas_por_mes.sort_values('month')

    df_final['weekday_en'] = df_final['purchaseDate'].dt.day_name()
    # Realizo un mapeo para traer los días en español
    dia_map = {
        'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
        'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
    }
    df_final['weekday'] = df_final['weekday_en'].map(dia_map)
    order_week = ['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo']
    # Agregación correcta por día de la semana
    ventas_por_weekday = df_final.groupby('weekday')['item_quantity'].sum().reindex(order_week).reset_index()
    ventas_por_weekday.columns = ['weekday', 'total_vendido']
    ventas_por_weekday['total_vendido'] = ventas_por_weekday['total_vendido'].fillna(0)

    # Configuración base para todas las gráficas
    plt.style.use('dark_background')
    color_principal = '#00b4d8'
    fig_size = (12, 6)
    
    # Gráfica 1: Ventas por Ciudad
    plt.figure(figsize=fig_size)
    bars = plt.bar(ventas_por_ciudad['city'], ventas_por_ciudad['total_vendido'], color=color_principal)
    plt.title('Total de Ventas por Ciudad', color=color_principal, pad=20, size=14)
    plt.xlabel('Ciudad', size=12)
    plt.ylabel('Cantidad Vendida', size=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, alpha=0.2)
    # Añadir etiquetas de valor en cada barra
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}',
                ha='center', va='bottom', color='white')
    plt.tight_layout()
    plt.savefig('grafica_ciudad.png', bbox_inches='tight', dpi=300, facecolor='#1e1e1e')
    plt.close()

    # Gráfica 2: Top 3 Productos
    plt.figure(figsize=fig_size)
    top_productos = productos_vendidos.head(3).copy()
    bars = plt.bar(top_productos['name'], top_productos['total_vendido'], color=color_principal)
    plt.title('Top 3 Productos Más Vendidos', color=color_principal, pad=20, size=14)
    plt.xlabel('Producto', size=12)
    plt.ylabel('Cantidad Vendida', size=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, alpha=0.2)
    # Añadir etiquetas de valor en cada barra
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}',
                ha='center', va='bottom', color='white')
    plt.tight_layout()
    plt.savefig('grafica_productos.png', bbox_inches='tight', dpi=300, facecolor='#1e1e1e')
    plt.close()

    # Gráfica 3: Ventas por Mes
    plt.figure(figsize=fig_size)
    plt.plot(ventas_por_mes['month'], ventas_por_mes['total_vendido'], 
             marker='o', color=color_principal, linewidth=2, markersize=8)
    plt.title('Ventas por Mes', color=color_principal, pad=20, size=14)
    plt.xlabel('Mes', size=12)
    plt.ylabel('Cantidad Vendida', size=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, alpha=0.2)
    # Añadir etiquetas de valor en cada punto
    for x, y in zip(ventas_por_mes['month'], ventas_por_mes['total_vendido']):
        plt.text(x, y, f'{int(y):,}', ha='center', va='bottom', color='white')
    plt.tight_layout()
    plt.savefig('grafica_mes.png', bbox_inches='tight', dpi=300, facecolor='#1e1e1e')
    plt.close()

    # Gráfica 4: Ventas por Día de la Semana
    plt.figure(figsize=fig_size)
    bars = plt.bar(ventas_por_weekday['weekday'], ventas_por_weekday['total_vendido'], color=color_principal)
    plt.title('Ventas por Día de la Semana', color=color_principal, pad=20, size=14)
    plt.xlabel('Día', size=12)
    plt.ylabel('Cantidad Vendida', size=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, alpha=0.2)
    # Añadir etiquetas de valor en cada barra
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}',
                ha='center', va='bottom', color='white')
    plt.tight_layout()
    plt.savefig('grafica_weekday.png', bbox_inches='tight', dpi=300, facecolor='#1e1e1e')
    plt.close()

    # Resumen textual para mostrar en el HTML
    resumen_html = """
    <div class='summary'>
      <h2>Resumen de productos</h2>
      <p><strong>Producto más vendido:</strong> {most_name} — {most_qty:.0f} unidades vendidas.</p>
      <p><strong>Producto menos vendido:</strong> {least_name} — {least_qty:.0f} unidades vendidas.</p>
      <h3>Recomendaciones rápidas</h3>
      <ul>
        <li>Implementar una estrategia de promoción y descuentos en los meses de menor venta para los productos menos vendidos.</li>
        <li>Analizar la estacionalidad en la gráfica de ventas por mes y planificar inventario y marketing acorde.</li>
        <li>Usar campañas dirigidas en los días con mayor venta por semana para incrementar conversión en días más flojos.</li>
        <li>Considerar un experimento A/B con precios o bundles en el top 3 de productos para incrementar margen.</li>
      </ul>
    </div>
    """.format(
        most_name=(most_sold['name'] if most_sold is not None else 'N/A'),
        most_qty=(most_sold['total_vendido'] if most_sold is not None else 0),
        least_name=(least_sold['name'] if least_sold is not None else 'N/A'),
        least_qty=(least_sold['total_vendido'] if least_sold is not None else 0)
    )
    
    
html_template = """
<html>
<head>
<title>Análisis de Ventas - El Arte de Vivir</title>
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.css">
<script type="text/javascript" charset="utf8" src="https://code.jquery.com/jquery-3.7.0.js"></script>
<script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.js"></script>
<style>
/* Estilos generales */
body { 
    font-family: 'Segoe UI', Arial, sans-serif;
    background-color: #1e1e1e;
    color: #e0e0e0;
    margin: 0;
    padding: 20px;
    line-height: 1.6;
}

/* Encabezados */
h1, h2, h3 { 
    color: #00b4d8;
    text-align: center;
    margin: 20px 0;
    padding: 10px;
    text-transform: uppercase;
    letter-spacing: 2px;
}

/* Contenedor principal */
.container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
}

/* Gráficas */
.graficas { 
    display: flex;
    flex-direction: column;
    gap: 40px;
    margin: 20px 0;
}

.grafica-container { 
    background-color: #2d2d2d;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}

.grafica-container h3 {
    margin: 0 0 20px 0;
}

.grafica { 
    width: 100%;
    height: auto;
    border-radius: 8px;
}

.summary {
    background-color: #2d2d2d;
    padding: 25px;
    border-radius: 8px;
    margin: 20px 0;
    line-height: 1.8;
}

.summary h2 {
    margin-top: 0;
}

.summary ul {
    padding-left: 20px;
}

.summary li {
    margin-bottom: 10px;
}

/* Tabla */
.dataTables_wrapper {
    margin: 30px 0;
    padding: 20px;
    background-color: #2d2d2d;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}

table.display {
    width: 100% !important;
    margin: 20px 0 !important;
    border-collapse: collapse;
    background-color: #363636;
}

table.display thead th {
    background-color: #1a1a1a;
    color: #00b4d8;
    padding: 12px;
    border-bottom: 2px solid #00b4d8;
}

table.display tbody td {
    padding: 10px;
    border-bottom: 1px solid #4a4a4a;
    color: #e0e0e0;
}

table.display tbody tr:hover {
    background-color: #404040;
}

/* Controles de DataTables */
.dataTables_info, 
.dataTables_length, 
.dataTables_filter {
    color: #e0e0e0 !important;
    margin: 10px 0;
}

.dataTables_filter input,
.dataTables_length select {
    background-color: #363636 !important;
    color: #e0e0e0 !important;
    border: 1px solid #4a4a4a !important;
    padding: 5px !important;
    border-radius: 4px !important;
}

.dataTables_paginate .paginate_button {
    background-color: #363636 !important;
    color: #e0e0e0 !important;
    border: 1px solid #4a4a4a !important;
    border-radius: 4px !important;
    padding: 5px 10px !important;
    margin: 0 2px !important;
}

.dataTables_paginate .paginate_button:hover {
    background-color: #404040 !important;
    color: #00b4d8 !important;
}

.dataTables_paginate .paginate_button.current {
    background-color: #00b4d8 !important;
    color: #1e1e1e !important;
    border-color: #00b4d8 !important;
}

@media (min-width: 768px) {
    .graficas-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 20px;
    }
}
</style>
</head>
<body>
<div class="container">
    <h1>Análisis de Ventas - El Arte de Vivir</h1>
    
    <!-- Resumen con producto más/menos vendido y recomendaciones -->
    {resumen}
    
    <!-- Gráficas -->
    <div class="graficas">
        <div class="grafica-container">
            <h3>Total de Ventas por Ciudad</h3>
            <img src="grafica_ciudad.png" alt="Ventas por Ciudad" class="grafica">
            <div class="analisis">
                <p>Esta gráfica muestra el total de ventas realizadas en cada ciudad, permitiendo identificar los mercados más importantes y aquellos que podrían necesitar más atención.</p>
            </div>
        </div>

        <div class="grafica-container">
            <h3>Top 3 Productos Más Vendidos</h3>
            <img src="grafica_productos.png" alt="Top 10 Productos" class="grafica">
            <div class="analisis">
                <p>Aquí se muestran los 10 productos más vendidos, lo que ayuda a identificar los productos estrella y gestionar mejor el inventario.</p>
            </div>
        </div>

        <div class="grafica-container">
            <h3>Ventas por Mes</h3>
            <img src="grafica_mes.png" alt="Ventas por Mes" class="grafica">
            <div class="analisis">
                <p>La tendencia mensual de ventas permite identificar patrones estacionales y planificar mejor las estrategias de venta.</p>
            </div>
        </div>

        <div class="grafica-container">
            <h3>Ventas por Día de la Semana</h3>
            <img src="grafica_weekday.png" alt="Ventas por Día" class="grafica">
            <div class="analisis">
                <p>Esta gráfica muestra los patrones de venta según el día de la semana, útil para optimizar la gestión de personal y recursos.</p>
            </div>
        </div>
    </div>

    <!-- Tabla Detallada -->
    <h2>Datos Detallados de Ventas</h2>
    {table}
</div>

<script>
$(document).ready( function () {
    $('#reporte-ventas').DataTable({
        "pageLength": 25,
        "language": {
            "search": "Buscar:",
            "lengthMenu": "Mostrar _MENU_ registros por página",
            "info": "Mostrando _START_ a _END_ de _TOTAL_ registros",
            "paginate": {
                "first": "Primero",
                "last": "Último",
                "next": "Siguiente",
                "previous": "Anterior"
            }
        }
    });
} );
</script>
</body>
</html>
"""

table_html = df_final.to_html(index=False, table_id="reporte-ventas", classes="display")

# Generar el HTML con la tabla y el resumen
final_html = html_template.replace("{table}", table_html).replace("{resumen}", resumen_html)

with open("reporte_ventas.html", "w", encoding='utf-8') as f:
    f.write(final_html)
print("Reporte 'reporte_ventas.html' generado con éxito.")

