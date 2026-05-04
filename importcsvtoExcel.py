import re
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt


# CONFIGURACIÓN


ARCHIVO = "spot.csv"                # Puede ser .csv, .xlsx o .xls
METODO = "FIFO"                     # Puede ser "FIFO" o "LIFO"
MONEDA_COTIZACION = "USDT"          # Para analizar pares contra USDT
CARPETA_SALIDA = "reporte_trading"
MOSTRAR_GRAFICOS = True             # Cambiar a False si no querés que se abran ventanas


# LECTURA DE ARCHIVOS


def leer_archivo(ruta):
    ruta = Path(ruta)

    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")

    if ruta.suffix.lower() == ".csv":
        df = pd.read_csv(
            ruta,
            sep=None,
            engine="python",
            encoding="utf-8-sig",
            index_col=False
        )
        return df

    if ruta.suffix.lower() in [".xlsx", ".xls"]:
        return pd.read_excel(ruta)

    raise ValueError("Formato no soportado. Usá CSV o Excel.")


# =====================================================
# FUNCIONES AUXILIARES GENÉRICAS
# =====================================================

def limpiar_numero(valor):
    if pd.isna(valor):
        return 0.0

    valor = str(valor).replace(",", "").strip()
    match = re.search(r"[-+]?\d*\.?\d+", valor)

    if match:
        return float(match.group())

    return 0.0


def extraer_moneda_base(par):
    par = str(par).upper().strip()

    cotizaciones = [
        "USDT", "USDC", "BUSD", "FDUSD", "DAI",
        "BTC", "ETH", "BNB", "EUR", "ARS"
    ]

    cotizaciones = sorted(cotizaciones, key=len, reverse=True)

    for cotizacion in cotizaciones:
        if par.endswith(cotizacion):
            return par[:-len(cotizacion)]

    return par


def extraer_moneda_cotizacion(par):
    par = str(par).upper().strip()

    cotizaciones = [
        "USDT", "USDC", "BUSD", "FDUSD", "DAI",
        "BTC", "ETH", "BNB", "EUR", "ARS"
    ]

    cotizaciones = sorted(cotizaciones, key=len, reverse=True)

    for cotizacion in cotizaciones:
        if par.endswith(cotizacion):
            return cotizacion

    return ""


def normalizar_nombre_columna(nombre):
    nombre = str(nombre)

    nombre = nombre.replace("\ufeff", "")
    nombre = nombre.replace("¹", "")
    nombre = nombre.replace("²", "")
    nombre = nombre.replace("³", "")

    nombre = nombre.strip().lower()

    return nombre


def buscar_columna(df, posibles_nombres):
    columnas_normalizadas = {}

    for col in df.columns:
        col_normalizada = normalizar_nombre_columna(col)

        if col_normalizada not in columnas_normalizadas:
            columnas_normalizadas[col_normalizada] = col

    for nombre in posibles_nombres:
        nombre_normalizado = normalizar_nombre_columna(nombre)

        if nombre_normalizado in columnas_normalizadas:
            return columnas_normalizadas[nombre_normalizado]

    raise ValueError(
        f"No encontré ninguna de estas columnas: {posibles_nombres}\n"
        f"Columnas disponibles: {list(df.columns)}\n"
        f"Columnas normalizadas: {list(columnas_normalizadas.keys())}"
    )


# =====================================================
# PREPARACIÓN DE DATOS
# =====================================================

