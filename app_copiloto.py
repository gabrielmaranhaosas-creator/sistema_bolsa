import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from groq import Groq
from typing import Tuple, Dict, Optional, Any
import math
from datetime import datetime
import base64

# ==============================================================================
# 1. CONFIGURAÇÃO DE INFRAESTRUTURA DE UI (FRONT-END INSTITUCIONAL)
# ==============================================================================
st.set_page_config(
    page_title="Terminal Quantamental | Inteligência Institucional", 
    page_icon="💠",
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Estilização Global CSS: Design Profissional, High-Tech e Mobile-Responsive
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=JetBrains+Mono:wght@400;700&display=swap');

    /* Variáveis Globais de Cor - Padrão Institucional Moderno */
    :root {
        --bg-dark: #0B0F19;
        --card-bg: #111827;
        --border-color: #1F2937;
        --text-main: #F3F4F6;
        --text-muted: #9CA3AF;
        --accent-blue: #3B82F6;
        --accent-green: #10B981;
        --accent-red: #EF4444;
        --accent-gold: #F59E0B;
    }

    /* Fundo e Fonte Base */
    .stApp {
        background-color: var(--bg-dark);
        font-family: 'Inter', sans-serif;
        color: var(--text-main);
    }

    /* Cabeçalhos */
    h1, h2, h3, h4 {
        color: #FFFFFF !important;
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    /* Métricas (Cartões de Dados) */
    .stMetric { 
        background-color: var(--card-bg); 
        padding: 1rem; 
        border-radius: 8px; 
        border: 1px solid var(--border-color);
        border-left: 4px solid var(--accent-blue);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: transform 0.2s ease, border-left-color 0.2s ease;
    }
    .stMetric:hover {
        transform: translateY(-2px);
        border-left-color: var(--accent-green);
    }
    .stMetric label { 
        color: var(--text-muted) !important; 
        font-family: 'Inter', sans-serif;
        font-weight: 600; 
        font-size: 0.75rem; 
        text-transform: uppercase; 
        letter-spacing: 0.05em;
    }
    .stMetric div { 
        font-family: 'JetBrains Mono', monospace !important;
        color: var(--text-main) !important; 
        font-size: 1.5rem !important;
    }
    .stMetric [data-testid="stMetricDelta"] div {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.9rem !important;
    }
    
    /* Indicadores Positivo/Negativo */
    .stMetric [data-testid="stMetricDelta"] svg[data-testid="stMetricDeltaIcon-Up"] { color: var(--accent-green); }
    .stMetric [data-testid="stMetricDelta"] div:has(> svg[data-testid="stMetricDeltaIcon-Up"]) { color: var(--accent-green) !important; }
    .stMetric [data-testid="stMetricDelta"] svg[data-testid="stMetricDeltaIcon-Down"] { color: var(--accent-red); }
    .stMetric [data-testid="stMetricDelta"] div:has(> svg[data-testid="stMetricDeltaIcon-Down"]) { color: var(--accent-red) !important; }

    /* Abas (Tabs) - Com Scroll Horizontal para Mobile */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 0; 
        border-bottom: 2px solid var(--border-color); 
        background-color: transparent;
        overflow-x: auto;
        white-space: nowrap;
        -webkit-overflow-scrolling: touch; /* Suavidade no iOS */
        padding-bottom: 5px;
    }
    .stTabs [data-baseweb="tab"] { 
        background-color: transparent; 
        border-radius: 6px 6px 0 0; 
        padding: 0.75rem 1.5rem; 
        border: none;
        color: var(--text-muted);
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] { 
        background-color: var(--card-bg); 
        color: var(--accent-blue) !important; 
        border-bottom: 2px solid var(--accent-blue);
    }

    /* Botões */
    .stButton>button { 
        background-color: var(--accent-blue);
        color: #FFFFFF; 
        font-family: 'Inter', sans-serif;
        font-weight: 600; 
        border-radius: 6px; 
        border: none; 
        padding: 0.5rem 1rem; 
        transition: background-color 0.2s; 
    }
    .stButton>button:hover { 
        background-color: #2563EB; 
        color: #FFFFFF;
    }

    /* Inputs e Selectboxes */
    .stSelectbox div[data-baseweb="select"], .stTextInput input, .stNumberInput input {
        background-color: var(--card-bg) !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-main) !important;
        border-radius: 6px;
    }

    /* Letreiro Institucional (Ticker Tape) */
    .ticker-wrap {
        width: 100%;
        overflow: hidden;
        background-color: var(--card-bg);
        box-sizing: content-box;
        border-top: 1px solid var(--border-color);
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 1.5rem;
        border-radius: 4px;
    }
    .ticker {
        display: inline-block;
        height: 2rem;
        line-height: 2rem;  
        white-space: nowrap;
        padding-right: 100%;
        box-sizing: content-box;
        animation: ticker 40s linear infinite;
        font-family: 'JetBrains Mono', monospace;
        color: var(--accent-blue);
        font-size: 0.85rem;
        letter-spacing: 0.5px;
    }
    @keyframes ticker {
        0% { transform: translate3d(100%, 0, 0); }
        100% { transform: translate3d(-100%, 0, 0); }
    }

    /* Adaptações Mobile Específicas */
    @media (max-width: 768px) {
        .stMetric { padding: 0.75rem; }
        .stMetric div { font-size: 1.25rem !important; }
        h1 { font-size: 1.5rem !important; }
        .stTabs [data-baseweb="tab"] { padding: 0.5rem 1rem; font-size: 0.85rem; }
    }
</style>

<div class="ticker-wrap">
    <div class="ticker">
        💠 TERMINAL QUANTAMENTAL INSTITUCIONAL // CONEXÃO DE DADOS ESTABELECIDA // PROCESSAMENTO ALGORÍTMICO: ATIVO // MOTOR ESTOCÁSTICO: ONLINE // INTELIGÊNCIA ARTIFICIAL: LLAMA 3.1 SINCRONIZADA // MONITORIZAÇÃO CONTÍNUA DE RISCO.
    </div>
