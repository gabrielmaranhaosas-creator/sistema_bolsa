import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from groq import Groq
from typing import Tuple, Dict, Optional, Any, List
import math
from datetime import datetime
import base64

# ==============================================================================
# 1. CORE & INFRAESTRUTURA DE DESIGN SYSTEM (V14 INSTITUTIONAL ALPHA)
# ==============================================================================
st.set_page_config(
    page_title="Terminal Quantamental | Alpha", 
    page_icon="⚡",
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Injeção de Design System (CSS Avançado Nível Palantir / Linear / Bloomberg)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

    /* Variáveis de Design (Tokens Cognitivos) */
    :root {
        --bg-app: #09090b;          /* Zinc 950 - Fundo Profundo */
        --bg-panel: #18181b;        /* Zinc 900 - Superfícies */
        --border-subtle: #27272a;   /* Zinc 800 - Bordas */
        --border-focus: #3f3f46;    /* Zinc 700 - Hover de Bordas */
        --text-primary: #fafafa;    /* Zinc 50 - Texto Principal */
        --text-secondary: #a1a1aa;  /* Zinc 400 - Texto Secundário */
        --text-tertiary: #52525b;   /* Zinc 600 - Texto Desabilitado */
        
        --accent-blue: #3b82f6;     /* Blue 500 - Ações e Info */
        --accent-blue-hover: #2563eb;
        --accent-green: #10b981;    /* Emerald 500 - Alta/Positivo */
        --accent-red: #f43f5e;      /* Rose 500 - Risco/Baixa */
        --accent-gold: #eab308;     /* Yellow 500 - Alertas/Sinal */
    }

    /* Reset e Fundo Global */
    .stApp {
        background-color: var(--bg-app);
        font-family: 'Inter', -apple-system, sans-serif;
        color: var(--text-primary);
    }
    
    /* Esconder elementos nativos do Streamlit */
    header { visibility: hidden; }
    footer { visibility: hidden; }

    /* Tipografia de Cabeçalhos */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
    }

    /* Sistema de Cards (Métricas) - Redução de Fadiga Ocular */
    [data-testid="metric-container"] {
        background-color: var(--bg-panel);
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        padding: 1.25rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: all 0.2s ease-in-out;
    }
    [data-testid="metric-container"]:hover {
        border-color: var(--border-focus);
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    /* Labels das Métricas */
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    
    /* Valores Numéricos (JetBrains Mono para precisão) */
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        color: var(--text-primary) !important;
        font-size: 1.75rem !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em;
    }
    
    /* Indicadores de Delta */
    [data-testid="stMetricDelta"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
    }
    [data-testid="stMetricDelta"] > div:has(> svg[data-testid="stMetricDeltaIcon-Up"]) { color: var(--accent-green) !important; }
    [data-testid="stMetricDelta"] > svg[data-testid="stMetricDeltaIcon-Up"] { color: var(--accent-green) !important; }
    [data-testid="stMetricDelta"] > div:has(> svg[data-testid="stMetricDeltaIcon-Down"]) { color: var(--accent-red) !important; }
    [data-testid="stMetricDelta"] > svg[data-testid="stMetricDeltaIcon-Down"] { color: var(--accent-red) !important; }

    /* Abas (Tabs) Estilo Linear/Vercel */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: transparent;
        border-bottom: 1px solid var(--border-subtle);
        padding-bottom: 0px;
    }
    .stTabs [data-baseweb="tab"] {
        color: var(--text-secondary);
        font-family: 'Inter', sans-serif;
        font-size: 0.875rem;
        font-weight: 500;
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 0;
        padding-right: 0;
        border: none;
        background-color: transparent;
        transition: color 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover { color: var(--text-primary); }
    .stTabs [aria-selected="true"] {
        color: var(--text-primary) !important;
        border-bottom: 2px solid var(--accent-blue) !important;
    }

    /* Inputs e Controles */
    .stSelectbox div[data-baseweb="select"], .stTextInput input, .stNumberInput input {
        background-color: var(--bg-panel) !important;
        border: 1px solid var(--border-subtle) !important;
        color: var(--text-primary) !important;
        border-radius: 6px;
        font-size: 0.875rem;
        transition: border-color 0.2s ease;
    }
    .stSelectbox div[data-baseweb="select"]:hover, .stTextInput input:hover, .stNumberInput input:hover {
        border-color: var(--border-focus) !important;
    }
    
    .stButton > button {
        background-color: var(--bg-panel);
        color: var(--text-primary);
        border: 1px solid var(--border-subtle);
        border-radius: 6px;
        font-family: 'Inter', sans-serif;
        font-size: 0.875rem;
        font-weight: 500;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: var(--border-subtle);
        border-color: var(--border-focus);
        color: white;
    }

    /* Barra Superior Institucional */
    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
        border-bottom: 1px solid var(--border-subtle);
    }
    .top-bar-title {
        font-size: 1.125rem;
        font-weight: 600;
        letter-spacing: -0.02em;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .status-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: var(--accent-green);
        background: rgba(16, 185, 129, 0.1);
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        border: 1px solid rgba(16, 185, 129, 0.2);
    }
    
    /* Box de Notícias */
    .news-box {
        background-color: var(--bg-panel);
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        transition: all 0.2s;
    }
    .news-box:hover { border-color: var(--border-focus); }
    .news-title { font-size: 0.9rem; font-weight: 600; color: var(--accent-blue); margin-bottom: 0.25rem; }
    .news-meta { font-size: 0.7rem; color: var(--text-secondary); text-transform: uppercase; font-family: 'JetBrains Mono', monospace; }
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# ==============================================================================
# 2. CONTEXTO MACROECONÔMICO
# ==============================================================================
GLOBAL_MACRO_CONTEXT = """
[CENÁRIO MACROECONÔMICO E GEOPOLÍTICO GLOBAL]
- BRASIL (COPOM): Taxa Selic mantida em 14.50% ao ano, configurando um dos maiores juros reais do planeta. Este cenário restritivo asfixia o varejo, alavanca a dívida das empresas de construção e atrai massivamente o capital para a Renda Fixa (CDI). A curva DI Futuro precifica risco fiscal elevado.
- ESTADOS UNIDOS (FED): Federal Reserve mantém Fed Funds Rate no patamar de 3.50% - 3.75%. O Core CPI cravado em 2.8% demonstra uma inflação rígida. O Dólar (DXY) fortalecido drena o capital de risco dos países emergentes.
- CHINA (PBoC): Crise imobiliária sistêmica sem resolução. Os estímulos monetários do Banco do Povo da China têm sido insuficientes para reativar o consumo interno e a construção civil, o que derruba a demanda global por aço e minério de ferro.
- GEOPOLÍTICA: O bloqueio do Estreito de Ormuz pelo Irã e os ataques no Mar Vermelho forçaram frotas globais a contornarem o Cabo da Boa Esperança, mantendo o petróleo Brent negociado com prêmio de guerra.
"""