def preparar_datos(df):
    df = df.copy()
    df.columns = df.columns.str.strip()

    print("\n===== DEBUG PREPARAR DATOS =====")
    print("Filas originales:", len(df))
    print("Columnas detectadas:", list(df.columns))

    col_fecha = buscar_columna(df, ["Hora", "Time", "Date", "Fecha"])
    col_par = buscar_columna(df, ["Par", "Pair", "Symbol"])
    col_lado = buscar_columna(df, ["Lado", "Side"])
    col_ejecutado = buscar_columna(df, ["Ejecutado", "Executed", "Filled", "Amount"])
    col_precio = buscar_columna(df, ["Precio promedio", "Average Price", "Avg Price", "Price"])
    col_total = buscar_columna(df, ["Total de trading", "Total", "Trading Total"])
    col_estado = buscar_columna(df, ["Estado", "Status"])

    print("Columna fecha:", col_fecha)
    print("Columna par:", col_par)
    print("Columna lado:", col_lado)
    print("Columna ejecutado:", col_ejecutado)
    print("Columna precio:", col_precio)
    print("Columna total:", col_total)
    print("Columna estado:", col_estado)

    df["Fecha"] = pd.to_datetime(
        df[col_fecha],
        format="%y-%m-%d %H:%M:%S",
        errors="coerce"
    )

    if df["Fecha"].isna().all():
        df["Fecha"] = pd.to_datetime(df[col_fecha], errors="coerce")

    df["Par"] = df[col_par].astype(str).str.upper().str.strip()
    df["Lado"] = df[col_lado].astype(str).str.upper().str.strip()
    df["Estado"] = df[col_estado].astype(str).str.upper().str.strip()

    df["Lado"] = df["Lado"].str.replace(r"\s+", " ", regex=True)
    df["Estado"] = df["Estado"].str.replace(r"\s+", " ", regex=True)

    df["Lado"] = df["Lado"].replace({
        "COMPRA": "BUY",
        "COMPRAR": "BUY",
        "BUY": "BUY",
        "VENTA": "SELL",
        "VENDER": "SELL",
        "SELL": "SELL"
    })

    df["Cantidad"] = df[col_ejecutado].apply(limpiar_numero)
    df["Precio"] = df[col_precio].apply(limpiar_numero)
    df["Total_Cotizacion"] = df[col_total].apply(limpiar_numero)

    df["Moneda"] = df["Par"].apply(extraer_moneda_base)
    df["Cotizacion"] = df["Par"].apply(extraer_moneda_cotizacion)

    print("\nPrimeras filas limpias antes de filtrar:")
    print(df[[
        "Fecha",
        "Par",
        "Moneda",
        "Cotizacion",
        "Lado",
        "Estado",
        "Cantidad",
        "Precio",
        "Total_Cotizacion"
    ]].head(10))

    print("\nValores únicos en Estado:")
    print(df["Estado"].unique())

    print("\nValores únicos en Lado:")
    print(df["Lado"].unique())

    print("\nValores únicos en Cotizacion:")
    print(df["Cotizacion"].unique())

    df = df.dropna(subset=["Fecha"])
    print("Después filtro Fecha válida:", len(df))

    estados_validos = [
        "FILLED",
        "FILL",
        "COMPLETED",
        "COMPLETADO",
        "EJECUTADO",
        "EJECUTADA"
    ]

    df = df[df["Estado"].isin(estados_validos)]
    print("Después filtro Estado:", len(df))

    df = df[df["Lado"].isin(["BUY", "SELL"])]
    print("Después filtro Lado BUY/SELL:", len(df))

    df = df[df["Cotizacion"] == MONEDA_COTIZACION]
    print("Después filtro Cotizacion USDT:", len(df))

    df = df[df["Cantidad"] > 0]
    print("Después filtro Cantidad > 0:", len(df))

    df = df[df["Precio"] > 0]
    print("Después filtro Precio > 0:", len(df))

    df = df[df["Total_Cotizacion"] > 0]
    print("Después filtro Total > 0:", len(df))

    df = df.sort_values("Fecha").reset_index(drop=True)

    print("Filas finales df_limpio:", len(df))
    print("===== FIN DEBUG =====\n")

    return df


# =====================================================
# CÁLCULO DE PNL CON FIFO / LIFO
# =====================================================

