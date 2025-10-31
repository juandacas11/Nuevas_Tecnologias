# Análisis de Ventas - El Arte de Vivir

**Autor:** Juan David Castaño  
**Cargo:** Desarrollador de software

---

## Descripción del Proyecto
Este proyecto realiza un análisis de ventas utilizando datos obtenidos desde una API REST. El script procesa la información, genera visualizaciones y crea un reporte HTML interactivo para facilitar la toma de decisiones comerciales.

---

## Resultados y Hallazgos
- **Producto más vendido:** El análisis identifica el producto con mayor cantidad de ventas, lo que permite enfocar estrategias de inventario y marketing.
- **Producto menos vendido:** Se detecta el producto con menor rotación, útil para campañas de promoción o revisión de catálogo.
- **Mejor mes del año:** El reporte muestra el mes con mayor volumen de ventas, evidenciando estacionalidad y oportunidades para reforzar acciones comerciales.
- **Evolución en años:** El sistema permite observar la tendencia de ventas a lo largo del tiempo, facilitando la planificación estratégica y la evaluación de crecimiento.

---

## Instrucciones para Ejecutar el Script

1. **Clonar el repositorio:**
   ```powershell
   git clone https://github.com/juandacas11/Nuevas_Tecnologias.git
   cd Nuevas_Tecnologias/Consumo
   ```

2. **Crear el entorno virtual:**
   ```powershell
   python -m venv .venv
   ```

3. **Activar el entorno virtual:**
   - En PowerShell:
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   - En CMD:
     ```cmd
     .venv\Scripts\activate.bat
     ```
   - En Linux/Mac:
     ```bash
     source .venv/bin/activate
     ```

4. **Instalar las dependencias:**
   ```powershell
   pip install pandas matplotlib openpyxl requests
   ```

5. **Ejecutar el script:**
   ```powershell
   python ejm.py
   ```

6. **Ver el reporte:**
   - El archivo `reporte_ventas.html` se generará en la carpeta del proyecto. Ábrelo con tu navegador para visualizar los resultados y gráficas.

---

## Notas
- El entorno virtual y los archivos generados (.png, .html) están excluidos del control de versiones por el archivo `.gitignore`.
- Asegúrate de tener acceso a la API REST configurada en el script (`ejm.py`).
- Si tienes dudas, contacta al autor.