</div>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# ==============================================================================
# 2. BASE DE DADOS MACROECONÔMICA GLOBAL
# ==============================================================================
GLOBAL_MACRO_CONTEXT = """
[CENÁRIO MACROECONÔMICO E GEOPOLÍTICO GLOBAL]
- BRASIL (COPOM): Taxa Selic mantida em 14.50% ao ano, configurando um dos maiores juros reais do planeta. Este cenário restritivo asfixia o varejo, alavanca a dívida das empresas de construção e atrai massivamente o capital para a Renda Fixa (CDI). A curva DI Futuro (Jan/31 a 13.36%) precifica risco fiscal elevado (descontrole de gastos públicos). A desancoragem do IPCA (5.04% Focus) anula qualquer chance de corte de juros a curto prazo.
- ESTADOS UNIDOS (FED): Federal Reserve mantém Fed Funds Rate no patamar de 3.50% - 3.75%. O Core CPI (inflação núcleo) cravado em 2.8% demonstra uma inflação de serviços rígida e resistente. O Dólar (DXY) fortalecido drena o capital de risco dos países emergentes, impactando a bolsa brasileira diretamente. O mercado de Treasuries (títulos de 10 anos) suga a liquidez de ações de dividendos.
- EUROPA (BCE): Zona do Euro enfrenta estagnação econômica, liderada pela recessão industrial da Alemanha. O BCE encontra dificuldades entre cortar juros para salvar o crescimento ou mantê-los para combater a inflação fragmentada.
- CHINA (PBoC): Crise imobiliária sistêmica sem resolução. Os estímulos monetários do Banco do Povo da China têm sido insuficientes para reativar o consumo interno e a construção civil, o que derruba a demanda global por aço e minério de ferro.
- GEOPOLÍTICA DE ENERGIA E LOGÍSTICA: O bloqueio persistente do Estreito de Ormuz pelo Irã e os ataques no Mar Vermelho (Canal de Suez) forçaram frotas globais a contornarem o Cabo da Boa Esperança. Resultados: fretes marítimos multiplicados em até 400%, rupturas na cadeia de suprimentos e o petróleo Brent negociado com prêmio de guerra (+25%).
"""

# ==============================================================================
# 3. DICIONÁRIO INSTITUCIONAL DE ATIVOS (CATÁLOGO GLOBAL)
# ==============================================================================
CATALOGO_INSTITUCIONAL = {
    "Índice Bovespa (BVSP)": "^BVSP", "S&P 500 EUA (SPY)": "SPY", "Nasdaq 100 EUA (QQQ)": "QQQ", 
    "Ibovespa ETF (BOVA11)": "BOVA11.SA", "S&P 500 B3 (IVVB11)": "IVVB11.SA", "Índice Small Caps (SMAL11)": "SMAL11.SA",
    "Ouro Físico (GLD)": "GLD", "Petróleo Brent ETF (BNO)": "BNO", "IFIX - Fundos Imobiliários": "^IFIX",
    "Petrobras PN (PETR4)": "PETR4.SA", "Petrobras ON (PETR3)": "PETR3.SA", "Vale S.A (VALE3)": "VALE3.SA", 
    "Gerdau Metalúrgica (GGBR4)": "GGBR4.SA", "CSN Siderurgia (CSNA3)": "CSNA3.SA", "Usiminas (USIM5)": "USIM5.SA",
    "Prio Petróleo (PRIO3)": "PRIO3.SA", "Enauta Petróleo (ENAT3)": "ENAT3.SA", "Suzano Celulose (SUZB3)": "SUZB3.SA", "Klabin (KLBN11)": "KLBN11.SA",
    "SLC Agrícola (SLCE3)": "SLCE3.SA", "São Martinho (SMTO3)": "SMTO3.SA", "JBS (JBSS3)": "JBSS3.SA", 
    "BRF Foods (BRFS3)": "BRFS3.SA", "Marfrig (MRFG3)": "MRFG3.SA",
    "Itaú Unibanco (ITUB4)": "ITUB4.SA", "Banco do Brasil (BBAS3)": "BBAS3.SA", "Bradesco PN (BBDC4)": "BBDC4.SA", 
    "Santander Brasil (SANB11)": "SANB11.SA", "BTG Pactual (BPAC11)": "BPAC11.SA", "B3 S.A. (B3SA3)": "B3SA3.SA", 
    "BB Seguridade (BBSE3)": "BBSE3.SA", "Porto Seguro (PSSA3)": "PSSA3.SA",
    "Eletrobras ON (ELET3)": "ELET3.SA", "Taesa (TAEE11)": "TAEE11.SA", "Equatorial Energia (EQTL3)": "EQTL3.SA", 
    "Isa Cteep (TRPL4)": "TRPL4.SA", "Engie Brasil (EGIE3)": "EGIE3.SA", "Copel (CPLE6)": "CPLE6.SA",
    "Sabesp (SBSP3)": "SBSP3.SA", "Copasa (CSMG3)": "CSMG3.SA",
    "Weg Equipamentos (WEGE3)": "WEGE3.SA", "Localiza (RENT3)": "RENT3.SA", "Magazine Luiza (MGLU3)": "MGLU3.SA", 
    "Lojas Renner (LREN3)": "LREN3.SA", "Assaí Atacadista (ASAI3)": "ASAI3.SA", "Carrefour (CRFB3)": "CRFB3.SA",
    "Rede D'Or (RDOR3)": "RDOR3.SA", "Hapvida (HAPV3)": "HAPV3.SA", "Rumo Logística (RAIL3)": "RAIL3.SA",
    "Cyrela (CYRE3)": "CYRE3.SA", "JHSF (JHSF3)": "JHSF3.SA", "MRV Engenharia (MRVE3)": "MRVE3.SA",
    "Maxi Renda FII (MXRF11)": "MXRF11.SA", "CSHG Logística (HGLG11)": "HGLG11.SA", "Kinea Renda (KNRI11)": "KNRI11.SA",
    "Nvidia Corp (NVDA)": "NVDA", "Apple Inc (AAPL)": "AAPL", "Microsoft (MSFT)": "MSFT", 
    "Alphabet / Google (GOOGL)": "GOOGL", "Amazon (AMZN)": "AMZN", "Tesla Inc (TSLA)": "TSLA", 
    "TSMC Semicondutores (TSM)": "TSM", "Mercado Livre (MELI)": "MELI", "Palantir (PLTR)": "PLTR",
    "Bitcoin (BTC-USD)": "BTC-USD", "Ethereum (ETH-USD)": "ETH-USD", "Solana (SOL-USD)": "SOL-USD", 
    "Dólar / Real (BRL=X)": "BRL=X", "Euro / Real (EURBRL=X)": "EURBRL=X",
    "Pesquisa Manual de Ticker": "OUTRO"
}