# ==============================================================================
# 3. DICIONÁRIO INSTITUCIONAL DE ATIVOS
# ==============================================================================
CATALOGO_INSTITUCIONAL = {
    "Índice Bovespa (BVSP)": "^BVSP", "S&P 500 EUA (SPY)": "SPY", "Nasdaq 100 EUA (QQQ)": "QQQ", 
    "Ibovespa ETF (BOVA11)": "BOVA11.SA", "Ouro Físico (GLD)": "GLD", "Petróleo Brent ETF (BNO)": "BNO", 
    "IFIX - Fundos Imobiliários": "^IFIX",
    "Petrobras PN (PETR4)": "PETR4.SA", "Petrobras ON (PETR3)": "PETR3.SA", "Vale S.A (VALE3)": "VALE3.SA", 
    "Gerdau Metalúrgica (GGBR4)": "GGBR4.SA", "CSN Siderurgia (CSNA3)": "CSNA3.SA", "Usiminas (USIM5)": "USIM5.SA",
    "Prio Petróleo (PRIO3)": "PRIO3.SA", "Suzano Celulose (SUZB3)": "SUZB3.SA", "Klabin (KLBN11)": "KLBN11.SA",
    "Itaú Unibanco (ITUB4)": "ITUB4.SA", "Banco do Brasil (BBAS3)": "BBAS3.SA", "Bradesco PN (BBDC4)": "BBDC4.SA", 
    "Eletrobras ON (ELET3)": "ELET3.SA", "Taesa (TAEE11)": "TAEE11.SA", "Equatorial (EQTL3)": "EQTL3.SA", 
    "Sabesp (SBSP3)": "SBSP3.SA", "Weg Equipamentos (WEGE3)": "WEGE3.SA", "Localiza (RENT3)": "RENT3.SA", 
    "Magazine Luiza (MGLU3)": "MGLU3.SA", "Nvidia Corp (NVDA)": "NVDA", "Apple Inc (AAPL)": "AAPL", 
    "Microsoft (MSFT)": "MSFT", "Bitcoin (BTC-USD)": "BTC-USD", "Dólar / Real (BRL=X)": "BRL=X",
    "Pesquisa Manual de Ticker": "OUTRO"
}

