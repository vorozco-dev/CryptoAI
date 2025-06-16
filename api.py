import time
import functools
import requests
import pandas as pd


# ===========================
# Decorador reutilizable
# ===========================
def retry_on_exception(max_retries=3, delay=2, backoff=2, allowed_statuses=(429, 502, 503)):
    """
    Decorador para reintentar funciones HTTP que fallen con codigos de error temporales.

    Parámetros:
    - max_retries: numero maximo de intentos
    - delay: tiempo inicial de espera entre reintentos (en segs)
    - backoff: factor multiplicador para cada reintento (exponencial)
    - allowed_statuses: codigos HTTP que activan reintento
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            wait = delay
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.HTTPError as e:
                    status = e.response.status_code
                    if status in allowed_statuses:
                        print(f"[{func.__name__}] Intento {attempt} fallido con status {status}. Reintentando en {wait}s...")
                        time.sleep(wait)
                        wait *= backoff
                    else:
                        raise  # Error no esperado, propagar
            raise Exception(f"[{func.__name__}] Falló tras {max_retries} intentos.")
        return wrapper
    return decorator

# ===========================
# Funcion API con retry
# ===========================
@retry_on_exception(max_retries=4, delay=2.0, backoff=2)
def fetch_market_chart(coin_id: str, vs_currency: str = 'usd', days: int = 365, interval: str = 'daily') -> dict:
    """
    Llama a la API de CoinGecko y obtiene datos históricos de precios.

    Parametros:
    - coin_id: ID de la moneda (ej. 'bitcoin')
    - vs_currency: Moneda de referencia (por defecto 'usd')
    - days: Numero de días de historico
    - interval: Intervalo de muestreo (por defecto 'daily')

    Retorna:
    - Diccionario con los datos del mercado
    """
    url = f'https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart'
    params = {
        'vs_currency': vs_currency,
        'days': days,
        'interval': interval
    }

    response = requests.get(url, params=params)
    response.raise_for_status()  # Si el status no es 200, lanza HTTPError
    return response.json()

# OHLC
@retry_on_exception(max_retries=4, delay=2.0, backoff=2)
def fetch_ohlc_with_volume(coin_id: str, vs_currency: str = 'usd', days: int = 30) -> pd.DataFrame:
    """
    Obtiene datos OHLC + Volumen desde la API de CoinGecko.

    Parámetros:
    - coin_id: ID de la criptomoneda
    - vs_currency: moneda de cotización (ej. 'usd')
    - days: rango de días (ej. 1, 7, 30, 90, 180, 365)

    Retorna:
    - DataFrame con columnas: date, open, high, low, close, volume
    """
    import pandas as pd
    import requests

    # --- OHLC data ---
    url_ohlc = f'https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc'
    params = {'vs_currency': vs_currency, 'days': days}
    ohlc_resp = requests.get(url_ohlc, params=params)
    ohlc_resp.raise_for_status()
    ohlc_data = ohlc_resp.json()

    df_ohlc = pd.DataFrame(ohlc_data, columns=['timestamp', 'open', 'high', 'low', 'close'])
    df_ohlc['date'] = pd.to_datetime(df_ohlc['timestamp'], unit='ms')
    df_ohlc.drop(columns='timestamp', inplace=True)

    # --- Volumen data (viene del endpoint market_chart) ---
    url_vol = f'https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart'
    params = {'vs_currency': vs_currency, 'days': days, 'interval': 'daily'}
    vol_resp = requests.get(url_vol, params=params)
    vol_resp.raise_for_status()
    vol_data = vol_resp.json()['total_volumes']

    df_vol = pd.DataFrame(vol_data, columns=['timestamp', 'volume'])
    df_vol['date'] = pd.to_datetime(df_vol['timestamp'], unit='ms')
    df_vol.drop(columns='timestamp', inplace=True)

    # --- Combinar por fecha ---
    df = pd.merge(df_ohlc, df_vol, on='date', how='inner')

    return df