# ==============================================================================
# 4. MÓDULO DE INGESTÃO DE DADOS (MARKET DATA & FUNDAMENTOS)
# ==============================================================================
@st.cache_data(ttl=600)
def fetch_market_data(ticker: str, period: str = "2y") -> Optional[pd.DataFrame]:
    try:
        data = yf.Ticker(ticker).history(period=period)
        if data.empty or len(data) < 50:
            return None
        if data.index.tz is not None:
            data.index = data.index.tz_localize(None)
        return data
    except Exception:
        return None

@st.cache_data(ttl=3600)
def fetch_fundamental_data(ticker: str) -> Dict[str, Any]:
    try:
        info = yf.Ticker(ticker).info
        return {
            'Market Cap': info.get('marketCap', 'N/A'),
            'P/E Ratio (P/L)': info.get('trailingPE', 'N/A'),
            'Forward P/E': info.get('forwardPE', 'N/A'),
            'Dividend Yield': info.get('dividendYield', 'N/A'),
            'Price to Book (P/VP)': info.get('priceToBook', 'N/A'),
            'EBITDA Margin': info.get('ebitdaMargins', 'N/A'),
            'Profit Margin': info.get('profitMargins', 'N/A'),
            'ROE (Retorno s/ Patrimônio)': info.get('returnOnEquity', 'N/A'),
            'Debt to Equity (Dívida/Patrimônio)': info.get('debtToEquity', 'N/A'),
            'Current Ratio (Liquidez)': info.get('currentRatio', 'N/A'),
        }
    except Exception:
        return {}

def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    """Função de exportação de dados para download."""
    return df.to_csv().encode('utf-8')

# ==============================================================================
# 5. MOTOR MATEMÁTICO INSTITUCIONAL (INDICADORES AVANÇADOS)
# ==============================================================================
def calculate_advanced_indicators(df: pd.DataFrame, ma_window: int = 20) -> Tuple[pd.DataFrame, Dict[str, float], float, float]:
    df_calc = df.copy()
    close = df_calc['Close']
    high = df_calc['High']
    low = df_calc['Low']
    volume = df_calc['Volume']
    df_calc['Close_Price'] = close
    
    df_calc['SMA'] = close.rolling(window=ma_window).mean()
    df_calc['EMA_9'] = close.ewm(span=9, adjust=False).mean()
    df_calc['EMA_21'] = close.ewm(span=21, adjust=False).mean()
    
    std_dev = close.rolling(window=ma_window).std()
    df_calc['BB_Upper'] = df_calc['SMA'] + (std_dev * 2)
    df_calc['BB_Lower'] = df_calc['SMA'] - (std_dev * 2)
    df_calc['BB_Width'] = (df_calc['BB_Upper'] - df_calc['BB_Lower']) / df_calc['SMA']
    
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df_calc['RSI'] = 100 - (100 / (1 + (gain / loss)))
    
    df_calc['MACD'] = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
    df_calc['Signal_Line'] = df_calc['MACD'].ewm(span=9, adjust=False).mean()
    df_calc['MACD_Hist'] = df_calc['MACD'] - df_calc['Signal_Line']
    
    tr = pd.concat([high - low, abs(high - close.shift(1)), abs(low - close.shift(1))], axis=1).max(axis=1)
    df_calc['ATR'] = tr.rolling(window=14).mean()
    
    lowest_low = low.rolling(window=14).min()
    highest_high = high.rolling(window=14).max()
    df_calc['Stoch_K'] = 100 * ((close - lowest_low) / (highest_high - lowest_low))
    
    obv = np.where(close > close.shift(1), volume, np.where(close < close.shift(1), -volume, 0))
    df_calc['OBV'] = pd.Series(obv, index=df_calc.index).cumsum()
    
    typical_price = (high + low + close) / 3
    raw_money_flow = typical_price * volume
    positive_flow = np.where(typical_price > typical_price.shift(1), raw_money_flow, 0)
    negative_flow = np.where(typical_price < typical_price.shift(1), raw_money_flow, 0)
    positive_mf = pd.Series(positive_flow, index=df_calc.index).rolling(window=14).sum()
    negative_mf = pd.Series(negative_flow, index=df_calc.index).rolling(window=14).sum()
    mfi_ratio = positive_mf / negative_mf
    df_calc['MFI'] = 100 - (100 / (1 + mfi_ratio))
    
    recent_df = df_calc.tail(252)
    max_p = recent_df['High'].max()
    min_p = recent_df['Low'].min()
    diff = max_p - min_p
    fibo_levels = {
        '100.0% (Topo)': max_p,
        '61.8% (Ouro Superior)': max_p - 0.382 * diff,
        '50.0% (Equilíbrio)': max_p - 0.5 * diff,
        '38.2% (Ouro Inferior)': max_p - 0.618 * diff,
        '0.0% (Fundo)': min_p
    }

    daily_returns = close.pct_change()
    ann_return = daily_returns.mean() * 252 * 100 
    ann_vol = daily_returns.std() * np.sqrt(252) * 100
    risk_free_rate = 14.50 
    sharpe_ratio = (ann_return - risk_free_rate) / ann_vol if ann_vol > 0 else 0

    return df_calc, fibo_levels, ann_return, sharpe_ratio

