import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

from processing import get_investments_by_coin


def plot_comparison_with_marker(df1: pd.DataFrame, df2: pd.DataFrame, name1: str, name2: str,
                                 marker_date: str, investment_amount: float):
    fig = make_subplots(rows=1, cols=2, subplot_titles=[f"{name1}", f"{name2}"])

    fig.add_trace(
        go.Scatter(x=df1['date'], y=df1['price_usd'], mode='lines', name=name1),
        row=1, col=1
    )

    #marker_row = df1[df1['date'] == marker_date]
    #if not marker_row.empty:
    #    fig.add_trace(
    #        go.Scatter(
    #            x=marker_row['date'],
    #            y=marker_row['price_usd'],
    #            mode='markers+text',
    #            marker=dict(color='red', size=10),
    #            text=[f"${investment_amount}"],
    #            textposition="top center",
    #            name=f"{name1} Inversión"
    #        ),
    #        row=1, col=1
    #    )

    fig.add_trace(
        go.Scatter(x=df2['date'], y=df2['price_usd'], mode='lines', name=name2),
        row=1, col=2
    )

    fig.update_layout(
        title_text=f"Comparación de precios: {name1} vs {name2} (con punto destacado)",
        height=500,
        width=1100,
        showlegend=False
    )

    fig.update_xaxes(
        title_text="Fecha",
        tickformat="%b\\n%Y",
        dtick="M1",
        tickangle=-45,
        tickfont=dict(size=9),
        row=1, col=1
    )
    fig.update_xaxes(
        title_text="Fecha",
        tickformat="%b\\n%Y",
        dtick="M1",
        tickangle=-45,
        tickfont=dict(size=9),
        row=1, col=2
    )

    fig.update_yaxes(title_text="Precio USD", row=1, col=1)
    fig.update_yaxes(title_text="Precio USD", row=1, col=2)

    # ➕ Agregar inversiones sobre df1 (name1) correctamente alineadas a precio
    investments1 = get_investments_by_coin(name1.lower())
    if not investments1.empty:
        merged1 = pd.merge(investments1, df1, on="date", how="inner")  # une con price_usd
        fig.add_trace(
            go.Scatter(
                x=merged1['date'],
                y=merged1['price_usd'],  # graficamos sobre el precio real
                mode='markers+text',
                marker=dict(color='green', size=8, symbol='diamond'),
                text=[f"${a:.2f}" for a in merged1['amount']],
                textposition="bottom center",
                name=f"Inversiones en {name1}"
            ),
            row=1, col=1
        )

    # ➕ Repetir para df2
    investments2 = get_investments_by_coin(name2.lower())
    if not investments2.empty:
        merged2 = pd.merge(investments2, df2, on="date", how="inner")
        fig.add_trace(
            go.Scatter(
                x=merged2['date'],
                y=merged2['price_usd'],
                mode='markers+text',
                marker=dict(color='blue', size=8, symbol='triangle-up'),
                text=[f"${a:.2f}" for a in merged2['amount']],
                textposition="bottom center",
                name=f"Inversiones en {name2}"
            ),
            row=1, col=2
        )

    fig.show()