def calcular_pnl(df, metodo="FIFO"):
    metodo = metodo.upper()

    if metodo not in ["FIFO", "LIFO"]:
        raise ValueError("El método debe ser FIFO o LIFO.")

    trades_cerrados = []
    posiciones_abiertas = []

    for moneda, operaciones in df.groupby("Moneda"):
        compras = []

        for _, row in operaciones.iterrows():

            if row["Lado"] == "BUY":
                compras.append({
                    "fecha_compra": row["Fecha"],
                    "cantidad": row["Cantidad"],
                    "precio_compra": row["Precio"],
                    "costo_total": row["Cantidad"] * row["Precio"]
                })

            elif row["Lado"] == "SELL":
                cantidad_vendida = row["Cantidad"]
                precio_venta = row["Precio"]

                costo_total = 0
                ingreso_total = 0
                cantidad_matcheada = 0
                fechas_compra = []

                while cantidad_vendida > 0 and compras:
                    index = 0 if metodo == "FIFO" else -1
                    compra = compras[index]

                    cantidad_usada = min(cantidad_vendida, compra["cantidad"])

                    costo = cantidad_usada * compra["precio_compra"]
                    ingreso = cantidad_usada * precio_venta

                    costo_total += costo
                    ingreso_total += ingreso
                    cantidad_matcheada += cantidad_usada
                    fechas_compra.append(compra["fecha_compra"])

                    compra["cantidad"] -= cantidad_usada
                    cantidad_vendida -= cantidad_usada

                    if compra["cantidad"] <= 0.00000001:
                        compras.pop(index)

                if cantidad_matcheada > 0:
                    pnl = ingreso_total - costo_total
                    roi = (pnl / costo_total) * 100 if costo_total > 0 else 0

                    trades_cerrados.append({
                        "Moneda": moneda,
                        "Fecha compra inicial": min(fechas_compra),
                        "Fecha venta": row["Fecha"],
                        "Cantidad vendida": cantidad_matcheada,
                        "Precio venta": precio_venta,
                        f"Costo {MONEDA_COTIZACION}": costo_total,
                        f"Venta {MONEDA_COTIZACION}": ingreso_total,
                        f"PnL {MONEDA_COTIZACION}": pnl,
                        "ROI %": roi,
                        "Resultado": "Ganancia" if pnl > 0 else "Pérdida"
                    })

        for compra in compras:
            posiciones_abiertas.append({
                "Moneda": moneda,
                "Fecha compra": compra["fecha_compra"],
                "Cantidad abierta": compra["cantidad"],
                "Precio compra": compra["precio_compra"],
                f"Costo abierto {MONEDA_COTIZACION}": compra["cantidad"] * compra["precio_compra"]
            })

    trades_df = pd.DataFrame(trades_cerrados)
    abiertas_df = pd.DataFrame(posiciones_abiertas)

    return trades_df, abiertas_df


# =====================================================
# RESUMEN POR MONEDA
# =====================================================

def crear_resumen(trades_df, abiertas_df):
    if trades_df.empty:
        return pd.DataFrame()

    col_pnl = f"PnL {MONEDA_COTIZACION}"
    col_costo = f"Costo {MONEDA_COTIZACION}"
    col_venta = f"Venta {MONEDA_COTIZACION}"

    resumen = trades_df.groupby("Moneda").agg(
        trades_cerrados=("Moneda", "count"),
        total_invertido=(col_costo, "sum"),
        total_vendido=(col_venta, "sum"),
        pnl_total=(col_pnl, "sum"),
        roi_promedio=("ROI %", "mean"),
        mejor_trade=(col_pnl, "max"),
        peor_trade=(col_pnl, "min"),
        winrate=(col_pnl, lambda x: (x > 0).mean() * 100)
    ).reset_index()

    resumen["roi_total"] = (resumen["pnl_total"] / resumen["total_invertido"]) * 100

    if not abiertas_df.empty:
        col_abierto = f"Costo abierto {MONEDA_COTIZACION}"

        abiertas_resumen = abiertas_df.groupby("Moneda").agg(
            cantidad_abierta=("Cantidad abierta", "sum"),
            costo_abierto=(col_abierto, "sum")
        ).reset_index()

        resumen = resumen.merge(abiertas_resumen, on="Moneda", how="left")
    else:
        resumen["cantidad_abierta"] = 0
        resumen["costo_abierto"] = 0

    resumen["cantidad_abierta"] = resumen["cantidad_abierta"].fillna(0)
    resumen["costo_abierto"] = resumen["costo_abierto"].fillna(0)

    return resumen.sort_values("pnl_total", ascending=False)


# =====================================================
# GRÁFICOS
# =====================================================

def guardar_y_mostrar(nombre_archivo):
    plt.tight_layout()
    plt.savefig(nombre_archivo)

    if MOSTRAR_GRAFICOS:
        plt.show(block=True)

    plt.close()