# ==============================================================================
# Renderizador Gráfico High-Tech (Plotly)
# ==============================================================================
def plot_master_chart(df: pd.DataFrame, ticker: str, fibo: Dict[str, float]) -> go.Figure:
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.04, 
                        subplot_titles=(f'PRICE ACTION & BOLLINGER BANDS', 'MFI (MONEY FLOW INDEX) & OBV', 'MACD (MOMENTUM)'),
                        row_width=[0.2, 0.2, 0.6])
    
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close_Price'], 
        name='Preço',
        increasing_line_color='#10B981', decreasing_line_color='#EF4444'
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], mode='lines', line=dict(color='#F59E0B', width=1.5), name='SMA'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], mode='lines', line=dict(color='rgba(59, 130, 246, 0.4)', width=1, dash='dash'), name='Bollinger Sup'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], mode='lines', line=dict(color='rgba(59, 130, 246, 0.4)', width=1, dash='dash'), name='Bollinger Inf', fill='tonexty', fillcolor='rgba(59, 130, 246, 0.05)'), row=1, col=1)
    
    fibo_colors = ['#EF4444', '#F97316', '#3B82F6', '#10B981', '#8B5CF6']
    for (level_name, price), color in zip(fibo.items(), fibo_colors):
        fig.add_hline(y=price, line_dash="dot", line_color=color, line_width=1, annotation_text=level_name, annotation_position="top right", annotation_font_color=color, row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df['MFI'], mode='lines', line=dict(color='#3B82F6', width=2), name='MFI (Money Flow)'), row=2, col=1)
    fig.add_hline(y=80, line_dash="dot", line_color="#EF4444", row=2, col=1)
    fig.add_hline(y=20, line_dash="dot", line_color="#10B981", row=2, col=1)

    colors_macd = ['#10B981' if val >= 0 else '#EF4444' for val in df['MACD_Hist']]
    fig.add_trace(go.Bar(x=df.index, y=df['MACD_Hist'], marker_color=colors_macd, name='Histograma'), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], mode='lines', line=dict(color='#3B82F6', width=1.5), name='MACD'), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Signal_Line'], mode='lines', line=dict(color='#F59E0B', width=1.5), name='Sinal'), row=3, col=1)
    
    fig.update_layout(
        template="plotly_dark", 
        xaxis_rangeslider_visible=False, 
        height=850, 
        margin=dict(l=10, r=10, t=40, b=10), 
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#111827",
        font=dict(family="Inter", color="#F3F4F6"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#1F2937')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#1F2937')
    return fig

# ==============================================================================
# 6. MOTOR DE BACKTESTING VETORIZADO
# ==============================================================================
def run_vectorized_backtest(df: pd.DataFrame, fast_period: int = 9, slow_period: int = 21) -> Dict[str, Any]:
    bt_df = df.copy()
    bt_df['EMA_Fast'] = bt_df['Close_Price'].ewm(span=fast_period, adjust=False).mean()
    bt_df['EMA_Slow'] = bt_df['Close_Price'].ewm(span=slow_period, adjust=False).mean()
    
    bt_df['Signal'] = 0
    bt_df.loc[bt_df['EMA_Fast'] > bt_df['EMA_Slow'], 'Signal'] = 1
    bt_df['Daily_Return'] = bt_df['Close_Price'].pct_change()
    bt_df['Strategy_Return'] = bt_df['Signal'].shift(1) * bt_df['Daily_Return']
    
    bt_df['Equity_Curve'] = (1 + bt_df['Strategy_Return'].fillna(0)).cumprod()
    bt_df['Buy_Hold_Curve'] = (1 + bt_df['Daily_Return'].fillna(0)).cumprod()
    
    total_strat_return = (bt_df['Equity_Curve'].iloc[-1] - 1) * 100
    total_bh_return = (bt_df['Buy_Hold_Curve'].iloc[-1] - 1) * 100
    
    rolling_max = bt_df['Equity_Curve'].cummax()
    drawdown = (bt_df['Equity_Curve'] - rolling_max) / rolling_max
    max_drawdown = drawdown.min() * 100
    
    bt_df['Trade_Change'] = bt_df['Signal'].diff()
    trades = bt_df[bt_df['Trade_Change'] == 1]
    
    winning_days = len(bt_df[(bt_df['Signal'] == 1) & (bt_df['Daily_Return'] > 0)])
    losing_days = len(bt_df[(bt_df['Signal'] == 1) & (bt_df['Daily_Return'] <= 0)])
    total_active_days = winning_days + losing_days
    win_rate = (winning_days / total_active_days * 100) if total_active_days > 0 else 0

    return {
        'total_return_pct': total_strat_return,
        'buy_hold_pct': total_bh_return,
        'max_drawdown_pct': max_drawdown,
        'win_rate_pct': win_rate,
        'total_trades': len(trades),
        'curve_df': bt_df[['Equity_Curve', 'Buy_Hold_Curve']].dropna()
    }

# ==============================================================================
# 7. MOTOR DE SAZONALIDADE HISTÓRICA 
# ==============================================================================
def calculate_seasonality(df: pd.DataFrame) -> pd.DataFrame:
    df_saz = df.copy()
    monthly = df_saz['Close_Price'].resample('ME').last()
    monthly_ret = monthly.pct_change() * 100
    seasonality = monthly_ret.groupby(monthly_ret.index.month).mean().to_frame(name='Avg_Return_Pct')
    meses = {1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun', 
             7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'}
    seasonality.index = seasonality.index.map(meses)
    return seasonality

def plot_seasonality(seasonality_df: pd.DataFrame, ticker: str) -> go.Figure:
    colors = ['#10B981' if val >= 0 else '#EF4444' for val in seasonality_df['Avg_Return_Pct']]
    fig = go.Figure(data=[go.Bar(
        x=seasonality_df.index, 
        y=seasonality_df['Avg_Return_Pct'],
        marker_color=colors,
        text=[f"{val:.2f}%" for val in seasonality_df['Avg_Return_Pct']],
        textposition='auto',
        marker_line_color='#1F2937',
        marker_line_width=1.5,
        opacity=0.9
    )])
    fig.update_layout(title=f"Sazonalidade Histórica Mensal: {ticker}",
                      yaxis_title="Retorno Médio (%)", template="plotly_dark", 
                      height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#111827",
                      font=dict(family="Inter", color="#F3F4F6"))
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#1F2937')
    return fig

# ==============================================================================
# 8. SIMULADOR ESTOCÁSTICO (MONTE CARLO RANDOM WALK)
# ==============================================================================
def run_monte_carlo_simulation(df: pd.DataFrame, days_ahead: int = 30, simulations: int = 200) -> Tuple[np.ndarray, go.Figure, float]:
    log_returns = np.log(1 + df['Close_Price'].pct_change()).dropna()
    u = log_returns.mean()
    var = log_returns.var()
    drift = u - (0.5 * var)
    stdev = log_returns.std()
    
    daily_returns = np.exp(drift + stdev * np.random.normal(0, 1, (days_ahead, simulations)))
    price_paths = np.zeros_like(daily_returns)
    price_paths[0] = df['Close_Price'].iloc[-1]
    
    for t in range(1, days_ahead):
        price_paths[t] = price_paths[t-1] * daily_returns[t]
        
    final_prices = price_paths[-1]
    expected_price = np.mean(final_prices)
    
    fig = go.Figure()
    for i in range(simulations):
        fig.add_trace(go.Scatter(y=price_paths[:, i], mode='lines', line=dict(color='rgba(59, 130, 246, 0.05)', width=1), showlegend=False))
    
    fig.add_trace(go.Scatter(y=price_paths.mean(axis=1), mode='lines', line=dict(color='#F59E0B', width=3), name='Caminho Médio Esperado'))
    fig.update_layout(title=f"Estocástico: {simulations} Caminhos Aleatórios ({days_ahead} pregões)",
                      yaxis_title="Projeção de Preço", template="plotly_dark", height=450, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#111827",
                      font=dict(family="Inter", color="#F3F4F6"))
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#1F2937')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#1F2937')
    return price_paths, fig, expected_price

# ==============================================================================
# 9. MOTOR EXPANDIDO BLACK-SCHOLES (COM GREGAS DE RISCO)
# ==============================================================================
def standard_normal_pdf(x: float) -> float:
    return math.exp(-0.5 * x**2) / math.sqrt(2 * math.pi)

def norm_cdf(x: float) -> float:
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

def black_scholes_greeks(S: float, K: float, T: float, r: float, sigma: float) -> Dict[str, float]:
    if T <= 0 or sigma <= 0: return {'call_price': 0, 'put_price': 0, 'delta_call': 0, 'gamma': 0, 'vega': 0, 'theta_call': 0}
    
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    
    call_price = S * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)
    put_price = K * math.exp(-r * T) * norm_cdf(-d2) - S * norm_cdf(-d1)
    
    delta_call = norm_cdf(d1)
    gamma = standard_normal_pdf(d1) / (S * sigma * math.sqrt(T))
    vega = S * standard_normal_pdf(d1) * math.sqrt(T) / 100 
    
    theta_call_part1 = -(S * standard_normal_pdf(d1) * sigma) / (2 * math.sqrt(T))
    theta_call_part2 = r * K * math.exp(-r * T) * norm_cdf(d2)
    theta_call = (theta_call_part1 - theta_call_part2) / 365 
    
    return {
        'call_price': call_price, 'put_price': put_price, 
        'delta_call': delta_call, 'gamma': gamma, 'vega': vega, 'theta_call': theta_call
    }

# ==============================================================================
# 10. O ORÁCULO QUANTAMENTAL (MOTOR GENERATIVO GROQ CLOUD MULTI-PERSONA)
# ==============================================================================
def generate_ai_response(prompt: str, context_data: str, api_key: str, persona: str) -> str:
    try:
        client = Groq(api_key=api_key)
        
        if persona == "Estrategista Macro (Foco em Juros e Geopolítica)":
            foco = "A prioridade máxima é cruzar o preço do ativo com a taxa Selic (14.50%), inflação e dados globais. Explique o cenário macroeconómico."
        elif persona == "Quant Trader (Foco em Backtest e Volatilidade)":
            foco = "A prioridade máxima é analisar o Backtest, os níveis de Fibonacci, Monte Carlo e a volatilidade. Foco rigoroso na matemática gráfica e quantitativa."
        else:
            foco = "A prioridade é analisar os fundamentos, múltiplos contábeis (P/L, ROE) e avaliar o risco paramétrico para dimensionamento de posições."
        
        system_instruction = f"""És o 'Cérebro Quantamental', o Motor de Inteligência Artificial de um Terminal Institucional.
        
        DIRETRIZES DA PERSONA:
        {foco}
        
        REGRAS INQUEBRÁVEIS:
        1. Tens acesso a um ficheiro massivo de dados processados. NUNCA inventes números. Baseia-te EXCLUSIVAMENTE nos dados fornecidos.
        2. Mantém uma postura analítica, institucional, pragmática e realista.
        3. FORMATAÇÃO: É PROIBIDO o uso de LaTeX no texto. Usa 'R$' ou 'USD'. Utiliza Bullet Points de forma estratégica para facilitar a leitura.
        4. O operador procura precisão. Sê direto, denso e fundamenta as decisões na matriz estatística e técnica disponível.
        """
        
        payload = f"{GLOBAL_MACRO_CONTEXT}\n\n[MATRIZ ALGORÍTMICA ABSOLUTA DO ATIVO]\n{context_data}"
        user_message = f"[DATA LAKE INJETADO]\n{payload}\n\n[COMANDO DO OPERADOR]\n{prompt}"
        
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": user_message}],
            model="llama-3.1-8b-instant",
            temperature=0.35, 
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"ALERTA CRÍTICO: Falha na comunicação com o servidor de IA (Groq). Verifique a chave de API e a conexão. Erro detalhado: {e}"

# ==============================================================================
# 11. THREAD PRINCIPAL DO TERMINAL (DASHBOARD & INTERFACE RESPONSIVA)
# ==============================================================================
def main():
    # Cabeçalho Limpo e Profissional
    st.markdown("<h1><span style='color:#3B82F6'>💠 TERMINAL QUANTAMENTAL</span> <span style='color:#4B5563; font-weight: 300;'>| INTELIGÊNCIA INSTITUCIONAL</span></h1>", unsafe_allow_html=True)
    
    # BARRA LATERAL (CONTROLE E EXTRAÇÃO)
    with st.sidebar:
        st.markdown("<h3 style='color:#9CA3AF; font-size:0.9rem; text-transform:uppercase;'>Painel de Controlo</h3>", unsafe_allow_html=True)
        selecao_ativo = st.selectbox("Selecione o Ativo:", list(CATALOGO_INSTITUCIONAL.keys()))
        
        if selecao_ativo == "Pesquisa Manual de Ticker":
            ticker = st.text_input("Ticker (Ex: BBDC4.SA):", value="PETR4.SA").upper()
        else:
            ticker = CATALOGO_INSTITUCIONAL[selecao_ativo]
            
        col_t1, col_t2 = st.columns(2)
        with col_t1: period = st.selectbox("Período", ["6mo", "1y", "2y", "5y", "max"], index=2)
        with col_t2: ma_window = st.number_input("SMA Base", min_value=5, max_value=200, value=20)
        
        st.markdown("---")
        api_key = "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"
        
        # Status do Sistema Profissional
        st.markdown("""
        <div style='background-color: var(--card-bg); border: 1px solid var(--border-color); padding: 1rem; border-radius: 6px; font-family: "JetBrains Mono", monospace; font-size: 0.8rem;'>
            <span style='color:var(--accent-green)'>● STATUS: OPERACIONAL</span><br><br>
            <span style='color:var(--text-muted)'>[✓] BACKTEST ENGINE</span><br>
            <span style='color:var(--text-muted)'>[✓] BLACK-SCHOLES</span><br>
            <span style='color:var(--text-muted)'>[✓] LLAMA 3.1 NPU</span>
        </div>
        """, unsafe_allow_html=True)

    # PROCESSAMENTO E INGESTÃO DE DADOS
    df_raw = fetch_market_data(ticker, period)
    fundament_data = fetch_fundamental_data(ticker)
    contexto_invisivel = "Pipeline Vazio."
    
    if df_raw is not None:
        # EXECUÇÃO DO PIPELINE MATEMÁTICO
        df_processed, fibo_levels, ann_return, sharpe_ratio = calculate_advanced_indicators(df_raw, ma_window)
        mc_paths, mc_fig, mc_expected_price = run_monte_carlo_simulation(df_processed, days_ahead=30, simulations=100)
        backtest_results = run_vectorized_backtest(df_processed, fast_period=9, slow_period=21)
        seasonality_df = calculate_seasonality(df_processed)
        
        # EXPORTAÇÃO DE DADOS (NOVA FUNCIONALIDADE)
        with st.sidebar:
            st.markdown("<br><h3 style='color:#9CA3AF; font-size:0.9rem; text-transform:uppercase;'>Exportação de Dados</h3>", unsafe_allow_html=True)
            csv_data = convert_df_to_csv(df_processed)
            st.download_button(
                label="📥 Transferir Matriz de Dados (CSV)",
                data=csv_data,
                file_name=f"{ticker}_quant_matrix.csv",
                mime="text/csv",
                use_container_width=True
            )

        # FOTOGRAFIA EM TEMPO REAL
        ultima = df_processed.iloc[-1]
        c_price, c_sma, c_rsi, c_macd, c_sig = ultima['Close_Price'], ultima['SMA'], ultima['RSI'], ultima['MACD'], ultima['Signal_Line']
        c_atr, c_bbw, c_stoch, c_obv, c_mfi = ultima['ATR'], ultima['BB_Width'], ultima['Stoch_K'], ultima['OBV'], ultima['MFI']
        
        trend = "ALTA TÉCNICA" if c_price > c_sma else "PRESSÃO VENDEDORA"
        if pd.isna(c_rsi): rsi_txt = "Liquidez Insuficiente"
        elif c_rsi > 70: rsi_txt = f"{c_rsi:.1f} (SOBRECOMPRADO)"
        elif c_rsi < 30: rsi_txt = f"{c_rsi:.1f} (SOBREVENDIDO)"
        else: rsi_txt = f"{c_rsi:.1f} (NEUTRO)"
        
        fibo_str = ", ".join([f"{k}: R$ {v:.2f}" for k, v in fibo_levels.items()])
        fundamentos_str = ", ".join([f"{k}: {v}" for k, v in fundament_data.items()]) if fundament_data else "N/A"
        
        current_month = datetime.now().month
        meses = {1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'}
        current_month_str = meses.get(current_month, '')
        saz_atual = seasonality_df.loc[current_month_str, 'Avg_Return_Pct'] if current_month_str in seasonality_df.index else 0
        
        contexto_invisivel = f"""
        [TELEMETRIA QUANTITATIVA E TÉCNICA - ATIVO: {ticker}]
        - Cotação Atual: R$ {c_price:.2f}
        - Tendência ({ma_window}d): {trend}
        - Força Relativa (RSI 14): {rsi_txt} | Money Flow Index (MFI): {c_mfi:.1f}
        - Volatilidade Diária Risco (ATR 14): R$ {c_atr:.2f}
        - Estocástico Lento (%K): {c_stoch:.1f}% | Bollinger Width Squeeze: {c_bbw:.3f}
        - Retorno Anualizado da Série: {ann_return:.2f}% | Sharpe Ratio: {sharpe_ratio:.2f} (Tx Livre Risco 14.50%)
        
        [NÍVEIS DE FIBONACCI]
        {fibo_str}
        
        [MONTE CARLO RANDOM WALK (Próximos 30 dias)]
        - Preço Médio Esperado: R$ {mc_expected_price:.2f}
        
        [BACKTEST ESTRATÉGIA EMA 9 vs 21]
        - Retorno Total da Estratégia: {backtest_results['total_return_pct']:.2f}% (vs Buy & Hold: {backtest_results['buy_hold_pct']:.2f}%)
        - Max Drawdown (Risco): {backtest_results['max_drawdown_pct']:.2f}%
        - Win Rate Estimado: {backtest_results['win_rate_pct']:.1f}%
        
        [SAZONALIDADE]
        - Mês Atual ({current_month_str}): Média histórica de {saz_atual:.2f}%.
        
        [BALANÇO FUNDAMENTALISTA E MÚLTIPLOS]
        {fundamentos_str}
        """

    # -------------------------------------------------------------------------
    # LAYOUT RESPONSIVO: 6 ABAS DE ANÁLISE PROFUNDA
    # -------------------------------------------------------------------------
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 GRÁFICO E PREÇO", 
        "⚙️ RISCO & OPÇÕES", 
        "🎲 MODELOS ESTATÍSTICOS",
        "🏢 FUNDAMENTOS (DRE)",
        "⚖️ TESTE DE ESTRATÉGIA",
        "🧠 CÉREBRO IA"
    ])

    with tab1:
        if df_raw is not None:
            c1, c2, c3, c4 = st.columns(4)
            delta_pct = ((c_price / df_raw['Close'].iloc[-2]) - 1) * 100 if len(df_raw) > 1 else 0
            c1.metric("COTAÇÃO ATUAL", f"R$ {c_price:.2f}", delta=f"{delta_pct:.2f}%")
            c2.metric("VOLATILIDADE (ATR)", f"R$ {c_atr:.2f}")
            c3.metric("FLUXO DE CAPITAL (MFI)", f"{c_mfi:.1f}")
            c4.metric("RENTABILIDADE ANUAL", f"{ann_return:.1f}%", delta=f"Índ. Sharpe: {sharpe_ratio:.2f}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            fig_master = plot_master_chart(df_processed, ticker, fibo_levels)
            st.plotly_chart(fig_master, use_container_width=True)
        else:
            st.error("Falha na sincronização dos dados de mercado. Verifique o ticker selecionado ou a sua ligação à internet.")

    with tab2:
        if df_raw is not None:
            st.markdown("### Dimensionamento de Posição Paramétrica")
            with st.form("risk_form"):
                c_f1, c_f2 = st.columns(2)
                with c_f1:
                    capital = st.number_input("Capital Operacional Alocado (R$)", min_value=0.0, value=250000.0, step=10000.0)
                    risk_pct = st.number_input("Tolerância a Drawdown (%)", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
                with c_f2:
                    entry_price = st.number_input("Alvo de Execução (Entrada)", min_value=0.0, value=c_price, step=0.01)
                    stop_loss = st.number_input("Nível de Proteção (Stop Loss)", min_value=0.0, value=c_price - (c_atr * 1.5), step=0.01)
                sub_btn = st.form_submit_button("PROCESSAR ALOCAÇÃO")

            if sub_btn:
                if stop_loss >= entry_price:
                    st.error("ALERTA: O Stop Loss deve ser estritamente inferior ao alvo de entrada para operações compradas (Long).")
                else:
                    risk_val = capital * (risk_pct / 100)
                    shares = int(risk_val // (entry_price - stop_loss))
                    st.success("✅ Dimensionamento matemático aprovado.")
                    cr1, cr2, cr3 = st.columns(3)
                    cr1.metric("LOTES PERMITIDOS", f"{shares} Ações")
                    cr2.metric("EXPOSIÇÃO FINANCEIRA", f"R$ {(shares * entry_price):,.2f}")
                    cr3.metric("RISCO DE CAPITAL BLOQUEADO", f"R$ {risk_val:,.2f}")
            
            st.markdown("---")
            st.markdown("### Motor Europeu de Precificação (Black-Scholes & Gregas)")
            with st.form("bs_form"):
                cb1, cb2, cb3 = st.columns(3)
                with cb1:
                    bs_spot = st.number_input("Preço Base (Spot)", value=c_price, step=0.1)
                    bs_strike = st.number_input("Preço de Exercício (Strike)", value=c_price * 1.05, step=0.1)
                with cb2:
                    bs_days = st.number_input("Dias Úteis P/ Vencimento", value=21, min_value=1)
                    bs_rf = st.number_input("Taxa de Juro S/ Risco (%)", value=14.50, step=0.10)
                with cb3:
                    vol_estimada = (c_atr / c_price) * math.sqrt(252) * 100
                    bs_vol = st.number_input("Volatilidade Implícita Anual (%)", value=float(vol_estimada), step=1.0)
                bs_submit = st.form_submit_button("COMPUTAR DERIVATIVO")
                
            if bs_submit:
                greeks = black_scholes_greeks(bs_spot, bs_strike, bs_days/252.0, bs_rf/100.0, bs_vol/100.0)
                st.success("✅ Simulação Estocástica de Opções Concluída.")
                
                cg1, cg2, cg3 = st.columns(3)
                cg1.metric("PRÊMIO TEÓRICO CALL", f"R$ {greeks['call_price']:.3f}")
                cg2.metric("PRÊMIO TEÓRICO PUT", f"R$ {greeks['put_price']:.3f}")
                cg3.metric("DELTA (Prob. de Exercício)", f"{greeks['delta_call'] * 100:.1f}%")
                
                cg4, cg5, cg6 = st.columns(3)
                cg4.metric("GAMMA (Taxa de Variação)", f"{greeks['gamma']:.4f}")
                cg5.metric("VEGA (Sens. Volatilidade)", f"R$ {greeks['vega']:.3f}")
                cg6.metric("THETA (Decaimento Temporal)", f"R$ {greeks['theta_call']:.3f}")

    with tab3:
        if df_raw is not None:
            c_alg1, c_alg2 = st.columns([1, 1])
            with c_alg1:
                st.markdown("### Mapa de Sazonalidade")
                st.markdown("<p style='color:var(--text-muted); font-size:0.9rem;'>Avaliação do retorno percentual médio mensal baseada na série temporal analisada.</p>", unsafe_allow_html=True)
                fig_saz = plot_seasonality(seasonality_df, ticker)
                st.plotly_chart(fig_saz, use_container_width=True)
            with c_alg2:
                st.markdown("### Simulação Estocástica (Monte Carlo)")
                st.markdown("<p style='color:var(--text-muted); font-size:0.9rem;'>Geração de 100 trajetórias de preços prováveis usando a variância histórica.</p>", unsafe_allow_html=True)
                st.plotly_chart(mc_fig, use_container_width=True)
                st.markdown(f"<div style='background-color:var(--card-bg); border: 1px solid var(--accent-blue); padding: 10px; border-radius: 6px; text-align:center;'>ALVO ESTATÍSTICO (30 DIAS): <strong>R$ {mc_expected_price:.2f}</strong></div>", unsafe_allow_html=True)

    with tab4:
        st.markdown("### Diagnóstico Fundamentalista (Múltiplos e Balanço)")
        if fundament_data:
            col_f1, col_f2, col_f3 = st.columns(3)
            col_f1.metric("VALOR DE MERCADO (CAP)", f"{fundament_data.get('Market Cap', 'N/A')}")
            col_f1.metric("P/L (PREÇO / LUCRO)", f"{fundament_data.get('P/E Ratio (P/L)', 'N/A')}")
            col_f1.metric("DIVIDEND YIELD", f"{fundament_data.get('Dividend Yield', 0) * 100 if isinstance(fundament_data.get('Dividend Yield'), (int, float)) else 'N/A'}%")
            
            col_f2.metric("P/VP (PREÇO / V. PATR.)", f"{fundament_data.get('Price to Book (P/VP)', 'N/A')}")
            col_f2.metric("ROE (RENTABILIDADE)", f"{fundament_data.get('ROE (Retorno s/ Patrimônio)', 0) * 100 if isinstance(fundament_data.get('ROE (Retorno s/ Patrimônio)'), (int, float)) else 'N/A'}%")
            col_f2.metric("MARGEM LÍQUIDA", f"{fundament_data.get('Profit Margin', 0) * 100 if isinstance(fundament_data.get('Profit Margin'), (int, float)) else 'N/A'}%")
            
            col_f3.metric("DÍVIDA / PATRIMÓNIO", f"{fundament_data.get('Debt to Equity (Dívida/Patrimônio)', 'N/A')}")
            col_f3.metric("LIQUIDEZ CORRENTE", f"{fundament_data.get('Current Ratio (Liquidez)', 'N/A')}")
            col_f3.metric("MARGEM EBITDA", f"{fundament_data.get('EBITDA Margin', 0) * 100 if isinstance(fundament_data.get('EBITDA Margin'), (int, float)) else 'N/A'}%")
        else:
            st.warning("Múltiplos indisponíveis para a entidade selecionada (frequente em Índices ou Fundos ETF).")

    with tab5:
        if df_raw is not None:
            st.markdown("### Backtest Vetorizado: Cruzamento de Médias Móveis (EMA 9 vs 21)")
            
            c_bt1, c_bt2, c_bt3, c_bt4 = st.columns(4)
            c_bt1.metric("RETORNO ESTRATÉGICO", f"{backtest_results['total_return_pct']:.2f}%")
            c_bt2.metric("BENCHMARK (BUY & HOLD)", f"{backtest_results['buy_hold_pct']:.2f}%")
            c_bt3.metric("DRAWDOWN MÁXIMO", f"{backtest_results['max_drawdown_pct']:.2f}%")
            c_bt4.metric("WIN RATE (EFICIÊNCIA)", f"{backtest_results['win_rate_pct']:.1f}%")
            
            curve_df = backtest_results['curve_df']
            fig_eq = go.Figure()
            fig_eq.add_trace(go.Scatter(x=curve_df.index, y=curve_df['Equity_Curve'], mode='lines', name='Algoritmo Cross EMA', line=dict(color='#10B981', width=2)))
            fig_eq.add_trace(go.Scatter(x=curve_df.index, y=curve_df['Buy_Hold_Curve'], mode='lines', name='Buy & Hold', line=dict(color='#6B7280', width=2, dash='dot')))
            fig_eq.update_layout(title="CURVA DE CRESCIMENTO DE CAPITAL (EQUITY CURVE)", template="plotly_dark", height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#111827", font=dict(family="Inter", color="#F3F4F6"))
            fig_eq.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#1F2937')
            fig_eq.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#1F2937')
            st.plotly_chart(fig_eq, use_container_width=True)

    with tab6:
        if df_raw is not None:
            st.markdown("### Centro de Comando IA (Integração Llama 3.1)")
            st.markdown("<p style='color:var(--text-muted); font-size:0.9rem;'>O modelo avalia a totalidade do ecossistema de dados processados, incluindo matemática quantitativa, balanço financeiro e variáveis macroeconómicas.</p>", unsafe_allow_html=True)
            
            col_persona, col_btn = st.columns([3, 1])
            with col_persona:
                persona_ia = st.radio("Enfoque Analítico da Resposta:", 
                                     ["Gestão de Risco e Análise Fundamentalista", 
                                      "Estratégia Macro e Geopolítica Global", 
                                      "Trading Quantitativo e Modelos de Volatilidade"], horizontal=True)
            with col_btn:
                if st.button("🧹 LIMPAR HISTÓRICO", use_container_width=True):
                    st.session_state.messages = []
                    st.rerun()
            
            st.markdown("---")
            chat_container = st.container(height=500)
            with chat_container:
                for msg in st.session_state.messages:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

            if prompt := st.chat_input("Introduza a sua questão (Ex: 'Analise o risco de mercado com base no backtest e no MFI atual.')"):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with chat_container:
                    with st.chat_message("user"): st.markdown(prompt)
                
                with chat_container:
                    with st.chat_message("assistant"):
                        with st.spinner("Compilando a matriz quantamental..."):
                            resp = generate_ai_response(prompt, contexto_invisivel, api_key, persona_ia)
                            st.markdown(resp)
                            st.session_state.messages.append({"role": "assistant", "content": resp})

if __name__ == "__main__":
    main()