import streamlit as st
import pandas as pd
from processing import get_all_investments, process_price_data_from_db
from datetime import datetime
import plotly.express as px


#  Streamlit
st.set_page_config(
    page_title="Ganancias actuales",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Ganancia Actual por Inversión")

# 1. Cargar inversiones
df_invest = get_all_investments()

if df_invest.empty:
    st.info("Aún no se han registrado inversiones.")
    st.stop()

df_invest['date'] = pd.to_datetime(df_invest['date'])

# 2. Cálculo fila por fila (sin agrupar), para más precisión
results = []

for _, row in df_invest.iterrows():
    coin = row['coin_id']
    fecha_inversion = row['date']
    monto_invertido = row['amount']

    try:
        # 3. Obtener historico de precios
        df_price = process_price_data_from_db(coin)

        # 4. Precio más cercano a la fecha de inversion
        df_hist = df_price[df_price['date'] <= fecha_inversion]
        if df_hist.empty:
            raise ValueError("No hay precio anterior a la fecha de inversión")
        precio_compra = df_hist.iloc[-1]['price_usd']

        # 5. Precio mas reciente disponible (hoy)
        precio_actual = df_price.iloc[-1]['price_usd']

        # 6. Calcular unidades compradas
        unidades = monto_invertido / precio_compra

        # 7. Calcular valor actual
        valor_actual = unidades * precio_actual
        ganancia = valor_actual - monto_invertido
        roi = ganancia / monto_invertido

        results.append({
            'coin_id': coin,
            'fecha_inversion': fecha_inversion.date(),
            'monto_invertido': monto_invertido,
            'precio_compra': precio_compra,
            'precio_actual': precio_actual,
            'unidades': unidades,
            'valor_actual': valor_actual,
            'ganancia': ganancia,
            'roi': roi
        })

    except Exception as e:
        st.warning(f"❌ {coin.upper()} - {fecha_inversion.date()}: {e}")

# 8. Mostrar resultados
if results:
    df_result = pd.DataFrame(results)

    # 💰 Ganancia total acumulada
    ganancia_total = df_result['ganancia'].sum()
    valor_total = df_result['valor_actual'].sum()
    roi_total = ganancia_total / df_result['monto_invertido'].sum()

    st.subheader("📊 Indicadores globales")

    col1, col2, col3 = st.columns(3)

    col1.metric("💰 Ganancia Total", f"${ganancia_total:,.2f}")
    col2.metric("📈 Valor Actual Total", f"${valor_total:,.2f}")
    col3.metric("🔁 ROI Promedio", f"{roi_total:.2%}")


    st.dataframe(df_result.style.format({
        'monto_invertido': '${:.2f}',
        'precio_compra': '${:.2f}',
        'precio_actual': '${:.2f}',
        'valor_actual': '${:.2f}',
        'ganancia': '${:.2f}',
        'roi': '{:.2%}'
    }), use_container_width=True)

    # 9. Grafico de ROI por moneda

    fig_roi = px.bar(
        df_result,
        x='coin_id',
        y='roi',
        color='coin_id',
        title="ROI actual por moneda",
        text=df_result['roi'].map(lambda x: f"{x:.2%}")
    )
    fig_roi.update_traces(textposition="outside", textfont_size=12)
    st.plotly_chart(fig_roi, use_container_width=True)

    # 10. Grafico de valor actual
    fig_valor = px.bar(df_result, x='coin_id', y='valor_actual', color='coin_id',
                       title="Valor actual de la inversión por moneda")
    st.plotly_chart(fig_valor, use_container_width=True)
else:
    st.info("No se pudieron calcular ganancias actuales.")