def crear_graficos(trades_df, resumen_df, carpeta_salida):
    carpeta = Path(carpeta_salida)
    carpeta.mkdir(exist_ok=True)

    if trades_df.empty:
        print("No hay trades cerrados para graficar.")
        return

    col_pnl = f"PnL {MONEDA_COTIZACION}"

    resumen_ordenado = resumen_df.sort_values("pnl_total")

    plt.figure(figsize=(12, 6))
    barras = plt.bar(resumen_ordenado["Moneda"], resumen_ordenado["pnl_total"])

    plt.title(f"PnL total por moneda ({MONEDA_COTIZACION})")
    plt.xlabel("Moneda")
    plt.ylabel(f"PnL total en {MONEDA_COTIZACION}")
    plt.grid(True)

    for barra, valor in zip(barras, resumen_ordenado["pnl_total"]):
        plt.text(
            barra.get_x() + barra.get_width() / 2,
            barra.get_height(),
            f"{valor:.2f}",
            ha="center",
            va="bottom" if valor >= 0 else "top"
        )

    guardar_y_mostrar(carpeta / "01_pnl_total_por_moneda.png")

    resumen_roi = resumen_df.sort_values("roi_total")

    plt.figure(figsize=(12, 6))
    barras = plt.bar(resumen_roi["Moneda"], resumen_roi["roi_total"])

    plt.title("ROI total por moneda")
    plt.xlabel("Moneda")
    plt.ylabel("ROI total %")
    plt.grid(True)

    for barra, valor in zip(barras, resumen_roi["roi_total"]):
        plt.text(
            barra.get_x() + barra.get_width() / 2,
            barra.get_height(),
            f"{valor:.2f}%",
            ha="center",
            va="bottom" if valor >= 0 else "top"
        )

    guardar_y_mostrar(carpeta / "02_roi_total_por_moneda.png")

    trades_por_moneda = trades_df.groupby("Moneda").size().reset_index(name="Cantidad")

    plt.figure(figsize=(12, 6))
    barras = plt.bar(trades_por_moneda["Moneda"], trades_por_moneda["Cantidad"])

    plt.title("Cantidad de trades cerrados por moneda")
    plt.xlabel("Moneda")
    plt.ylabel("Cantidad de trades")
    plt.grid(True)

    for barra, valor in zip(barras, trades_por_moneda["Cantidad"]):
        plt.text(
            barra.get_x() + barra.get_width() / 2,
            barra.get_height(),
            f"{valor}",
            ha="center",
            va="bottom"
        )

    guardar_y_mostrar(carpeta / "03_cantidad_trades_por_moneda.png")

    trades_ordenados = trades_df.sort_values("Fecha venta").copy()
    trades_ordenados["PnL acumulado"] = trades_ordenados[col_pnl].cumsum()

    plt.figure(figsize=(12, 6))
    plt.plot(
        trades_ordenados["Fecha venta"],
        trades_ordenados["PnL acumulado"],
        marker="o"
    )

    plt.title(f"PnL acumulado general ({MONEDA_COTIZACION})")
    plt.xlabel("Fecha de venta")
    plt.ylabel(f"PnL acumulado en {MONEDA_COTIZACION}")
    plt.grid(True)

    guardar_y_mostrar(carpeta / "04_pnl_acumulado_general.png")

    roi_promedio = trades_df.groupby("Moneda")["ROI %"].mean().reset_index()
    roi_promedio = roi_promedio.sort_values("ROI %")

    plt.figure(figsize=(12, 6))
    barras = plt.bar(roi_promedio["Moneda"], roi_promedio["ROI %"])

    plt.title("ROI promedio por moneda")
    plt.xlabel("Moneda")
    plt.ylabel("ROI promedio %")
    plt.grid(True)

    for barra, valor in zip(barras, roi_promedio["ROI %"]):
        plt.text(
            barra.get_x() + barra.get_width() / 2,
            barra.get_height(),
            f"{valor:.2f}%",
            ha="center",
            va="bottom" if valor >= 0 else "top"
        )

    guardar_y_mostrar(carpeta / "05_roi_promedio_por_moneda.png")

    carpeta_monedas = carpeta / "graficos_por_moneda"
    carpeta_monedas.mkdir(exist_ok=True)

    for moneda, data_moneda in trades_df.groupby("Moneda"):
        data_moneda = data_moneda.sort_values("Fecha venta").copy()
        data_moneda["PnL acumulado"] = data_moneda[col_pnl].cumsum()
        etiquetas = data_moneda["Fecha venta"].dt.strftime("%d/%m/%y")

        plt.figure(figsize=(12, 6))
        barras = plt.bar(etiquetas, data_moneda[col_pnl])

        plt.title(f"{moneda} - Ganancia / pérdida por trade")
        plt.xlabel("Fecha de venta")
        plt.ylabel(f"PnL en {MONEDA_COTIZACION}")
        plt.xticks(rotation=45)
        plt.grid(True)

        for barra, pnl, roi in zip(barras, data_moneda[col_pnl], data_moneda["ROI %"]):
            plt.text(
                barra.get_x() + barra.get_width() / 2,
                barra.get_height(),
                f"{pnl:.2f}\n{roi:.2f}%",
                ha="center",
                va="bottom" if pnl >= 0 else "top",
                fontsize=8
            )

        guardar_y_mostrar(carpeta_monedas / f"{moneda}_01_pnl_por_trade.png")

        plt.figure(figsize=(12, 6))
        barras = plt.bar(etiquetas, data_moneda["ROI %"])

        plt.title(f"{moneda} - ROI por trade")
        plt.xlabel("Fecha de venta")
        plt.ylabel("ROI %")
        plt.xticks(rotation=45)
        plt.grid(True)

        for barra, valor in zip(barras, data_moneda["ROI %"]):
            plt.text(
                barra.get_x() + barra.get_width() / 2,
                barra.get_height(),
                f"{valor:.2f}%",
                ha="center",
                va="bottom" if valor >= 0 else "top",
                fontsize=8
            )

        guardar_y_mostrar(carpeta_monedas / f"{moneda}_02_roi_por_trade.png")

        plt.figure(figsize=(12, 6))
        plt.plot(
            data_moneda["Fecha venta"],
            data_moneda["PnL acumulado"],
            marker="o"
        )

        plt.title(f"{moneda} - PnL acumulado")
        plt.xlabel("Fecha de venta")
        plt.ylabel(f"PnL acumulado en {MONEDA_COTIZACION}")
        plt.grid(True)

        guardar_y_mostrar(carpeta_monedas / f"{moneda}_03_pnl_acumulado.png")


