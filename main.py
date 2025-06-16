
#CryptoAI
#│
#├── main.py                         # Script principal (ejecucion)
#├── app_streamlit.py                # UI WEB
#├── api.py                          # Lógica de conexión con CoinGecko
#├── processing.py                   # Procesamiento de datos crudos (DataFrame, fechas, etc.)
#├── plotter.py                      # Todas las funciones de visualización (plot_comparison_with_marker)
#└── requirements.txt                # (opcional) para definir dependencias como `plotly`, `pandas`, etc.



from processing import get_historical_price_dataframe
from plotter import plot_comparison_with_marker

if __name__ == "__main__":
    df_algorand = get_historical_price_dataframe("algorand")
    df_solana = get_historical_price_dataframe("solana")

    plot_comparison_with_marker(
        df1=df_algorand,
        df2=df_solana,
        name1="Algorand",
        name2="Solana",
        marker_date="2024-11-01",
        investment_amount=500
    )


