import streamlit as st
from processing import (
    get_historical_price_dataframe,
    insert_investment,
    get_all_investments,
    delete_investment,
    get_investments_by_coin,
    bulk_insert_investments
)
from plotter import plot_comparison_with_marker
import pandas as pd


st.set_page_config(page_title="CryptoAI ",layout="wide")
st.title("📊 CryptoAI - Visualización & Registro de Inversiones")

# ======= PARTE 1: Comparador de criptomonedas =======
#st.header("🔍 Comparar precios históricos")


# Selección de monedas
available_coins = ["algorand", "solana", "bitcoin", "cardano", "dogecoin", "avalanche-2", "polkadot", "chainlink", "arbitrum", "aave"]
selected_coins = st.multiselect(
    "Selecciona hasta 4 monedas para comparar",
    options=available_coins,
    default=["algorand", "solana"]
)

if len(selected_coins) < 2:
    st.warning("Selecciona al menos 2 monedas.")
    st.stop()

# Descargar data
coin_dataframes = {}
for coin in selected_coins:
    #coin_dataframes[coin] = get_historical_price_dataframe(coin)
    try:
        coin_dataframes[coin] = get_historical_price_dataframe(coin)
    except Exception as e:
        st.error(f"❌ Error al obtener datos de {coin.upper()}: {str(e)}")
        continue  # sigue con la siguiente moneda

# Crear subgraficas organizadas en 2 columnas
from plotly.subplots import make_subplots
import plotly.graph_objects as go

cols = 2
rows = (len(selected_coins) + 1) // 2
fig = make_subplots(rows=rows, cols=cols, subplot_titles=[coin.capitalize() for coin in selected_coins])

for idx, coin in enumerate(selected_coins):
    row = (idx // cols) + 1
    col = (idx % cols) + 1
    df = coin_dataframes[coin]

    # Línea de precio
    fig.add_trace(
        go.Scatter(x=df['date'], y=df['price_usd'], mode='lines', name=coin),
        row=row, col=col
    )

    # Ultimo punto con texto y color rojo  -  '%Y-%m-%d'
    # Añadir punto rojo como antes
    last_row = df.iloc[-1]
    fig.add_trace(
        go.Scatter(
            x=[last_row['date']],
            y=[last_row['price_usd']],
            mode='markers',
            marker=dict(size=8, color='red', symbol='circle'),
            name=f"{coin} último"
        ),
        row=row, col=col
    )

    # Añadir texto con fondo rojo y letras blancas como anotación
    fig.add_annotation(
        x=last_row['date'],
        y=last_row['price_usd'],
        text=f"{last_row['date'].strftime('%m-%d')}<br>${last_row['price_usd']:.2f}",
        showarrow=True,
        arrowhead=0,
        ax=30,
        ay=-30,
        font=dict(color='white', size=9),
        align='right',
        bgcolor='red',
        bordercolor='red',
        borderwidth=1,
        row=row,
        col=col
    )

    # Inversiones alineadas
    inv_df = get_investments_by_coin(coin)
    if not inv_df.empty:
        merged = pd.merge(inv_df, df, on="date", how="inner")
        fig.add_trace(
            go.Scatter(
                x=merged['date'],
                y=merged['price_usd'],
                mode='markers+text',
                marker=dict(size=10, color='black', symbol='hexagon'),
                text=[f"${a:.0f}" for a in merged['amount']],
                textposition="bottom center",
                name=f"Inversiones en {coin}"
            ),
            row=row, col=col
        )

# Layout
fig.update_layout(
    title_text="Comparador múltiple de precios con puntos de inversión",
    height=600 * rows,
    width=1200,
    showlegend=False,
    hovermode="x unified"  # ← NUEVO: activa spike + tooltip combinado
)

# Estetica de ejes
for r in range(1, rows + 1):
    for c in range(1, cols + 1):
        #fig.update_xaxes(title_text="Fecha", tickformat="%b\n%Y", dtick="M1", tickangle=-45,
        #                 tickfont=dict(size=9), row=r, col=c)
        fig.update_xaxes(
            title_text="Fecha",
            tickformat="%b\n%Y",
            dtick="M1",
            tickangle=-45,
            tickfont=dict(size=9),
            showspikes=True,  # ← NUEVO: activa línea vertical
            spikemode="across",  # ← NUEVO: línea cruzando subplots
            spikesnap="cursor",  # ← NUEVO: sigue el cursor
            spikedash="dot",  # ← NUEVO: línea punteada
            spikethickness=1,
            spikecolor="gray",
            row=r,
            col=c
        )
        fig.update_yaxes(title_text="Precio USD", row=r, col=c)

st.plotly_chart(fig, use_container_width=True)

# ======= PARTE 2: Registro de inversion =======
st.header("📝 Registrar nueva inversión")

with st.form("investment_form"):
    coin_id = st.selectbox("Selecciona una criptomoneda", options=available_coins, index=0)                   #st.text_input("Coin ID", value="algorand")
    date = st.date_input("Fecha")
    investment = st.text_input("Canal de inversión", value="bitso")
    amount = st.number_input("Monto (USD)", min_value=0.0)
    note = st.text_area("Nota")

    submitted = st.form_submit_button("Guardar inversión")
    if submitted:
        success = insert_investment(coin_id, str(date), investment, amount, note)
        if success:
            st.success("✅ Inversión guardada exitosamente.")
        else:
            st.error("⚠️ Ya existe una inversión con ese ID, fecha y tipo.")

# ======= PARTE 3: Mostrar historial de inversiones =======
st.header("📋 Historial de Inversiones")

df_invest = get_all_investments()
if df_invest.empty:
    st.info("Aún no se han registrado inversiones.")
else:
    st.dataframe(df_invest, use_container_width=True)
    # ➕ Botón para exportar CSV
    csv_data = df_invest.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Descargar como CSV",
        data=csv_data,
        file_name="historial_inversiones.csv",
        mime="text/csv"
    )