# =====================================================
# EXPORTAR EXCEL
# =====================================================

def exportar_excel(df_limpio, trades_df, abiertas_df, resumen_df, carpeta_salida):
    carpeta = Path(carpeta_salida)
    carpeta.mkdir(exist_ok=True)

    archivo_excel = carpeta / "reporte_trading.xlsx"

    with pd.ExcelWriter(archivo_excel, engine="openpyxl") as writer:
        resumen_df.to_excel(writer, sheet_name="Resumen por moneda", index=False)
        trades_df.to_excel(writer, sheet_name="Trades cerrados", index=False)
        abiertas_df.to_excel(writer, sheet_name="Posiciones abiertas", index=False)
        df_limpio.to_excel(writer, sheet_name="Datos limpios", index=False)

    return archivo_excel


# =====================================================
# MOSTRAR RESULTADOS
# =====================================================

def mostrar_resultados(resumen_df, abiertas_df):
    print("\n" + "=" * 60)
    print("RESUMEN POR MONEDA")
    print("=" * 60)

    if resumen_df.empty:
        print("No hay trades cerrados.")
    else:
        print(resumen_df)

    print("\n" + "=" * 60)
    print("POSICIONES ABIERTAS")
    print("=" * 60)

    if abiertas_df.empty:
        print("No hay posiciones abiertas.")
    else:
        print(abiertas_df)


# =====================================================
# MAIN
# =====================================================

def main():
    carpeta = Path(CARPETA_SALIDA)
    carpeta.mkdir(exist_ok=True)

    print("Leyendo archivo...")
    df_original = leer_archivo(ARCHIVO)

    print("Preparando datos...")
    df_limpio = preparar_datos(df_original)

    print(f"Calculando PnL con método {METODO}...")
    trades_df, abiertas_df = calcular_pnl(df_limpio, metodo=METODO)

    print("Creando resumen...")
    resumen_df = crear_resumen(trades_df, abiertas_df)

    print("Creando gráficos...")
    crear_graficos(trades_df, resumen_df, carpeta)

    print("Exportando Excel...")
    archivo_excel = exportar_excel(
        df_limpio=df_limpio,
        trades_df=trades_df,
        abiertas_df=abiertas_df,
        resumen_df=resumen_df,
        carpeta_salida=carpeta
    )

    mostrar_resultados(resumen_df, abiertas_df)

    print("\n" + "=" * 60)
    print("PROCESO TERMINADO")
    print("=" * 60)
    print(f"Excel generado: {archivo_excel}")
    print(f"Gráficos guardados en la carpeta: {carpeta}")


if __name__ == "__main__":
    main()