# ==============================================================================
# 4. DATA PIPELINE (INGESTÃO DE PREÇOS, FUNDAMENTOS E NOTÍCIAS)
# ==============================================================================
@st.cache_data(ttl=600)
def fetch_market_data(ticker: str, period: str = "2y") -> Optional[pd.DataFrame]:
    try:
        data = yf.Ticker(ticker).history(period=period)
        if data.empty or len(data) < 50: return None
        if data.index.tz is not None: data.index = data.index.tz_localize(None)
        return data
    except: return None

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
            'ROE': info.get('returnOnEquity', 'N/A'),
            'Debt to Equity': info.get('debtToEquity', 'N/A'),
            'Current Ratio': info.get('currentRatio', 'N/A'),
        }
    except: return {}

@st.cache_data(ttl=1800)
def fetch_recent_news(ticker: str) -> List[Dict[str, str]]:
    """Extrai o fluxo de notícias do ativo via Yahoo Finance API."""
    try:
        tk = yf.Ticker(ticker)
        news_data = tk.news[:5] # Top 5 manchetes recentes
        return [{"title": n.get('title', ''), "publisher": n.get('publisher', ''), "link": n.get('link', '')} for n in news_data]
    except: return []

def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv().encode('utf-8')

# ==============================================================================
# 5. QUANTITATIVE ENGINE (ALGORITMOS TÉCNICOS E RISCO INSTITUCIONAL)
# ==============================================================================
def calculate_advanced_indicators(df: pd.DataFrame, ma_window: int = 20) -> Tuple[pd.DataFrame, Dict[str, float], float, float]:
    df_calc = df.copy()
    close, high, low, volume = df_calc['Close'], df_calc['High'], df_calc['Low'], df_calc['Volume']
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
    max_p, min_p = recent_df['High'].max(), recent_df['Low'].min()
    diff = max_p - min_p
    fibo_levels = {
        '100.0% (Topo)': max_p, '61.8% (Ouro Sup)': max_p - 0.382 * diff,
        '50.0% (Equilíbrio)': max_p - 0.5 * diff, '38.2% (Ouro Inf)': max_p - 0.618 * diff,
        '0.0% (Fundo)': min_p
    }

    daily_returns = close.pct_change()
    ann_return = daily_returns.mean() * 252 * 100 
    ann_vol = daily_returns.std() * np.sqrt(252) * 100
    sharpe_ratio = (ann_return - 14.50) / ann_vol if ann_vol > 0 else 0

    return df_calc, fibo_levels, ann_return, sharpe_ratio

def calculate_risk_metrics(df: pd.DataFrame, confidence_level: float = 0.95) -> Tuple[float, float]:
    """Motor Analítico de Risco: Value at Risk (VaR) e Expected Shortfall (CVaR) Histórico."""
    returns = df['Close_Price'].pct_change().dropna()
    if len(returns) == 0: return 0.0, 0.0
    var = np.percentile(returns, (1 - confidence_level) * 100)
    cvar = returns[returns <= var].mean()
    return var * 100, cvar * 100

def calculate_volume_profile(df: pd.DataFrame, bins: int = 15) -> pd.DataFrame:
    """Motor de Liquidez Institucional: Volume by Price (VBP)."""
    recent_df = df.tail(252).copy() # Perfil de Volume do último ano
    min_p, max_p = recent_df['Low'].min(), recent_df['High'].max()
    price_bins = np.linspace(min_p, max_p, bins)
    recent_df['Typical_Price'] = (recent_df['High'] + recent_df['Low'] + recent_df['Close_Price']) / 3
    recent_df['Bin'] = pd.cut(recent_df['Typical_Price'], bins=price_bins)
    vbp = recent_df.groupby('Bin', observed=False)['Volume'].sum().reset_index()
    vbp['Bin_Center'] = vbp['Bin'].apply(lambda x: x.mid)
    return vbp