#========
# Subir CSV
st.header("📥 Cargar inversiones desde CSV")
uploaded_file = st.file_uploader("📤 Sube un archivo CSV con columnas: coin_id, date, investor, amount, note",
                                 type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        # Validar columnas requeridas
        expected_cols = {"coin_id", "date", "investor", "amount", "note"}
        if not expected_cols.issubset(df.columns):
            st.error(f"❌ El archivo debe tener las columnas: {', '.join(expected_cols)}")
        else:
            st.write("📄 Vista previa del archivo:")
            st.dataframe(df.head())

            if st.button("🚀 Cargar inversiones"):
                result = bulk_insert_investments(df)
                st.success(f"✅ Se insertaron {result['insertados']} registros.")
                if result['errores'] > 0:
                    st.warning(f"⚠️ Se omitieron {result['errores']} registros ya existentes (por clave duplicada).")

    except Exception as e:
        st.error(f"🚨 Error al procesar el archivo: {e}")
else:
    st.info("📄 Esperando un archivo CSV...")

#======== Eliminar inversiones

st.header("🗑️ Eliminar inversiones registradas")

df_invest = get_all_investments()

if df_invest.empty:
    st.info("No hay inversiones registradas.")
else:
    df_invest['seleccionar'] = False  # columna para selección en multiselect
    edited_df = st.data_editor(
        df_invest,
        column_config={"seleccionar": st.column_config.CheckboxColumn("Seleccionar")},
        disabled=["coin_id", "date", "investment", "amount", "note"],
        use_container_width=True
    )

    # Filtra solo los seleccionados
    rows_to_delete = edited_df[edited_df['seleccionar'] == True]

    if not rows_to_delete.empty:
        st.warning(f"{len(rows_to_delete)} inversión(es) seleccionadas para eliminar.")
        if st.button("Eliminar seleccionadas"):
            for _, row in rows_to_delete.iterrows():
                delete_investment(
                    coin_id=row['coin_id'],
                    date=row['date'],
                    investor=row['investor']
                )
            st.success("✅ Inversiones eliminadas exitosamente.")
            #st.experimental_rerun()  # actualiza todo automáticamente
            st.rerun()