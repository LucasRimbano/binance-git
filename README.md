# 📊 Crypto Spot Trading Analyzer

Herramienta desarrollada en **Python** para analizar historiales de operaciones Spot de criptomonedas a partir de archivos **CSV o Excel**.

> Proyecto creado por **Lucas Rimbano** como herramienta de análisis de datos aplicada al trading Spot de criptomonedas.

---

## 🚀 Descripción

**Crypto Spot Trading Analyzer** permite importar archivos de operaciones Spot exportados desde exchanges de criptomonedas y procesarlos automáticamente para obtener métricas de rendimiento.

El sistema está pensado para trabajar con archivos en formato:

- `.csv`
- `.xlsx`
- `.xls`

Aunque fue probado con un formato similar al historial Spot de Binance, la estructura del código permite adaptarlo a otros exchanges siempre que el archivo contenga columnas equivalentes como fecha, par, lado de la operación, cantidad ejecutada, precio promedio, total operado y estado de la orden.

---

## 📌 Funcionalidades principales

- Importación de archivos CSV y Excel.
- Limpieza automática de datos.
- Compatibilidad con nombres de columnas exportados por exchanges.
- Detección de operaciones de compra y venta.
- Cálculo de PnL realizado.
- Detección de posiciones abiertas.
- Cálculo de ROI por operación.
- Resumen por moneda.
- Cálculo de win rate.
- Soporte para método FIFO y LIFO.
- Generación automática de gráficos con Matplotlib.
- Exportación de resultados a Excel.
- Uso de datos ficticios para pruebas.

---

## 📈 Métricas generadas

El reporte permite visualizar:

- Total invertido por moneda.
- Total vendido por moneda.
- Ganancia o pérdida total.
- ROI total.
- ROI promedio.
- Mejor trade.
- Peor trade.
- Cantidad de trades cerrados.
- Win rate.
- Cantidad abierta por moneda.
- Costo abierto de posiciones no cerradas.

---

## 📊 Gráficos generados

El sistema genera gráficos generales y gráficos individuales por moneda.

### Gráficos generales

- PnL total por moneda.
- ROI total por moneda.
- Cantidad de trades cerrados por moneda.
- PnL acumulado general.
- ROI promedio por moneda.

### Gráficos por moneda

- Ganancia/pérdida por trade.
- ROI por trade.
- PnL acumulado por moneda.

Los gráficos se guardan automáticamente en la carpeta de salida.

---

## 🧮 Método de cálculo

El proyecto permite calcular resultados usando:

```text
FIFO: First In, First Out
LIFO: Last In, Last Out


```markdown
**Autor:** Lucas Rimbano  
**Área:** Python · Data Analysis · Trading · Automation
