import streamlit as st
from api import fetch_ohlc_with_volume
import plotly.graph_objects as go

# ========================
# Configuracion de pagina
# ========================
st.set_page_config(layout="wide")
st.title("📈 Análisis Técnico - Gráfico de Velas + Volumen")

# ========================
# Entrada de parametros
# ========================
coin_id = st.selectbox(
    "Selecciona una criptomoneda",
    options=["bitcoin", "ethereum", "cardano", "solana", "dogecoin"],
    index=0
)


# Slider libre
raw_days = st.slider(
    "Rango de días a analizar",
    min_value=1,
    max_value=365,
    value=30,
    step=1
)

# CoinGecko solo acepta estos valores
valid_days = [1, 7, 14, 30, 90, 180, 365]
# Buscar el mas cercano
days = min(valid_days, key=lambda x: abs(x - raw_days))






# ========================
# Boton para generar grafica
# ========================
if st.button("📊 Mostrar gráfico de velas + volumen"):
    with st.spinner("Consultando datos..."):
        df = fetch_ohlc_with_volume(coin_id=coin_id, days=days)

        if df.empty:
            st.warning("No se obtuvieron datos. Intenta con otra moneda o rango de días.")
        else:
            fig = go.Figure()

            # --- Candlestick ---
            fig.add_trace(go.Candlestick(
                x=df['date'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='OHLC'
            ))

            # --- Volumen ---
            fig.add_trace(go.Bar(
                x=df['date'],
                y=df['volume'],
                marker_color=[
                    'green' if c >= o else 'red'
                    for o, c in zip(df['open'], df['close'])
                ],
                name='Volumen',
                yaxis='y2'
            ))

            # --- Layout combinado ---
            fig.update_layout(
                title=f"{coin_id.capitalize()} - Gráfico de Velas + Volumen ({days} días)",
                xaxis=dict(title="Fecha"),
                yaxis=dict(title="Precio"),
                yaxis2=dict(
                    title="Volumen",
                    overlaying="y",
                    side="right",
                    showgrid=False,
                    range=[0, df['volume'].max() * 3]
                ),
                height=600,
                legend=dict(orientation="h", y=1.02)
            )

            st.plotly_chart(fig, use_container_width=True)
