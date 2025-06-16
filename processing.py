# Se crea en automatico la DB

import pandas as pd
import sqlite3
import os
from api import fetch_market_chart

from datetime import datetime, timedelta

DB_PATH = "data/crypto.db"

def create_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            coin_id TEXT,
            date TEXT,
            price_usd REAL,
            PRIMARY KEY (coin_id, date)
        )
    """)

    # Crear tabla de inversiones
    cursor.execute("""
           CREATE TABLE IF NOT EXISTS investments (
               coin_id TEXT,
               date TEXT,
               investor TEXT,
               amount REAL,
               note TEXT,
               PRIMARY KEY (coin_id, date, investor)
           )
       """)
    conn.commit()
    conn.close()

def save_to_db(df: pd.DataFrame, coin_id: str):
    #conn = sqlite3.connect(DB_PATH)
    #df_copy = df.copy()
    #df_copy['coin_id'] = coin_id
    #df_copy[['coin_id', 'date', 'price_usd']].to_sql("prices", conn, if_exists="append", index=False)
    #conn.close()
    conn = sqlite3.connect(DB_PATH)
    df_copy = df.copy()
    df_copy['coin_id'] = coin_id

    # Obtener fechas existentes
    existing = pd.read_sql_query(
        "SELECT date FROM prices WHERE coin_id = ?", conn, params=(coin_id,)
    )
    existing_dates = set(existing['date'])

    # Filtrar solo fechas nuevas
    df_copy = df_copy[~df_copy['date'].astype(str).isin(existing_dates)]

    # Insertar solo lo nuevo
    df_copy[['coin_id', 'date', 'price_usd']].to_sql("prices", conn, if_exists="append", index=False)
    conn.close()

def load_from_db(coin_id: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    query = f"SELECT date, price_usd FROM prices WHERE coin_id = ?"
    df = pd.read_sql_query(query, conn, params=(coin_id,))
    conn.close()
    if df.empty:
        return None
    df['date'] = pd.to_datetime(df['date'])
    return df

def process_price_data(market_data: dict) -> pd.DataFrame:
    prices = market_data.get('prices', [])
    df = pd.DataFrame(prices, columns=['timestamp', 'price_usd'])
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df[['date', 'price_usd']]

def get_historical_price_dataframe(coin_id: str, vs_currency: str = 'usd', days: int = 365) -> pd.DataFrame:
    create_db()
    #df = load_from_db(coin_id)
    #if df is not None:
    #    return df
    #raw_data = fetch_market_chart(coin_id, vs_currency, days)
    #df = process_price_data(raw_data)
    #save_to_db(df, coin_id)
    #return df
    df = load_from_db(coin_id)

    if df is None or df.empty:
        # No hay datos, descarga completa
        raw_data = fetch_market_chart(coin_id, vs_currency, days)
        df = process_price_data(raw_data)
        save_to_db(df, coin_id)
        return df

    # Verificar si está actualizado
    last_date = df['date'].max().date()
    today = datetime.utcnow().date()

    if last_date < today:
        # Necesita actualización desde el último día registrado hasta hoy
        days_missing = (today - last_date).days
        print(f"Actualizando {coin_id} desde {last_date} ({days_missing} días faltantes)")

        # Traer datos faltantes desde la última fecha
        raw_data = fetch_market_chart(coin_id, vs_currency, days=days_missing + 1)
        new_df = process_price_data(raw_data)

        # Filtrar solo datos nuevos
        new_df = new_df[new_df['date'].dt.date > last_date]

        if not new_df.empty:
            df = pd.concat([df, new_df]).drop_duplicates(subset=['date']).reset_index(drop=True)
            save_to_db(df, coin_id)

    return df


# ======================
# NUEVAS FUNCIONES investment
# ======================

def insert_investment(coin_id: str, date: str, investor: str, amount: float, note: str) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO investments (coin_id, date, investor, amount, note)
            VALUES (?, ?, ?, ?, ?)
        """, (coin_id, date, investor, amount, note))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def get_all_investments() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    df = pd.read_sql_query("SELECT * FROM investments ORDER BY date DESC", conn)
    conn.close()
    return df
# "SELECT date, amount, note, investor  FROM investments WHERE coin_id = ?"
def get_investments_by_coin(coin_id: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    df = pd.read_sql_query("SELECT date, amount, note, investor FROM investments WHERE LOWER(coin_id) = LOWER(?)",
        conn,
        params=(coin_id,)
    )
    conn.close()
    df['date'] = pd.to_datetime(df['date'])
    return df

def delete_investment(coin_id: str, date: str, investor: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM investments
        WHERE coin_id = ? AND date = ? AND investor = ?
    """, (coin_id, date, investor))
    conn.commit()
    conn.close()


def process_price_data_from_db(coin_id: str) -> pd.DataFrame:
    """
    Carga y procesa los precios históricos de una criptomoneda directamente desde SQLite.

    Parámetros:
        coin_id (str): ID de la criptomoneda (ej. 'bitcoin')

    Retorna:
        pd.DataFrame con columnas: date (datetime), price_usd (float)
    """
    conn = sqlite3.connect(DB_PATH)

    query = """
        SELECT date, price_usd
        FROM prices
        WHERE coin_id = ?
        ORDER BY date ASC
    """
    df = pd.read_sql_query(query, conn, params=(coin_id,))
    conn.close()

    if df.empty:
        raise ValueError(f"No hay datos de precios para {coin_id} en la base de datos.")

    # Convertir date a datetime
    df['date'] = pd.to_datetime(df['date'])

    return df