# ==============================================================================
# 6. DATA VISUALIZATION (DESIGN SYSTEM GRÁFICO NÍVEL PALANTIR)
# ==============================================================================
def plot_master_chart(df: pd.DataFrame, ticker: str, fibo: Dict[str, float]) -> go.Figure:
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_width=[0.2, 0.2, 0.6])
    
    up_color, down_color = '#10b981', '#f43f5e'
    sma_color, band_color = '#3b82f6', 'rgba(161, 161, 170, 0.2)'
    
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close_Price'], 
        name='Preço', increasing_line_color=up_color, decreasing_line_color=down_color,
        increasing_fillcolor=up_color, decreasing_fillcolor=down_color, line_width=1
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], mode='lines', line=dict(color=sma_color, width=1.2), name='SMA'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], mode='lines', line=dict(color=band_color, width=1), name='BB Sup', showlegend=False), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], mode='lines', line=dict(color=band_color, width=1), name='BB Inf', fill='tonexty', fillcolor='rgba(255,255,255,0.02)', showlegend=False), row=1, col=1)
    
    for level_name, price in fibo.items():
        fig.add_hline(y=price, line_dash="solid", line_color='rgba(255,255,255,0.1)', line_width=1, annotation_text=level_name, annotation_position="top left", annotation_font_color='rgba(255,255,255,0.4)', annotation_font_size=10, row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df['MFI'], mode='lines', line=dict(color='#8b5cf6', width=1.2), name='MFI'), row=2, col=1)
    fig.add_hline(y=80, line_dash="dash", line_color="rgba(244, 63, 94, 0.5)", line_width=1, row=2, col=1)
    fig.add_hline(y=20, line_dash="dash", line_color="rgba(16, 185, 129, 0.5)", line_width=1, row=2, col=1)

    colors_macd = [up_color if val >= 0 else down_color for val in df['MACD_Hist']]
    fig.add_trace(go.Bar(x=df.index, y=df['MACD_Hist'], marker_color=colors_macd, name='Hist', opacity=0.8), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], mode='lines', line=dict(color='#3b82f6', width=1.2), name='MACD'), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Signal_Line'], mode='lines', line=dict(color='#eab308', width=1.2), name='Sinal'), row=3, col=1)
    
    fig.update_layout(
        xaxis_rangeslider_visible=False, height=750, margin=dict(l=10, r=10, t=10, b=10), 
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#a1a1aa", size=11), showlegend=False, hovermode="x unified"
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#27272a', zeroline=False)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#27272a', zeroline=False)
    return fig

def plot_volume_profile(vbp_df: pd.DataFrame) -> go.Figure:
    """Renderiza o Perfil de Volume Institucional (Horizontal)."""
    fig = go.Figure(go.Bar(
        x=vbp_df['Volume'], y=vbp_df['Bin_Center'], orientation='h',
        marker_color='rgba(59, 130, 246, 0.4)', marker_line_color='#3b82f6', marker_line_width=1
    ))
    fig.update_layout(
        height=350, margin=dict(l=0, r=0, t=20, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#a1a1aa", size=11),
        xaxis_title="Volume Acumulado", yaxis_title="Nível de Preço (R$)"
    )
    fig.update_xaxes(showgrid=True, gridcolor='#27272a')
    fig.update_yaxes(showgrid=True, gridcolor='#27272a')
    return fig

# ==============================================================================
# 7. MODELOS ESTATÍSTICOS ADICIONAIS
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
    drawdown = (bt_df['Equity_Curve'] - bt_df['Equity_Curve'].cummax()) / bt_df['Equity_Curve'].cummax()
    
    win_days = len(bt_df[(bt_df['Signal'] == 1) & (bt_df['Daily_Return'] > 0)])
    lose_days = len(bt_df[(bt_df['Signal'] == 1) & (bt_df['Daily_Return'] <= 0)])
    
    return {
        'total_return_pct': total_strat_return, 'buy_hold_pct': total_bh_return,
        'max_drawdown_pct': drawdown.min() * 100,
        'win_rate_pct': (win_days / (win_days + lose_days) * 100) if (win_days + lose_days) > 0 else 0,
        'curve_df': bt_df[['Equity_Curve', 'Buy_Hold_Curve']].dropna()
    }

def calculate_seasonality(df: pd.DataFrame) -> pd.DataFrame:
    monthly = df['Close_Price'].resample('ME').last()
    seasonality = (monthly.pct_change() * 100).groupby(monthly.index.month).mean().to_frame('Avg_Return_Pct')
    seasonality.index = seasonality.index.map({1:'Jan',2:'Fev',3:'Mar',4:'Abr',5:'Mai',6:'Jun',7:'Jul',8:'Ago',9:'Set',10:'Out',11:'Nov',12:'Dez'})
    return seasonality

def plot_seasonality(seasonality_df: pd.DataFrame) -> go.Figure:
    colors = ['#10b981' if val >= 0 else '#f43f5e' for val in seasonality_df['Avg_Return_Pct']]
    fig = go.Figure(data=[go.Bar(
        x=seasonality_df.index, y=seasonality_df['Avg_Return_Pct'],
        marker_color=colors, marker_line_width=0, opacity=0.85
    )])
    fig.update_layout(
        height=300, margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#a1a1aa", size=11)
    )
    fig.update_yaxes(showgrid=True, gridcolor='#27272a', zerolinecolor='#3f3f46')
    return fig

def run_monte_carlo_simulation(df: pd.DataFrame, days_ahead: int = 30, simulations: int = 200) -> Tuple[np.ndarray, go.Figure, float]:
    log_returns = np.log(1 + df['Close_Price'].pct_change()).dropna()
    daily_returns = np.exp((log_returns.mean() - 0.5 * log_returns.var()) + log_returns.std() * np.random.normal(0, 1, (days_ahead, simulations)))
    price_paths = np.zeros_like(daily_returns)
    price_paths[0] = df['Close_Price'].iloc[-1]
    
    for t in range(1, days_ahead): price_paths[t] = price_paths[t-1] * daily_returns[t]
        
    fig = go.Figure()
    for i in range(simulations):
        fig.add_trace(go.Scatter(y=price_paths[:, i], mode='lines', line=dict(color='rgba(59, 130, 246, 0.03)', width=1), showlegend=False))
    fig.add_trace(go.Scatter(y=price_paths.mean(axis=1), mode='lines', line=dict(color='#fafafa', width=2), name='Média'))
    
    fig.update_layout(
        height=300, margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter", color="#a1a1aa", size=11)
    )
    fig.update_xaxes(showgrid=True, gridcolor='#27272a')
    fig.update_yaxes(showgrid=True, gridcolor='#27272a')
    return price_paths, fig, np.mean(price_paths[-1])

def black_scholes_greeks(S: float, K: float, T: float, r: float, sigma: float) -> Dict[str, float]:
    if T <= 0 or sigma <= 0: return {'call_price': 0, 'put_price': 0, 'delta_call': 0, 'gamma': 0, 'vega': 0, 'theta_call': 0}
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    cdf = lambda x: (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0
    pdf = lambda x: math.exp(-0.5 * x**2) / math.sqrt(2 * math.pi)
    
    return {
        'call_price': S * cdf(d1) - K * math.exp(-r * T) * cdf(d2),
        'put_price': K * math.exp(-r * T) * cdf(-d2) - S * cdf(-d1), 
        'delta_call': cdf(d1), 'gamma': pdf(d1) / (S * sigma * math.sqrt(T)),
        'vega': S * pdf(d1) * math.sqrt(T) / 100,
        'theta_call': (-(S * pdf(d1) * sigma) / (2 * math.sqrt(T)) - r * K * math.exp(-r * T) * cdf(d2)) / 365
    }

# ==============================================================================
# 8. ORÁCULO IA (LLAMA 3.1 NPU) - AGORA COM DADOS DE RISCO E SENTIMENTO
# ==============================================================================
def generate_ai_response(prompt: str, context_data: str, api_key: str, persona: str) -> str:
    try:
        client = Groq(api_key=api_key)
        foco = {
            "Análise de Risco & Valuation": "Foco em fundamentos (P/L, ROE) e no Value at Risk (VaR).",
            "Estratégia Macro & Geopolítica": "Cruze o preço do ativo com a taxa Selic (14.50%), inflação e sentimento de notícias.",
            "Quant Trader & Volatilidade": "Foco estrito em backtest, níveis de Fibonacci, Liquidez (Volume Profile) e volatilidade."
        }.get(persona, "Análise estrutural baseada nos dados do terminal.")
        
        sys_prompt = f"""Você é o Cérebro Neural Integrado do Terminal Quantamental.
DIRETRIZ DA PERSONA: {foco}
REGRAS: Seja denso, cínico, direto, pragmático. Baseie-se EXCLUSIVAMENTE nos dados estatísticos (VaR, CVaR, Fluxo MFI, Notícias) fornecidos. Formate com Bullet Points limpos. NUNCA use LaTeX. Responda num tom institucional premium de Wall Street/Hedge Fund."""
        
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": f"[DATA LAKE]\n{GLOBAL_MACRO_CONTEXT}\n\n[MATRIZ QUANTITATIVA, RISCO EXTREMO E SENTIMENTO]\n{context_data}\n\n[QUERY DO GESTOR]\n{prompt}"}
            ],
            model="llama-3.1-8b-instant", temperature=0.3
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"ALERTA DO SISTEMA: Falha na conexão de rede neural. [Erro: {e}]"

# ==============================================================================
# 9. FRONTEND & UX (ESTRUTURA PRINCIPAL)
# ==============================================================================
def main():
    # Barra Superior (Header Institucional Minimalista)
    st.markdown("""
        <div class="top-bar">
            <div class="top-bar-title">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>
                Terminal Quantamental | Institutional Alpha
            </div>
            <div class="status-indicator">
                <span style="height:6px;width:6px;background-color:#10b981;border-radius:50%;display:inline-block;"></span>
                INFRAESTRUTURA ONLINE
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Grid Layout: Sidebar Integrada para Gestão de Espaço
    col_nav, col_main = st.columns([1, 4], gap="large")
    
    with col_nav:
        st.markdown("<p style='font-size:0.75rem; color:var(--text-secondary); font-weight:600; letter-spacing:0.05em;'>PARÂMETROS DE EXECUÇÃO</p>", unsafe_allow_html=True)
        selecao_ativo = st.selectbox("Ativo Institucional", list(CATALOGO_INSTITUCIONAL.keys()), label_visibility="collapsed")
        ticker = st.text_input("Ticker Customizado", value="PETR4.SA") if selecao_ativo == "Pesquisa Manual de Ticker" else CATALOGO_INSTITUCIONAL[selecao_ativo]
        period = st.selectbox("Horizonte de Análise", ["6mo", "1y", "2y", "5y", "max"], index=2)
        ma_window = st.number_input("Suavização (SMA Base)", min_value=5, max_value=200, value=20)
        
        st.markdown("<br><p style='font-size:0.75rem; color:var(--text-secondary); font-weight:600; letter-spacing:0.05em;'>EXPORTAÇÃO QUANTITATIVA</p>", unsafe_allow_html=True)
        export_placeholder = st.empty()
        
        api_key = "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"

    # Processamento Massivo de Dados
    df_raw = fetch_market_data(ticker, period)
    fundament_data = fetch_fundamental_data(ticker)
    recent_news = fetch_recent_news(ticker)
    
    if df_raw is not None:
        df_processed, fibo_levels, ann_return, sharpe_ratio = calculate_advanced_indicators(df_raw, ma_window)
        
        # Novos Motores (V14)
        var_95, cvar_95 = calculate_risk_metrics(df_processed)
        vbp_df = calculate_volume_profile(df_processed)
        
        mc_paths, mc_fig, mc_expected_price = run_monte_carlo_simulation(df_processed)
        bt_results = run_vectorized_backtest(df_processed)
        seasonality_df = calculate_seasonality(df_processed)
        
        with export_placeholder:
            st.download_button("↓ Matriz de Dados (CSV)", convert_df_to_csv(df_processed), f"{ticker}_data.csv", "text/csv", use_container_width=True)

        ultima = df_processed.iloc[-1]
        c_price, c_atr, c_mfi = ultima['Close_Price'], ultima['ATR'], ultima['MFI']
        
        with col_main:
            # Painel Superior de Alta Densidade Numérica
            m1, m2, m3, m4 = st.columns(4)
            delta_pct = ((c_price / df_raw['Close'].iloc[-2]) - 1) * 100 if len(df_raw) > 1 else 0
            m1.metric("Último Preço (Spot)", f"R$ {c_price:.2f}", f"{delta_pct:.2f}%")
            m2.metric("Volatilidade (ATR 14)", f"R$ {c_atr:.2f}")
            m3.metric("Risco Absoluto (VaR 95%)", f"{var_95:.2f}%", "Estimativa Diária", delta_color="off")
            m4.metric("Alpha vs Risk-Free", f"{ann_return:.1f}%", f"Sharpe: {sharpe_ratio:.2f}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Navegação de Abas (Tabs) Clean
            tab_chart, tab_risk, tab_models, tab_backtest, tab_fund, tab_ai = st.tabs([
                "Visão Técnica", "Risco & Opções", "Estatística Quant.", "Backtest Engine", "Valuation & Sentimento", "Inteligência Artificial"
            ])

            with tab_chart:
                tc1, tc2 = st.columns([3, 1], gap="large")
                with tc1:
                    fig_master = plot_master_chart(df_processed, ticker, fibo_levels)
                    st.plotly_chart(fig_master, use_container_width=True, config={'displayModeBar': False})
                with tc2:
                    st.markdown("<p style='font-size:0.85rem; font-weight:600; color:var(--text-secondary); text-transform:uppercase;'>Volume Profile (Liquidez)</p>", unsafe_allow_html=True)
                    fig_vbp = plot_volume_profile(vbp_df)
                    st.plotly_chart(fig_vbp, use_container_width=True, config={'displayModeBar': False})

            with tab_risk:
                r_col1, r_col2 = st.columns(2, gap="large")
                with r_col1:
                    st.markdown("#### Dimensionamento e Risco Cauda (CVaR)")
                    st.info(f"O **Expected Shortfall (CVaR 95%)** indica que, nos piores 5% dos dias de mercado, a queda histórica média deste ativo foi de **{cvar_95:.2f}%**.")
                    
                    capital = st.number_input("Capital Operacional (R$)", value=250000.0, step=10000.0)
                    risk_pct = st.number_input("Tolerância de Risco por Trade (%)", value=1.0, step=0.1)
                    entry_price = st.number_input("Alvo de Entrada (R$)", value=float(c_price), step=0.01)
                    stop_loss = st.number_input("Nível Hard-Stop (R$)", value=float(c_price - c_atr * 1.5), step=0.01)
                    
                    if stop_loss < entry_price:
                        shares = int((capital * (risk_pct/100)) // (entry_price - stop_loss))
                        st.success(f"Protocolo Aprovado: **{shares} Lotes** autorizados. (Alocação Bruta: R$ {(shares*entry_price):,.2f})")
                    else:
                        st.error("Stop Loss deve ser inferior ao Alvo de Entrada.")
                        
                with r_col2:
                    st.markdown("#### Motor Black-Scholes (Gregas)")
                    bs_strike = st.number_input("Strike (Exercício)", value=float(c_price * 1.05))
                    bs_days = st.number_input("Dias para Vencimento", value=21)
                    bs_vol = st.number_input("Vol. Implícita (%)", value=float((c_atr/c_price)*math.sqrt(252)*100))
                    
                    greeks = black_scholes_greeks(c_price, bs_strike, bs_days/252.0, 0.145, bs_vol/100.0)
                    g_c1, g_c2, g_c3 = st.columns(3)
                    g_c1.metric("Prêmio Call", f"R${greeks['call_price']:.3f}")
                    g_c2.metric("Prêmio Put", f"R${greeks['put_price']:.3f}")
                    g_c3.metric("Delta (Prob.)", f"{greeks['delta_call']*100:.1f}%")
                    st.caption(f"Gamma: {greeks['gamma']:.4f} | Vega: {greeks['vega']:.3f} | Theta (Decaimento Diário): R$ {greeks['theta_call']:.3f}")

            with tab_models:
                mod_c1, mod_c2 = st.columns(2, gap="large")
                with mod_c1:
                    st.markdown("#### Simulação Monte Carlo (30 Dias)")
                    st.plotly_chart(mc_fig, use_container_width=True, config={'displayModeBar': False})
                    st.caption(f"Preço de Convergência Estatística: R$ {mc_expected_price:.2f}")
                with mod_c2:
                    st.markdown("#### Mapa de Sazonalidade (Mensal)")
                    st.plotly_chart(plot_seasonality(seasonality_df), use_container_width=True, config={'displayModeBar': False})

            with tab_backtest:
                st.markdown("#### Motor Vetorizado: Cruzamento de Médias Móveis Exponenciais (9x21)")
                b_sub1, b_sub2, b_sub3, b_sub4 = st.columns(4)
                b_sub1.metric("Retorno Algoritmo", f"{bt_results['total_return_pct']:.1f}%")
                b_sub2.metric("Retorno Buy&Hold", f"{bt_results['buy_hold_pct']:.1f}%")
                b_sub3.metric("Max Drawdown", f"{bt_results['max_drawdown_pct']:.1f}%")
                b_sub4.metric("Win Rate", f"{bt_results['win_rate_pct']:.1f}%")
                
                fig_eq = go.Figure()
                fig_eq.add_trace(go.Scatter(x=bt_results['curve_df'].index, y=bt_results['curve_df']['Equity_Curve'], mode='lines', name='Algoritmo (EMA)', line=dict(color='#10b981', width=2)))
                fig_eq.add_trace(go.Scatter(x=bt_results['curve_df'].index, y=bt_results['curve_df']['Buy_Hold_Curve'], mode='lines', name='Buy & Hold', line=dict(color='#52525b', width=2, dash='dot')))
                fig_eq.update_layout(height=350, margin=dict(l=0,r=0,t=20,b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter", color="#a1a1aa", size=11))
                fig_eq.update_xaxes(showgrid=True, gridcolor='#27272a'); fig_eq.update_yaxes(showgrid=True, gridcolor='#27272a')
                st.plotly_chart(fig_eq, use_container_width=True, config={'displayModeBar': False})

            with tab_fund:
                f_c1, f_c2 = st.columns([1, 1], gap="large")
                with f_c1:
                    st.markdown("#### Múltiplos Contábeis")
                    if fundament_data:
                        f_sub1, f_sub2 = st.columns(2)
                        f_sub1.metric("P/L", f"{fundament_data.get('P/E Ratio (P/L)', 'N/A')}")
                        f_sub2.metric("P/VP", f"{fundament_data.get('Price to Book (P/VP)', 'N/A')}")
                        f_sub1.metric("Div Yield", f"{fundament_data.get('Dividend Yield', 0)*100 if isinstance(fundament_data.get('Dividend Yield'), (int,float)) else 'N/A'}%")
                        f_sub2.metric("ROE", f"{fundament_data.get('ROE', 0)*100 if isinstance(fundament_data.get('ROE'), (int,float)) else 'N/A'}%")
                
                with f_c2:
                    st.markdown("#### Termômetro de Mercado (Notícias)")
                    if recent_news:
                        for news in recent_news:
                            st.markdown(f"""
                            <div class="news-box">
                                <div class="news-title"><a href="{news['link']}" target="_blank" style="color:var(--accent-blue); text-decoration:none;">{news['title']}</a></div>
                                <div class="news-meta">Fonte: {news['publisher']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("Nenhuma notícia recente identificada nos feeds primários.")

            with tab_ai:
                st.markdown("#### Cérebro Llama 3.1 Integrado")
                persona = st.radio("Foco Cognitivo da NPU:", ["Análise de Risco & Valuation", "Estratégia Macro & Geopolítica", "Quant Trader & Volatilidade"], horizontal=True, label_visibility="collapsed")
                
                chat_box = st.container(height=350)
                with chat_box:
                    for msg in st.session_state.messages:
                        st.chat_message(msg["role"]).markdown(msg["content"])
                        
                if prompt := st.chat_input("Ex: 'Com um VaR de " + f"{var_95:.2f}%" + " e o fluxo MFI atual, é viável executar uma operação long?'"):
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    st.rerun()
                    
                if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                    with chat_box:
                        with st.spinner("Decodificando Matriz de Risco e Fluxo de Volume..."):
                            # Preparar contexto monumental com os novos dados
                            noticias_txt = " | ".join([n['title'] for n in recent_news]) if recent_news else "Sem fluxo de notícias."
                            context = f"""
                            Preço: R$ {c_price:.2f} | ATR 14: R$ {c_atr:.2f} | MFI: {c_mfi:.1f}
                            Risco Extremo (VaR 95%): {var_95:.2f}% | Expected Shortfall (CVaR): {cvar_95:.2f}%
                            MonteCarlo 30d: R$ {mc_expected_price:.2f} | WinRate Estratégia (EMA): {bt_results['win_rate_pct']:.1f}%
                            Manchetes Recentes: {noticias_txt}
                            """
                            resp = generate_ai_response(st.session_state.messages[-1]["content"], context, api_key, persona)
                            st.session_state.messages.append({"role": "assistant", "content": resp})
                            st.rerun()
    else:
        st.error("Ruptura no pipeline de dados. Verifique a liquidez do ativo ou a conexão.")

if __name__ == "__main__":
    main()