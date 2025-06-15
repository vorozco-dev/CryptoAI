
📁 README - Proyecto CryptoAI
=============================

CryptoAI es una aplicación desarrollada con Python y Streamlit para visualizar, analizar e interactuar con datos históricos de criptomonedas. Utiliza la API de CoinGecko para obtener precios, volumen y datos OHLC para generar gráficos tipo candlestick con volumen.
Además, CryptoAI permite **registrar tus inversiones** en distintas criptomonedas, llevar seguimiento de tu historial por fechas e inversores, y calcular métricas como el **ROI (Return on Investment)** para ayudarte a identificar la mejor opción de ingreso y tomar decisiones más informadas.

🔧 Requisitos
------------
- Python 3.9 o superior
- pip
- Conexión a Internet (para llamadas a la API de CoinGecko)

📦 Dependencias
--------------
Instálalas ejecutando:

    pip install -r requirements.txt

O manualmente:

    pip install streamlit pandas plotly requests openpyxl

📂 Estructura del proyecto
--------------------------
    /CryptoAI/
    ├── app_streamlit.py           ← Página principal
    ├── data			   ← DB para datos		
    ├── pages/
    │   └── 1_profit.py		   ← Pagina para el calculo de ganancias y registro de inversiones 		
    │   └── 2_analysis.py          ← Pagina secundaria para análisis técnico
    ├── ai			   ← Modulo para la integracion con un agente de AI analisis de la mejor oportunidad de inversion
    ├── api.py                     ← Funciones para conexión a CoinGecko
    ├── processing.py              ← (Opcional) Funciones auxiliares de datos
    ├── requirements.txt           ← Lista de dependencias
    └── README.txt                 ← Este archivo

🚀 Cómo ejecutar
----------------

### Windows
1. Abre `cmd` o PowerShell.
2. Activa tu entorno virtual (si aplica).
3. Ejecuta:

    streamlit run app_streamlit.py

Tambien puede ejecutar el modulo embedado en EXE


### Linux / macOS
1. Abre una terminal.
2. Activa tu entorno virtual (si aplica).
3. Ejecuta:

    streamlit run app_streamlit.py

🌐 Navegador:
La app se abrirá en http://localhost:8501  
También puedes ver las otras páginas desde el menú lateral (por ejemplo, "2_analysis").

🧠 Funcionalidades actuales
---------------------------
✔ Visualización de precios históricos (OHLC)  
✔ Gráficos tipo candlestick interactivos con volumen  
✔ Selección dinámica de monedas y rango de días válidos  
✔ Retry automático ante errores temporales de API  
✔ Interfaz simple y multiplataforma

🔒 Notas
--------
- El endpoint OHLC de CoinGecko solo acepta días: 1, 7, 14, 30, 90, 180, 365.
- Si se pasa un valor diferente, el sistema lo ajustará automáticamente al más cercano.
- La API de CoinGecko tiene limitaciones de tasa. Si ves errores 429, intenta nuevamente luego.

📧 Soporte
----------
Contacto: [vorozco@google.com]
