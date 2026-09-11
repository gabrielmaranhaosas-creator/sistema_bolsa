# ==============================================================================
# TERMINAL QUANTAMENTAL v2.0 — ARQUITETURA INSTITUCIONAL
# Separation of Concerns | Fail-Safe | Observable | Secure
# ==============================================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Tuple, Dict, Optional, Any
import math
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

# ── Scipy para VaR paramétrico (graceful fallback) ──────────────────────────
try:
    from scipy import stats as scipy_stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

# ==============================================================================
# 1. DESIGN SYSTEM — CONFIGURAÇÃO E CSS INSTITUCIONAL
# ==============================================================================
st.set_page_config(
    page_title="Terminal Quantamental v2.0",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
    --bg-app:       #09090b;
    --bg-panel:     #18181b;
    --bg-card:      #1c1c1f;
    --border-s:     #27272a;
    --border-f:     #3f3f46;
    --txt-1:        #fafafa;
    --txt-2:        #a1a1aa;
    --txt-3:        #52525b;
    --blue:         #3b82f6;
    --blue-d:       rgba(59,130,246,.12);
    --green:        #10b981;
    --green-d:      rgba(16,185,129,.12);
    --red:          #f43f5e;
    --red-d:        rgba(244,63,94,.12);
    --gold:         #eab308;
    --gold-d:       rgba(234,179,8,.12);
    --purple:       #8b5cf6;
}

.stApp { background-color: var(--bg-app); font-family: 'Inter', -apple-system, sans-serif; color: var(--txt-1); }
header, footer { visibility: hidden; }
h1,h2,h3,h4,h5,h6 { color: var(--txt-1) !important; font-family: 'Inter', sans-serif !important; font-weight: 600 !important; letter-spacing: -0.02em !important; }

section[data-testid="stSidebar"] { background-color: var(--bg-panel) !important; border-right: 1px solid var(--border-s); }

[data-testid="metric-container"] {
    background: var(--bg-card); border: 1px solid var(--border-s); border-radius: 8px;
    padding: 1rem 1.25rem; transition: all 0.18s ease;
}
[data-testid="metric-container"]:hover { border-color: var(--border-f); transform: translateY(-1px); }
[data-testid="stMetricLabel"] { color: var(--txt-2) !important; font-size: .69rem !important; font-weight: 600 !important; text-transform: uppercase; letter-spacing: .06em; }
[data-testid="stMetricValue"] { font-family: 'JetBrains Mono', monospace !important; color: var(--txt-1) !important; font-size: 1.55rem !important; font-weight: 600 !important; }
[data-testid="stMetricDelta"] { font-family: 'JetBrains Mono', monospace !important; font-size: .79rem !important; }
[data-testid="stMetricDelta"] > div:has(> svg[data-testid="stMetricDeltaIcon-Up"])   { color: var(--green) !important; }
[data-testid="stMetricDelta"] > div:has(> svg[data-testid="stMetricDeltaIcon-Down"]) { color: var(--red)   !important; }

.stTabs [data-baseweb="tab-list"] { gap: 0; background: transparent; border-bottom: 1px solid var(--border-s); overflow-x: auto; white-space: nowrap; -webkit-overflow-scrolling: touch; }
.stTabs [data-baseweb="tab"] { color: var(--txt-2); font-family: 'Inter', sans-serif; font-size: .84rem; font-weight: 500; padding: .85rem 1.1rem; border: none; background: transparent; border-bottom: 2px solid transparent; transition: color .18s; }
.stTabs [data-baseweb="tab"]:hover { color: var(--txt-1); }
.stTabs [aria-selected="true"] { color: var(--txt-1) !important; border-bottom: 2px solid var(--blue) !important; }

.stSelectbox div[data-baseweb="select"], .stTextInput input, .stNumberInput input {
    background: var(--bg-panel) !important; border: 1px solid var(--border-s) !important;
    color: var(--txt-1) !important; border-radius: 6px; font-size: .875rem;
}
.stButton > button { background: var(--bg-panel); color: var(--txt-1); border: 1px solid var(--border-s); border-radius: 6px; font-family: 'Inter', sans-serif; font-size: .875rem; font-weight: 500; padding: .5rem 1rem; transition: all .18s; }
.stButton > button:hover { background: var(--border-s); border-color: var(--border-f); }
.stSlider > div { padding: 0; }

/* Badges */
.badge-ok  { display:inline-flex; align-items:center; gap:6px; background:var(--green-d); color:var(--green); border:1px solid rgba(16,185,129,.25); border-radius:9999px; padding:.22rem .7rem; font-family:'JetBrains Mono',monospace; font-size:.72rem; }
.badge-ko  { display:inline-flex; align-items:center; gap:6px; background:var(--red-d);   color:var(--red);   border:1px solid rgba(244,63,94,.25);  border-radius:9999px; padding:.22rem .7rem; font-family:'JetBrains Mono',monospace; font-size:.72rem; }
.badge-inf { display:inline-flex; align-items:center; gap:6px; background:var(--blue-d);  color:var(--blue);  border:1px solid rgba(59,130,246,.25);  border-radius:9999px; padding:.22rem .7rem; font-family:'JetBrains Mono',monospace; font-size:.72rem; }

/* Cartão de regime */
.regime-card { background:var(--bg-card); border:1px solid var(--border-s); border-radius:8px; padding:.85rem 1.1rem; }
.sec-hdr { font-size:.67rem; font-weight:700; color:var(--txt-3); text-transform:uppercase; letter-spacing:.1em; margin-bottom:.6rem; padding-bottom:.4rem; border-bottom:1px solid var(--border-s); }

/* Tabela de Fibonacci */
.fib-card { background:var(--bg-card); border:1px solid var(--border-s); border-radius:6px; padding:.6rem; text-align:center; }

/* Info-boxes */
.ibox { background:var(--bg-card); border:1px solid var(--border-s); border-radius:8px; padding:.85rem 1.1rem; margin:.4rem 0; }
.ibox-blue   { border-left:3px solid var(--blue);   }
.ibox-green  { border-left:3px solid var(--green);  }
.ibox-red    { border-left:3px solid var(--red);    }
.ibox-gold   { border-left:3px solid var(--gold);   }

/* Fundamental row */
.fund-row { display:flex; justify-content:space-between; padding:.45rem 0; border-bottom:1px solid var(--border-s); }
.fund-k   { color:var(--txt-2); font-size:.79rem; }
.fund-v   { color:var(--txt-1); font-family:'JetBrains Mono',monospace; font-size:.79rem; font-weight:600; }

@media (max-width:768px) {
    [data-testid="stMetricValue"] { font-size:1.2rem !important; }
}
</style>
""",
    unsafe_allow_html=True,
)

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# ==============================================================================
# 2. BASE MACROECONÔMICA — CONTEXTO GLOBAL
# ==============================================================================
MACRO = """
[CENÁRIO MACROECONÔMICO GLOBAL — MATRIZ DE RISCO SISTÊMICO]

BRASIL (COPOM):
- Selic: 14.50% a.a. — maior juro real do G20. Tom hawkish até ao menos 2026.
- IPCA Focus: 5.04% (acima da meta de 3%). Risco de desancoragem consolidado.
- DI Futuro Jan/31: 13.36% — precifica risco fiscal severo.
- Consequência: Ações de crescimento destruídas. Capital migra para renda fixa CDI.

EUA (FED):
- Fed Funds: 3.50–3.75%. "Higher for longer" confirmado.
- Core PCE: 2.8% — inflação de serviços sticky.
- DXY forte: pressão sobre emergentes; Treasuries 10Y em 4.5%+ drenam liquidez de equities.

EUROPA (BCE):
- Recessão industrial na Alemanha (-0.3% PIB).
- Dilema: cortar juros (crescimento) vs manter (inflação fragmentada).

CHINA (PBoC):
- Crise imobiliária sistêmica (Evergrande liquidada).
- Estímulos insuficientes. Demanda por minério de ferro deprimida.

GEOPOLÍTICA:
- Estreito de Ormuz: tensão Irã-Israel → prêmio de guerra Brent +25%.
- Mar Vermelho (Houthis): rota Suez bloqueada → fretes +400%.
- Ucrânia: pressão sobre commodities agrícolas.
"""

# ==============================================================================
# 3. CATÁLOGO DE ATIVOS INSTITUCIONAL
# ==============================================================================
CATALOGO: Dict[str, str] = {
    # Índices
    "Ibovespa (^BVSP)":           "^BVSP",
    "S&P 500 (SPY)":              "SPY",
    "Nasdaq 100 (QQQ)":           "QQQ",
    "IFIX — FIIs":                "^IFIX",
    # ETFs B3
    "BOVA11 — Ibovespa ETF":      "BOVA11.SA",
    "IVVB11 — S&P 500 B3":        "IVVB11.SA",
    "SMAL11 — Small Caps":        "SMAL11.SA",
    # Commodities
    "Ouro (GLD)":                 "GLD",
    "Petróleo Brent (BNO)":       "BNO",
    # Petróleo & Energia
    "Petrobras PN (PETR4)":       "PETR4.SA",
    "Petrobras ON (PETR3)":       "PETR3.SA",
    "Prio (PRIO3)":               "PRIO3.SA",
    "Enauta (ENAT3)":             "ENAT3.SA",
    # Mineração & Siderurgia
    "Vale (VALE3)":               "VALE3.SA",
    "Gerdau (GGBR4)":             "GGBR4.SA",
    "CSN (CSNA3)":                "CSNA3.SA",
    "Usiminas (USIM5)":           "USIM5.SA",
    # Papel & Celulose
    "Suzano (SUZB3)":             "SUZB3.SA",
    "Klabin (KLBN11)":            "KLBN11.SA",
    # Agro
    "SLC Agrícola (SLCE3)":       "SLCE3.SA",
    "São Martinho (SMTO3)":       "SMTO3.SA",
    # Proteínas
    "JBS (JBSS3)":                "JBSS3.SA",
    "BRF (BRFS3)":                "BRFS3.SA",
    "Marfrig (MRFG3)":            "MRFG3.SA",
    # Financeiro
    "Itaú (ITUB4)":               "ITUB4.SA",
    "Banco do Brasil (BBAS3)":    "BBAS3.SA",
    "Bradesco (BBDC4)":           "BBDC4.SA",
    "BTG Pactual (BPAC11)":       "BPAC11.SA",
    "B3 (B3SA3)":                 "B3SA3.SA",
    "BB Seguridade (BBSE3)":      "BBSE3.SA",
    # Elétrico
    "Eletrobras (ELET3)":         "ELET3.SA",
    "Taesa (TAEE11)":             "TAEE11.SA",
    "Equatorial (EQTL3)":         "EQTL3.SA",
    "Engie (EGIE3)":              "EGIE3.SA",
    # Saneamento
    "Sabesp (SBSP3)":             "SBSP3.SA",
    # Industrial & Varejo
    "WEG (WEGE3)":                "WEGE3.SA",
    "Localiza (RENT3)":           "RENT3.SA",
    "Magazine Luiza (MGLU3)":     "MGLU3.SA",
    "Assaí (ASAI3)":              "ASAI3.SA",
    # Saúde
    "Rede D'Or (RDOR3)":          "RDOR3.SA",
    "Hapvida (HAPV3)":            "HAPV3.SA",
    # Logística
    "Rumo (RAIL3)":               "RAIL3.SA",
    # Construção
    "Cyrela (CYRE3)":             "CYRE3.SA",
    "MRV (MRVE3)":                "MRVE3.SA",
    # FIIs
    "Maxi Renda (MXRF11)":        "MXRF11.SA",
    "HGLG11 — Logística":         "HGLG11.SA",
    "KNRI11 — Kinea":             "KNRI11.SA",
    # EUA Tech
    "Nvidia (NVDA)":              "NVDA",
    "Apple (AAPL)":               "AAPL",
    "Microsoft (MSFT)":           "MSFT",
    "Alphabet (GOOGL)":           "GOOGL",
    "Amazon (AMZN)":              "AMZN",
    "Tesla (TSLA)":               "TSLA",
    "Palantir (PLTR)":            "PLTR",
    "Mercado Livre (MELI)":       "MELI",
    # Cripto
    "Bitcoin (BTC-USD)":          "BTC-USD",
    "Ethereum (ETH-USD)":         "ETH-USD",
    "Solana (SOL-USD)":           "SOL-USD",
    # Câmbio
    "USD/BRL":                    "BRL=X",
    "EUR/BRL":                    "EURBRL=X",
    # Manual
    "🔍 Ticker Manual":           "OUTRO",
}

# ==============================================================================
# 4. DATA PIPELINE — INGESTÃO E EXPORTAÇÃO
# ==============================================================================
@st.cache_data(ttl=300)
def fetch_market_data(ticker: str, period: str = "2y") -> Optional[pd.DataFrame]:
    try:
        data = yf.Ticker(ticker).history(period=period, auto_adjust=True)
        if data.empty or len(data) < 60:
            return None
        if data.index.tz is not None:
            data.index = data.index.tz_localize(None)
        return data.dropna(subset=["Close", "Open", "High", "Low"])
    except Exception:
        return None


@st.cache_data(ttl=3600)
def fetch_benchmark(period: str = "2y") -> Optional[pd.Series]:
    """IBOV como benchmark para cálculo de Beta."""
    try:
        df = yf.Ticker("^BVSP").history(period=period, auto_adjust=True)
        if df.empty:
            return None
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)
        return df["Close"]
    except Exception:
        return None


@st.cache_data(ttl=3600)
def fetch_fundamentals(ticker: str) -> Dict[str, Any]:
    try:
        info = yf.Ticker(ticker).info
        return {
            "Market Cap":              info.get("marketCap", "N/A"),
            "P/L Trailing":            info.get("trailingPE", "N/A"),
            "P/L Forward":             info.get("forwardPE", "N/A"),
            "P/VP":                    info.get("priceToBook", "N/A"),
            "Dividend Yield":          info.get("dividendYield", "N/A"),
            "Margem EBITDA":           info.get("ebitdaMargins", "N/A"),
            "Margem Líquida":          info.get("profitMargins", "N/A"),
            "ROE":                     info.get("returnOnEquity", "N/A"),
            "ROA":                     info.get("returnOnAssets", "N/A"),
            "Dívida / Patrimônio":     info.get("debtToEquity", "N/A"),
            "Liquidez Corrente":       info.get("currentRatio", "N/A"),
            "Receita TTM":             info.get("totalRevenue", "N/A"),
            "Beta (Yahoo 52s)":        info.get("beta", "N/A"),
            "Setor":                   info.get("sector", "N/A"),
            "País":                    info.get("country", "N/A"),
        }
    except Exception:
        return {}


def to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv().encode("utf-8")


# ==============================================================================
# 5. QUANTITATIVE ENGINE — INDICADORES TÉCNICOS
# ==============================================================================
def calculate_indicators(
    df: pd.DataFrame, ma_window: int = 20
) -> Tuple[pd.DataFrame, Dict[str, float], float, float, float, float]:
    """
    Pipeline completo de indicadores.
    Retorna: df_calc, fibo, ann_return, sharpe, sortino, calmar
    """
    d = df.copy()
    close, high, low, vol = d["Close"], d["High"], d["Low"], d["Volume"]
    d["Close_Price"] = close

    # ── Médias Móveis ────────────────────────────────────────────────────────
    d["SMA_20"]  = close.rolling(ma_window).mean()
    d["EMA_9"]   = close.ewm(span=9,   adjust=False).mean()
    d["EMA_21"]  = close.ewm(span=21,  adjust=False).mean()
    d["EMA_50"]  = close.ewm(span=50,  adjust=False).mean()
    d["EMA_200"] = close.ewm(span=200, adjust=False).mean()

    # ── Bollinger Bands ──────────────────────────────────────────────────────
    std = close.rolling(ma_window).std()
    d["BB_Upper"] = d["SMA_20"] + std * 2
    d["BB_Lower"] = d["SMA_20"] - std * 2
    d["BB_Width"] = (d["BB_Upper"] - d["BB_Lower"]) / d["SMA_20"]
    d["BB_Pct"]   = (close - d["BB_Lower"]) / (d["BB_Upper"] - d["BB_Lower"] + 1e-10)

    # ── RSI (14) ─────────────────────────────────────────────────────────────
    delta = close.diff()
    gain  = delta.where(delta > 0, 0).rolling(14).mean()
    loss  = (-delta.where(delta < 0, 0)).rolling(14).mean()
    d["RSI"] = 100 - (100 / (1 + gain / loss.replace(0, np.nan)))

    # ── MACD ─────────────────────────────────────────────────────────────────
    d["MACD"]        = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
    d["Signal_Line"] = d["MACD"].ewm(span=9, adjust=False).mean()
    d["MACD_Hist"]   = d["MACD"] - d["Signal_Line"]

    # ── ATR (14) ─────────────────────────────────────────────────────────────
    tr = pd.concat(
        [high - low, (high - close.shift(1)).abs(), (low - close.shift(1)).abs()],
        axis=1,
    ).max(axis=1)
    d["ATR"] = tr.rolling(14).mean()

    # ── Stochastic ───────────────────────────────────────────────────────────
    ll = low.rolling(14).min()
    hh = high.rolling(14).max()
    d["Stoch_K"] = 100 * (close - ll) / (hh - ll + 1e-10)
    d["Stoch_D"] = d["Stoch_K"].rolling(3).mean()

    # ── OBV ──────────────────────────────────────────────────────────────────
    obv_vals = np.where(close > close.shift(1), vol, np.where(close < close.shift(1), -vol, 0))
    d["OBV"] = pd.Series(obv_vals, index=d.index).cumsum()

    # ── MFI (14) ─────────────────────────────────────────────────────────────
    tp = (high + low + close) / 3
    rmf = tp * vol
    pos = pd.Series(np.where(tp > tp.shift(1), rmf, 0), index=d.index).rolling(14).sum()
    neg = pd.Series(np.where(tp < tp.shift(1), rmf, 0), index=d.index).rolling(14).sum()
    d["MFI"] = 100 - (100 / (1 + pos / neg.replace(0, np.nan)))

    # ── Volatilidade Realizada (21d) ─────────────────────────────────────────
    d["Vol_21d"] = close.pct_change().rolling(21).std() * np.sqrt(252) * 100

    # ── Fibonacci (252 sessões) ───────────────────────────────────────────────
    rec   = d.tail(252)
    mx, mn = rec["High"].max(), rec["Low"].min()
    dif   = mx - mn
    fibo  = {
        "100.0% (Topo)":         mx,
        "78.6%":                 mx - 0.214 * dif,
        "61.8% (Ouro Sup)":      mx - 0.382 * dif,
        "50.0% (Equilíbrio)":    mx - 0.500 * dif,
        "38.2% (Ouro Inf)":      mx - 0.618 * dif,
        "23.6%":                 mx - 0.764 * dif,
        "0.0% (Fundo)":          mn,
    }

    # ── Métricas de Risco / Retorno ──────────────────────────────────────────
    daily_ret  = close.pct_change().dropna()
    ann_ret    = daily_ret.mean() * 252 * 100
    ann_vol    = daily_ret.std() * np.sqrt(252) * 100
    rf         = 14.50  # Selic

    sharpe  = (ann_ret - rf) / ann_vol if ann_vol > 0 else 0.0

    down_std  = daily_ret[daily_ret < 0].std() * np.sqrt(252) * 100
    sortino   = (ann_ret - rf) / down_std if down_std > 0 else 0.0

    cum = (1 + daily_ret).cumprod()
    max_dd = ((cum - cum.cummax()) / cum.cummax()).min() * 100
    calmar  = abs(ann_ret / max_dd) if max_dd < 0 else 0.0

    return d, fibo, ann_ret, sharpe, sortino, calmar


# ==============================================================================
# 6. REGIME DETECTION — CLASSIFICAÇÃO DE MERCADO
# ==============================================================================
def detect_regime(df: pd.DataFrame) -> Dict[str, Any]:
    close = df["Close_Price"]
    ret60 = close.pct_change().rolling(60).sum() * 100
    vol20 = close.pct_change().rolling(20).std() * np.sqrt(252) * 100
    r, v  = ret60.iloc[-1], vol20.iloc[-1]
    v_med = vol20.median()

    if r > 10 and v < v_med * 1.3:
        regime, color, desc = "BULL TREND",       "#10b981", "Tendência de alta com volatilidade controlada."
    elif r < -10 and v > v_med * 1.2:
        regime, color, desc = "BEAR / CRISE",     "#f43f5e", "Pressão vendedora dominante. Risco de capitulação."
    elif abs(r) < 5 and v < v_med:
        regime, color, desc = "CONSOLIDAÇÃO",     "#eab308", "Compressão de volatilidade. Aguardar rompimento."
    elif v > v_med * 1.8:
        regime, color, desc = "ALTA VOLATILIDADE","#8b5cf6", "Evento extraordinário. Reduzir sizing imediatamente."
    else:
        regime, color, desc = "INDEFINIDO",       "#a1a1aa", "Sem regime dominante identificável."

    ema50, ema200 = df["EMA_50"].iloc[-1], df["EMA_200"].iloc[-1]
    cross  = "GOLDEN CROSS ▲" if ema50 > ema200 else "DEATH CROSS ▼"
    c_col  = "#10b981"        if ema50 > ema200 else "#f43f5e"

    return {"regime": regime, "color": color, "desc": desc,
            "ret60": r, "vol20": v, "cross": cross, "cross_col": c_col}


# ==============================================================================
# 7. ROLLING BETA vs BENCHMARK
# ==============================================================================
def rolling_beta(df: pd.DataFrame, bench: pd.Series, window: int = 60) -> pd.Series:
    a_ret = df["Close_Price"].pct_change()
    b_ret = bench.pct_change()
    aligned = pd.DataFrame({"a": a_ret, "b": b_ret}).dropna()
    cov = aligned["a"].rolling(window).cov(aligned["b"])
    var = aligned["b"].rolling(window).var()
    return (cov / var).dropna()


# ==============================================================================
# 8. RISK ENGINE — VaR / CVaR / KELLY
# ==============================================================================
def _norm_ppf(p: float) -> float:
    """Inverse normal CDF via scipy or numerical approximation."""
    if SCIPY_AVAILABLE:
        return float(scipy_stats.norm.ppf(p))
    # Approximation (Beasley-Springer-Moro)
    a = [2.50662823884, -18.61500062529, 41.39119773534, -25.44106049637]
    b = [-8.47351093090, 23.08336743743, -21.06224101826,  3.13082909833]
    c = [0.3374754822726147, 0.9761690190917186, 0.1607979714918209,
         0.0276438810333863, 0.0038405729373609, 0.0003951896511349,
         0.0000321767881768, 0.0000002888167364, 0.0000003960315187]
    u  = p - 0.5
    if abs(u) < 0.42:
        r = u * u
        return u * (((a[3]*r + a[2])*r + a[1])*r + a[0]) / ((((b[3]*r + b[2])*r + b[1])*r + b[0])*r + 1)
    r = math.log(-math.log(p if u < 0 else 1 - p))
    x = c[0]+r*(c[1]+r*(c[2]+r*(c[3]+r*(c[4]+r*(c[5]+r*(c[6]+r*(c[7]+r*c[8])))))))
    return -x if u < 0 else x


def calc_var_cvar(df: pd.DataFrame, confidence: float = 0.95) -> Dict[str, float]:
    """VaR e CVaR em 3 metodologias (% diário)."""
    ret = df["Close_Price"].pct_change().dropna() * 100
    alpha = 1 - confidence

    # 1. Histórico
    var_h   = np.percentile(ret, alpha * 100)
    tail_h  = ret[ret <= var_h]
    cvar_h  = tail_h.mean() if len(tail_h) > 0 else var_h

    # 2. Paramétrico (Normal)
    mu, sig = ret.mean(), ret.std()
    z       = _norm_ppf(alpha)
    var_p   = mu + z * sig
    cvar_p  = mu - sig * math.exp(-0.5 * z**2) / (math.sqrt(2 * math.pi) * alpha)

    # 3. Cornish-Fisher (ajuste skewness + kurtosis)
    s = float(ret.skew())
    k = float(ret.kurt())  # excess kurtosis
    z_cf  = z + (z**2 - 1)*s/6 + (z**3 - 3*z)*k/24 - (2*z**3 - 5*z)*s**2/36
    var_cf = mu + z_cf * sig
    tail_cf = ret[ret <= var_cf]
    cvar_cf = tail_cf.mean() if len(tail_cf) > 0 else var_p

    return {
        "var_h":   abs(var_h),  "cvar_h":  abs(cvar_h),
        "var_p":   abs(var_p),  "cvar_p":  abs(cvar_p),
        "var_cf":  abs(var_cf), "cvar_cf": abs(cvar_cf),
        "skew": s, "kurt": k, "vol_d": sig,
    }


def calc_kelly(df: pd.DataFrame, rf_daily: float = 14.50 / 252 / 100) -> Dict[str, float]:
    """Kelly Criterion contínuo e fracionário."""
    ret  = df["Close_Price"].pct_change().dropna()
    mu   = ret.mean()
    var  = ret.var()

    kelly_f = (mu - rf_daily) / var if var > 0 else 0.0
    wins   = ret[ret > 0]
    losses = ret[ret < 0]

    kelly_d = 0.0
    if len(wins) > 0 and len(losses) > 0:
        p    = len(wins) / len(ret)
        avg_w = wins.mean()
        avg_l = abs(losses.mean())
        b     = avg_w / avg_l if avg_l > 0 else 1.0
        kelly_d = (p * b - (1 - p)) / b

    return {
        "full":     kelly_f * 100,
        "half":     kelly_f * 50,
        "quarter":  kelly_f * 25,
        "discrete": kelly_d * 100,
        "win_rate": len(wins) / len(ret) * 100,
    }


def stress_test(price: float) -> pd.DataFrame:
    """9 cenários de stress test com impactos estimados."""
    scenarios = [
        ("Crash Sistêmico 2008",          -45.0, "2%",  "🔴 Extremo"),
        ("COVID Crash Mar/2020",          -35.0, "3%",  "🔴 Extremo"),
        ("Selic +500 bps (Choque Juro)",  -22.0, "8%",  "🟠 Alto"),
        ("USD/BRL +30% (Crise Cambial)",  -18.0, "10%", "🟠 Alto"),
        ("Petróleo -50% (Recessão)",      -15.0, "12%", "🟡 Moderado"),
        ("Recessão Técnica Brasil",       -20.0, "15%", "🟠 Alto"),
        ("Crise Fiscal (Spread +200bps)", -25.0, "10%", "🟠 Alto"),
        ("Contagio Cripto / Liquidity",   -12.0, "8%",  "🟡 Moderado"),
        ("Rally Risk-On Emergentes",      +25.0, "20%", "🟢 Positivo"),
    ]
    rows = []
    for name, imp, prob, sev in scenarios:
        rows.append({
            "Cenário":         name,
            "Impacto":         f"{imp:+.1f}%",
            "Preço Estressado":f"R$ {price*(1+imp/100):.2f}",
            "Prob. Histórica": prob,
            "Severidade":      sev,
        })
    return pd.DataFrame(rows)


# ==============================================================================
# 9. BACKTEST v2 — COM CUSTOS E MÉTRICAS AVANÇADAS
# ==============================================================================
def run_backtest(
    df: pd.DataFrame, fast: int = 9, slow: int = 21, cost_bps: float = 10
) -> Dict[str, Any]:
    bt = df.copy()
    bt["F"] = bt["Close_Price"].ewm(span=fast, adjust=False).mean()
    bt["S"] = bt["Close_Price"].ewm(span=slow, adjust=False).mean()
    bt["Sig"] = (bt["F"] > bt["S"]).astype(int)
    bt["Ret"] = bt["Close_Price"].pct_change()

    # Custo por trade (bps)
    cost = bt["Sig"].diff().abs() * (cost_bps / 10_000)
    bt["Strat_Ret"] = bt["Sig"].shift(1) * bt["Ret"] - cost
    bt["BH_Ret"]    = bt["Ret"]

    bt["Equity"] = (1 + bt["Strat_Ret"].fillna(0)).cumprod()
    bt["BH_Eq"]  = (1 + bt["BH_Ret"].fillna(0)).cumprod()

    total_r = (bt["Equity"].iloc[-1] - 1) * 100
    bh_r    = (bt["BH_Eq"].iloc[-1]  - 1) * 100

    dd = ((bt["Equity"] - bt["Equity"].cummax()) / bt["Equity"].cummax()).fillna(0)
    max_dd = dd.min() * 100

    ann_s    = bt["Strat_Ret"].mean() * 252 * 100
    dn_std   = bt["Strat_Ret"][bt["Strat_Ret"] < 0].std() * np.sqrt(252) * 100
    sortino  = (ann_s - 14.50) / dn_std if dn_std > 0 else 0.0
    calmar   = abs(ann_s / max_dd)       if max_dd < 0 else 0.0

    active = bt[bt["Sig"].shift(1) == 1]
    wins   = active[active["Strat_Ret"] > 0]["Strat_Ret"]
    losses = active[active["Strat_Ret"] < 0]["Strat_Ret"]
    wr     = len(wins) / len(active) * 100 if len(active) > 0 else 0.0
    pf     = abs(wins.sum() / losses.sum()) if len(losses) > 0 and losses.sum() != 0 else 0.0
    trades = int(bt["Sig"].diff().eq(1).sum())

    return {
        "total_r": total_r, "bh_r": bh_r, "max_dd": max_dd,
        "win_rate": wr, "sortino": sortino, "calmar": calmar,
        "profit_factor": pf, "trades": trades,
        "curve": bt[["Equity", "BH_Eq"]].dropna(),
        "drawdown": dd.dropna(),
    }


# ==============================================================================
# 10. MONTE CARLO v2 — BANDAS PERCENTÍLICAS
# ==============================================================================
def run_monte_carlo(
    df: pd.DataFrame, days: int = 30, sims: int = 500
) -> Tuple[np.ndarray, go.Figure, Dict[str, float]]:
    """Monte Carlo com bandas IC 5/25/75/95%."""
    log_ret = np.log(1 + df["Close_Price"].pct_change()).dropna()
    drift   = log_ret.mean() - 0.5 * log_ret.var()
    sigma   = log_ret.std()
    s0      = df["Close_Price"].iloc[-1]

    rand    = np.random.normal(0, 1, (days, sims))
    factors = np.exp(drift + sigma * rand)

    paths     = np.zeros((days, sims))
    paths[0]  = s0
    for t in range(1, days):
        paths[t] = paths[t - 1] * factors[t]

    x   = list(range(days))
    p5  = np.percentile(paths, 5,  axis=1)
    p25 = np.percentile(paths, 25, axis=1)
    p50 = np.percentile(paths, 50, axis=1)
    p75 = np.percentile(paths, 75, axis=1)
    p95 = np.percentile(paths, 95, axis=1)
    avg = paths.mean(axis=1)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x + x[::-1], y=list(p95) + list(p5[::-1]),
        fill="toself", fillcolor="rgba(59,130,246,.06)",
        line_color="rgba(0,0,0,0)", name="IC 90%",
    ))
    fig.add_trace(go.Scatter(
        x=x + x[::-1], y=list(p75) + list(p25[::-1]),
        fill="toself", fillcolor="rgba(59,130,246,.14)",
        line_color="rgba(0,0,0,0)", name="IC 50%",
    ))
    fig.add_trace(go.Scatter(x=x, y=p50, mode="lines", line=dict(color="#3b82f6", width=2), name="Mediana"))
    fig.add_trace(go.Scatter(x=x, y=avg, mode="lines", line=dict(color="#fafafa", width=1.5, dash="dash"), name="Média"))
    fig.add_hline(y=s0, line_dash="dot", line_color="rgba(255,255,255,.18)")
    fig.update_layout(
        height=300, margin=dict(l=0, r=0, t=8, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#a1a1aa", size=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1, font_size=9, bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#27272a")
    fig.update_yaxes(showgrid=True, gridcolor="#27272a")

    final = paths[-1]
    return paths, fig, {
        "mean": float(np.mean(final)),
        "median": float(np.median(final)),
        "p5":   float(np.percentile(final, 5)),
        "p95":  float(np.percentile(final, 95)),
        "prob_up": float((final > s0).mean() * 100),
    }


# ==============================================================================
# 11. SAZONALIDADE
# ==============================================================================
def calc_seasonality(df: pd.DataFrame) -> pd.DataFrame:
    monthly = df["Close_Price"].resample("ME").last()
    ret = (monthly.pct_change() * 100).groupby(monthly.index.month)
    out = ret.agg(["mean", "std", "count"])
    out.columns = ["Retorno", "Desvio", "Amostras"]
    mmap = {1:"Jan",2:"Fev",3:"Mar",4:"Abr",5:"Mai",6:"Jun",
            7:"Jul",8:"Ago",9:"Set",10:"Out",11:"Nov",12:"Dez"}
    out.index = out.index.map(mmap)
    return out


def plot_seasonality_fig(saz: pd.DataFrame) -> go.Figure:
    cols = ["#10b981" if v >= 0 else "#f43f5e" for v in saz["Retorno"]]
    fig  = go.Figure()
    fig.add_trace(go.Bar(
        x=saz.index, y=saz["Retorno"],
        marker_color=cols, marker_line_width=0, opacity=0.85,
        error_y=dict(type="data", array=saz["Desvio"].fillna(0).tolist(),
                     visible=True, color="rgba(255,255,255,.18)"),
    ))
    fig.update_layout(
        height=260, margin=dict(l=0, r=0, t=8, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#a1a1aa", size=10), showlegend=False,
    )
    fig.update_yaxes(showgrid=True, gridcolor="#27272a", zerolinecolor="#3f3f46")
    fig.update_xaxes(showgrid=False)
    return fig


# ==============================================================================
# 12. BLACK-SCHOLES COMPLETO + PAYOFF
# ==============================================================================
def _cdf(x: float) -> float:
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

def _pdf(x: float) -> float:
    return math.exp(-0.5 * x**2) / math.sqrt(2 * math.pi)


def black_scholes(S: float, K: float, T: float, r: float, sigma: float) -> Dict[str, float]:
    zero = {k: 0.0 for k in ["call","put","delta_c","delta_p","gamma","vega","theta_c","theta_p","rho_c","rho_p","d1","d2"]}
    if T <= 0 or sigma <= 0 or S <= 0:
        return zero
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    Ke = K * math.exp(-r * T)
    call  = S * _cdf(d1)  - Ke * _cdf(d2)
    put   = Ke * _cdf(-d2) - S * _cdf(-d1)
    dc    = _cdf(d1)
    dp    = dc - 1
    gamma = _pdf(d1) / (S * sigma * math.sqrt(T))
    vega  = S * _pdf(d1) * math.sqrt(T) / 100
    tc = (-(S * _pdf(d1) * sigma) / (2 * math.sqrt(T)) - r * Ke * _cdf(d2))  / 365
    tp = (-(S * _pdf(d1) * sigma) / (2 * math.sqrt(T)) + r * Ke * _cdf(-d2)) / 365
    rc = Ke * T * _cdf(d2)  / 100
    rp = -Ke * T * _cdf(-d2) / 100
    return {"call": call, "put": put, "delta_c": dc, "delta_p": dp,
            "gamma": gamma, "vega": vega, "theta_c": tc, "theta_p": tp,
            "rho_c": rc, "rho_p": rp, "d1": d1, "d2": d2}


def plot_payoff(S: float, K: float, call_prem: float, put_prem: float) -> go.Figure:
    px   = np.linspace(S * 0.6, S * 1.4, 300)
    p_call = np.maximum(px - K, 0) - call_prem
    p_put  = np.maximum(K - px, 0) - put_prem
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=px, y=p_call, mode="lines", line=dict(color="#10b981", width=2), name="Call (Long)"))
    fig.add_trace(go.Scatter(x=px, y=p_put,  mode="lines", line=dict(color="#f43f5e",  width=2), name="Put (Long)"))
    fig.add_hline(y=0, line_dash="dot", line_color="rgba(255,255,255,.25)")
    fig.add_vline(x=K, line_dash="dot", line_color="rgba(234,179,8,.5)",
                  annotation_text="Strike", annotation_font_color="#eab308")
    fig.add_vline(x=S, line_dash="dot", line_color="rgba(255,255,255,.2)",
                  annotation_text="Spot",   annotation_font_color="#a1a1aa")
    fig.update_layout(
        title="Payoff no Vencimento", height=280,
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#a1a1aa", size=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, font_size=9, bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#27272a", title="Preço no Vencimento")
    fig.update_yaxes(showgrid=True, gridcolor="#27272a", zerolinecolor="#3f3f46", title="P&L (R$)")
    return fig


# ==============================================================================
# 13. MASTER CHART v2 — Volume + EMA 50/200 + RSI
# ==============================================================================
def plot_master_chart(df: pd.DataFrame, fibo: Dict[str, float]) -> go.Figure:
    fig = make_subplots(
        rows=4, cols=1, shared_xaxes=True,
        vertical_spacing=0.018,
        row_heights=[0.55, 0.15, 0.15, 0.15],
    )
    up, dn = "#10b981", "#f43f5e"

    # ── Candlestick ───────────────────────────────────────────────────────────
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close_Price"], name="Preço",
        increasing_line_color=up, decreasing_line_color=dn,
        increasing_fillcolor=up, decreasing_fillcolor=dn, line_width=1,
    ), row=1, col=1)

    # ── Médias Móveis ─────────────────────────────────────────────────────────
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA_20"],  mode="lines", line=dict(color="#3b82f6", width=1.1), name="SMA 20"),  row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA_50"],  mode="lines", line=dict(color="#eab308", width=1.1), name="EMA 50"),  row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA_200"], mode="lines", line=dict(color="#f43f5e", width=1.1), name="EMA 200"), row=1, col=1)

    # ── Bollinger Bands ───────────────────────────────────────────────────────
    bc = "rgba(161,161,170,.25)"
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_Upper"], mode="lines", line=dict(color=bc, width=1), showlegend=False), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_Lower"], mode="lines", line=dict(color=bc, width=1),
                             fill="tonexty", fillcolor="rgba(161,161,170,.03)", showlegend=False), row=1, col=1)

    # ── Fibonacci ─────────────────────────────────────────────────────────────
    fib_cols = ["rgba(244,63,94,.5)","rgba(251,146,60,.5)","rgba(234,179,8,.5)",
                "rgba(59,130,246,.5)","rgba(16,185,129,.5)","rgba(139,92,246,.5)","rgba(16,185,129,.3)"]
    for (name, price), col_f in zip(fibo.items(), fib_cols):
        fig.add_hline(y=price, line_dash="dot", line_color=col_f, line_width=0.8,
                      annotation_text=name, annotation_font_color=col_f,
                      annotation_font_size=9, row=1, col=1)

    # ── Volume ────────────────────────────────────────────────────────────────
    close = df["Close_Price"]
    vc = [up if close.iloc[i] >= close.iloc[max(i-1,0)] else dn for i in range(len(df))]
    fig.add_trace(go.Bar(x=df.index, y=df["Volume"], marker_color=vc,
                         marker_line_width=0, opacity=0.55, showlegend=False), row=2, col=1)

    # ── RSI ───────────────────────────────────────────────────────────────────
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], mode="lines",
                             line=dict(color="#a1a1aa", width=1.1), showlegend=False), row=3, col=1)
    for lv, lc in [(70,"rgba(244,63,94,.45)"), (50,"rgba(255,255,255,.1)"), (30,"rgba(16,185,129,.45)")]:
        fig.add_hline(y=lv, line_dash="dot" if lv != 50 else "solid", line_color=lc, line_width=1, row=3, col=1)

    # ── MACD ──────────────────────────────────────────────────────────────────
    hcols = [up if v >= 0 else dn for v in df["MACD_Hist"]]
    fig.add_trace(go.Bar(x=df.index, y=df["MACD_Hist"], marker_color=hcols,
                         marker_line_width=0, opacity=0.8, showlegend=False), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD"],        mode="lines", line=dict(color="#3b82f6", width=1), showlegend=False), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["Signal_Line"], mode="lines", line=dict(color="#eab308", width=1), showlegend=False), row=4, col=1)

    fig.update_layout(
        xaxis_rangeslider_visible=False, height=780,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#a1a1aa", size=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1,
                    font_size=10, bgcolor="rgba(0,0,0,0)"),
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="#27272a")
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="#27272a", zeroline=False)
    fig.update_yaxes(title_text="Vol",  row=2, col=1)
    fig.update_yaxes(title_text="RSI",  row=3, col=1)
    fig.update_yaxes(title_text="MACD", row=4, col=1)
    return fig


# ==============================================================================
# 14. ORÁCULO IA v2 — CONTEXTO RICO (40+ VARIÁVEIS)
# ==============================================================================
def build_ai_context(
    ticker: str, ultima: pd.Series, fibo: Dict, mc: Dict, bt: Dict,
    saz: pd.DataFrame, var_d: Dict, kelly: Dict, regime: Dict,
    fund: Dict, ann_ret: float, sharpe: float, sortino: float, calmar: float,
) -> str:
    mm = {"Jan":"Jan","Feb":"Fev","Mar":"Mar","Apr":"Abr","May":"Mai","Jun":"Jun",
          "Jul":"Jul","Aug":"Ago","Sep":"Set","Oct":"Out","Nov":"Nov","Dec":"Dez"}
    m_pt = mm.get(datetime.now().strftime("%b"), "N/A")
    saz_m = saz.loc[m_pt, "Retorno"] if m_pt in saz.index else 0.0

    fund_str = "\n".join([f"  {k}: {v}" for k, v in fund.items()])

    return f"""
[IDENTIFICAÇÃO]
Ticker: {ticker} | Setor: {fund.get('Setor','N/A')} | País: {fund.get('País','N/A')}

[REGIME DE MERCADO]
Regime: {regime['regime']} | {regime['cross']}
Retorno 60d: {regime['ret60']:.1f}% | Volatilidade 20d: {regime['vol20']:.1f}%

[PRICE ACTION]
Spot: {ultima['Close_Price']:.2f}
SMA20: {ultima['SMA_20']:.2f} | EMA9: {ultima['EMA_9']:.2f} | EMA21: {ultima['EMA_21']:.2f}
EMA50: {ultima['EMA_50']:.2f} | EMA200: {ultima['EMA_200']:.2f}
ATR: {ultima['ATR']:.2f} | Vol 21d: {ultima['Vol_21d']:.1f}%

[INDICADORES TÉCNICOS]
RSI(14): {ultima['RSI']:.1f} {'[SOBRECOMPRADO]' if ultima['RSI']>70 else '[SOBREVENDIDO]' if ultima['RSI']<30 else '[NEUTRO]'}
MACD: {ultima['MACD']:.4f} | Sinal: {ultima['Signal_Line']:.4f} | Hist: {ultima['MACD_Hist']:.4f}
MFI(14): {ultima['MFI']:.1f} {'[SOBRECOMPRADO]' if ultima['MFI']>80 else '[SOBREVENDIDO]' if ultima['MFI']<20 else '[NEUTRO]'}
Stoch %K: {ultima['Stoch_K']:.1f} | %D: {ultima['Stoch_D']:.1f}
BB Width: {ultima['BB_Width']:.4f} | %B: {ultima['BB_Pct']:.2f}

[FIBONACCI 252 SESSÕES]
{chr(10).join([f"  {k}: {v:.2f}" for k,v in fibo.items()])}

[PERFORMANCE AJUSTADA A RISCO]
Retorno Anualizado: {ann_ret:.2f}%
Sharpe:  {sharpe:.2f} | Sortino: {sortino:.2f} | Calmar: {calmar:.2f}

[VaR / CVaR — 95% — DIÁRIO]
Histórico:     VaR {var_d['var_h']:.2f}%  | CVaR {var_d['cvar_h']:.2f}%
Paramétrico:   VaR {var_d['var_p']:.2f}%  | CVaR {var_d['cvar_p']:.2f}%
Cornish-Fisher:VaR {var_d['var_cf']:.2f}% | CVaR {var_d['cvar_cf']:.2f}%
Skewness: {var_d['skew']:.3f} | Curtose: {var_d['kurt']:.3f} | Vol diária: {var_d['vol_d']:.2f}%

[KELLY CRITERION]
Full: {kelly['full']:.1f}% | Half: {kelly['half']:.1f}% | Quarter: {kelly['quarter']:.1f}%
Discreto: {kelly['discrete']:.1f}% | Win Rate: {kelly['win_rate']:.1f}%

[MONTE CARLO 30d — 500 SIMULAÇÕES]
Média: {mc['mean']:.2f} | Mediana: {mc['median']:.2f}
IC 90%: [{mc['p5']:.2f} ; {mc['p95']:.2f}]
Prob. de Alta: {mc['prob_up']:.1f}%

[BACKTEST EMA 9×21 (com custos)]
Algo: {bt['total_r']:.2f}% | B&H: {bt['bh_r']:.2f}%
Max DD: {bt['max_dd']:.2f}% | Win Rate: {bt['win_rate']:.1f}%
Sortino: {bt['sortino']:.2f} | Calmar: {bt['calmar']:.2f}
Profit Factor: {bt['profit_factor']:.2f} | Trades: {bt['trades']}

[SAZONALIDADE]
Mês atual ({m_pt}): {saz_m:.2f}%
Melhor: {saz['Retorno'].idxmax()} ({saz['Retorno'].max():.2f}%)
Pior: {saz['Retorno'].idxmin()} ({saz['Retorno'].min():.2f}%)

[FUNDAMENTOS]
{fund_str}
"""


def generate_ai_response(
    prompt: str, context: str, api_key: str, persona: str
) -> str:
    if not api_key.strip():
        return "⚠️ Nenhuma API Key configurada. Insira sua chave Groq no painel lateral."
    if not GROQ_AVAILABLE:
        return "⚠️ Biblioteca `groq` não instalada. Execute: `pip install groq`"

    personas = {
        "Risco & Valuation": "Priorize VaR, CVaR, Sharpe, Sortino, Kelly e múltiplos contábeis. Sizing rigoroso.",
        "Estratégia Macro":  "Cruze dados do ativo com Selic, DXY, geopolítica. Identifique correlações macro.",
        "Quant & Volatilidade": "Foco em Backtest, Monte Carlo, Fibonacci e estrutura estocástica da volatilidade.",
    }
    foco = personas.get(persona, personas["Risco & Valuation"])

    system = f"""Você é o Cérebro Quantamental — motor analítico institucional de nível hedge fund.

PERSONA: {persona}
DIRETRIZ: {foco}

PROTOCOLO:
- Tom: institucional, denso, frio, pragmático. Zero verbose.
- Nunca invente dados. Use EXCLUSIVAMENTE os números injetados.
- Bullet points objetivos. Sem LaTeX. Use R$ e %.
- Encerre com um parágrafo de conclusão operacional (3-4 linhas)."""

    try:
        client  = Groq(api_key=api_key)
        resp    = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": f"[MACRO]\n{MACRO}\n\n[MATRIZ QUANTAMENTAL]\n{context}\n\n[QUERY]\n{prompt}"},
            ],
            model="llama-3.1-8b-instant",
            temperature=0.22,
            max_tokens=1500,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"⚠️ Erro Groq: {e}"


# ==============================================================================
# 15. FRONTEND — MAIN
# ==============================================================================
def main() -> None:

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="display:flex;justify-content:space-between;align-items:center;
                padding:.7rem 0;margin-bottom:1.4rem;border-bottom:1px solid #27272a;">
        <div style="display:flex;align-items:center;gap:10px;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
                 stroke="#3b82f6" stroke-width="2.5">
                <polygon points="12 2 2 7 12 12 22 7 12 2"/>
                <polyline points="2 17 12 22 22 17"/>
                <polyline points="2 12 12 17 22 12"/>
            </svg>
            <span style="font-size:.98rem;font-weight:700;color:#fafafa;letter-spacing:-.02em;">
                Terminal Quantamental <span style="color:#3b82f6;">v2.0</span>
            </span>
        </div>
        <span class="badge-ok">
            <span style="height:6px;width:6px;background:#10b981;border-radius:50%;display:inline-block;"></span>
            SISTEMAS OPERACIONAIS
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown('<p class="sec-hdr">PARÂMETROS</p>', unsafe_allow_html=True)

        selecao  = st.selectbox("Ativo", list(CATALOGO.keys()), label_visibility="collapsed")
        ticker   = (
            st.text_input("Ticker", value="PETR4.SA", placeholder="Ex: VALE3.SA").upper().strip()
            if selecao == "🔍 Ticker Manual"
            else CATALOGO[selecao]
        )
        period   = st.select_slider("Horizonte", ["6mo","1y","2y","5y","max"], value="2y")
        ma_win   = st.slider("Janela SMA", 5, 200, 20, 5)

        st.markdown("---")
        st.markdown('<p class="sec-hdr">IA — GROQ API</p>', unsafe_allow_html=True)
        api_key  = st.text_input(
            "Chave API",
            type="password",
            placeholder="gsk_...",
            help="Não é armazenada. Obtenha em console.groq.com",
        )

        st.markdown("---")
        st.markdown('<p class="sec-hdr">EXPORTAÇÃO</p>', unsafe_allow_html=True)
        export_slot = st.empty()

        st.markdown("---")
        st.markdown("""
        <div style="font-family:'JetBrains Mono',monospace;font-size:.68rem;color:#3f3f46;line-height:2;">
            [✓] VaR/CVaR — 3 metodologias<br>
            [✓] Kelly Criterion (4 variantes)<br>
            [✓] Stress Test — 9 cenários<br>
            [✓] Monte Carlo — 500 sims IC<br>
            [✓] Backtest com custos reais<br>
            [✓] Sortino · Calmar · PF<br>
            [✓] Regime Detection<br>
            [✓] Rolling Beta vs IBOV<br>
            [✓] Black-Scholes + Payoff<br>
            [✓] EMA 50 · 200 · Volume<br>
            [✓] IA com 40+ variáveis<br>
        </div>
        """, unsafe_allow_html=True)

    # ── Data Pipeline ─────────────────────────────────────────────────────────
    df_raw   = fetch_market_data(ticker, period)
    fund     = fetch_fundamentals(ticker)
    bench    = fetch_benchmark(period)

    if df_raw is None:
        st.error(f"❌ Falha na ingestão para `{ticker}`. Verifique o ticker ou a conexão.")
        return

    # ── Processamento ─────────────────────────────────────────────────────────
    df, fibo, ann_ret, sharpe, sortino, calmar = calculate_indicators(df_raw, ma_win)
    _, mc_fig, mc_stats = run_monte_carlo(df)
    bt_res   = run_backtest(df)
    saz      = calc_seasonality(df)
    var_d    = calc_var_cvar(df)
    kelly    = calc_kelly(df)
    regime   = detect_regime(df)
    ultima   = df.iloc[-1]

    # Export
    with export_slot:
        st.download_button("↓ Exportar CSV", to_csv(df), f"{ticker}_v2.csv", "text/csv", use_container_width=True)

    # Rolling Beta
    beta_now = None
    beta_ser = None
    if bench is not None:
        try:
            beta_ser = rolling_beta(df, bench)
            beta_now = float(beta_ser.iloc[-1])
        except Exception:
            pass

    # ── KPI Row ───────────────────────────────────────────────────────────────
    d1pct = ((ultima["Close_Price"] / df["Close_Price"].iloc[-2]) - 1) * 100 if len(df) > 1 else 0.0
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Preço",         f"R$ {ultima['Close_Price']:.2f}", f"{d1pct:+.2f}% (1d)")
    k2.metric("ATR / Vol 21d", f"R$ {ultima['ATR']:.2f}",        f"{ultima['Vol_21d']:.1f}%")
    k3.metric("RSI / MFI",     f"{ultima['RSI']:.0f} / {ultima['MFI']:.0f}")
    k4.metric("Sharpe / Sortino", f"{sharpe:.2f} / {sortino:.2f}")
    k5.metric("VaR CF 95%",    f"{var_d['var_cf']:.2f}%",        f"CVaR {var_d['cvar_cf']:.2f}%", delta_color="inverse")
    k6.metric("Half Kelly",    f"{kelly['half']:.1f}%",           f"WR {kelly['win_rate']:.0f}%")

    st.markdown("<br>", unsafe_allow_html=True)

    # Regime Card
    col_reg, col_rest = st.columns([1, 4])
    with col_reg:
        st.markdown(f"""
        <div class="regime-card" style="border-left:3px solid {regime['color']};">
            <div class="sec-hdr" style="margin-bottom:.4rem;">REGIME</div>
            <div style="font-size:1rem;font-weight:700;color:{regime['color']};">{regime['regime']}</div>
            <div style="font-size:.72rem;color:#a1a1aa;margin:.3rem 0;">{regime['desc']}</div>
            <div style="font-size:.7rem;font-family:'JetBrains Mono',monospace;color:{regime['cross_col']};">{regime['cross']}</div>
            <div style="font-size:.68rem;color:#52525b;margin-top:.4rem;">
                Ret 60d: {regime['ret60']:+.1f}% | Vol: {regime['vol20']:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Abas ──────────────────────────────────────────────────────────────────
    t1, t2, t3, t4, t5, t6 = st.tabs([
        "📈 Análise Técnica",
        "🛡️ Risco Quantitativo",
        "🎲 Modelos Estatísticos",
        "⚙️ Derivativos & Sizing",
        "📊 Backtest & Fundamentos",
        "🧠 Inteligência Artificial",
    ])

    # ── Tab 1: Análise Técnica ─────────────────────────────────────────────────
    with t1:
        fig_m = plot_master_chart(df, fibo)
        st.plotly_chart(fig_m, use_container_width=True, config={"displayModeBar": False})

        st.markdown('<p class="sec-hdr" style="margin-top:1.2rem;">RETRAÇÃO DE FIBONACCI — 252 SESSÕES</p>', unsafe_allow_html=True)
        fib_col_list = st.columns(len(fibo))
        fib_colors   = ["#f43f5e","#fb923c","#eab308","#3b82f6","#10b981","#8b5cf6","#10b981"]
        for (name, price), col_f, c_f in zip(fibo.items(), fib_col_list, fib_colors):
            dist = (ultima["Close_Price"] - price) / price * 100
            col_f.markdown(f"""
            <div class="fib-card" style="border-top:2px solid {c_f};">
                <div style="font-size:.63rem;color:#a1a1aa;font-weight:600;">{name}</div>
                <div style="font-size:.95rem;font-family:'JetBrains Mono',monospace;
                            color:#fafafa;font-weight:700;">R$ {price:.2f}</div>
                <div style="font-size:.68rem;color:{'#10b981' if dist>=0 else '#f43f5e'};">{dist:+.1f}%</div>
            </div>""", unsafe_allow_html=True)

    # ── Tab 2: Risco Quantitativo ──────────────────────────────────────────────
    with t2:
        st.markdown('<p class="sec-hdr">VaR / CVaR — CONFIANÇA 95% — DIÁRIO</p>', unsafe_allow_html=True)
        v1, v2, v3 = st.columns(3)

        with v1:
            st.markdown('<div class="ibox ibox-blue"><div style="font-size:.68rem;color:#a1a1aa;font-weight:700;text-transform:uppercase;margin-bottom:.5rem;">Histórico</div>', unsafe_allow_html=True)
            st.metric("VaR",  f"{var_d['var_h']:.2f}%",  delta_color="off")
            st.metric("CVaR", f"{var_d['cvar_h']:.2f}%", delta_color="off")
            st.markdown("</div>", unsafe_allow_html=True)

        with v2:
            st.markdown('<div class="ibox ibox-gold"><div style="font-size:.68rem;color:#a1a1aa;font-weight:700;text-transform:uppercase;margin-bottom:.5rem;">Paramétrico</div>', unsafe_allow_html=True)
            st.metric("VaR",  f"{var_d['var_p']:.2f}%",  delta_color="off")
            st.metric("CVaR", f"{var_d['cvar_p']:.2f}%", delta_color="off")
            st.markdown("</div>", unsafe_allow_html=True)

        with v3:
            st.markdown('<div class="ibox ibox-red"><div style="font-size:.68rem;color:#a1a1aa;font-weight:700;text-transform:uppercase;margin-bottom:.5rem;">Cornish-Fisher</div>', unsafe_allow_html=True)
            st.metric("VaR",  f"{var_d['var_cf']:.2f}%",  delta_color="off")
            st.metric("CVaR", f"{var_d['cvar_cf']:.2f}%", delta_color="off")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="ibox" style="margin-top:.75rem;font-size:.78rem;color:#a1a1aa;">
            📐 Skewness: <b style="color:#fafafa;">{var_d['skew']:.3f}</b> &nbsp;|&nbsp;
            Curtose Exc.: <b style="color:#fafafa;">{var_d['kurt']:.3f}</b> &nbsp;|&nbsp;
            Vol Diária: <b style="color:#fafafa;">{var_d['vol_d']:.2f}%</b>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<p class="sec-hdr">KELLY CRITERION — SIZING ÓTIMO</p>', unsafe_allow_html=True)
        kc1, kc2, kc3, kc4 = st.columns(4)
        kc1.metric("Full Kelly",    f"{kelly['full']:.1f}%",     help="Agressivo — raramente usado em produção")
        kc2.metric("Half Kelly",    f"{kelly['half']:.1f}%",     help="Padrão institucional recomendado")
        kc3.metric("Quarter Kelly", f"{kelly['quarter']:.1f}%",  help="Ultraconservador — operações de alta incerteza")
        kc4.metric("Kelly Discreto",f"{kelly['discrete']:.1f}%", help="Baseado em win/loss empírico da série")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<p class="sec-hdr">STRESS TEST — 9 CENÁRIOS</p>', unsafe_allow_html=True)
        st.dataframe(stress_test(ultima["Close_Price"]), use_container_width=True, hide_index=True)

        if beta_ser is not None and beta_now is not None:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<p class="sec-hdr">ROLLING BETA vs IBOVESPA (60 DIAS)</p>', unsafe_allow_html=True)
            st.metric(
                "Beta Atual",
                f"{beta_now:.3f}",
                "Mais volátil que IBOV" if beta_now > 1 else "Menos volátil que IBOV",
                delta_color="off",
            )
            fig_b = go.Figure()
            fig_b.add_trace(go.Scatter(x=beta_ser.index, y=beta_ser.values, mode="lines",
                                       line=dict(color="#3b82f6", width=1.5), name="Beta 60d"))
            fig_b.add_hline(y=1, line_dash="dot", line_color="rgba(255,255,255,.2)")
            fig_b.add_hline(y=0, line_dash="dot", line_color="rgba(255,255,255,.1)")
            fig_b.update_layout(height=180, margin=dict(l=0,r=0,t=8,b=0),
                                 paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                 font=dict(family="Inter", color="#a1a1aa", size=10), showlegend=False)
            fig_b.update_xaxes(showgrid=True, gridcolor="#27272a")
            fig_b.update_yaxes(showgrid=True, gridcolor="#27272a")
            st.plotly_chart(fig_b, use_container_width=True, config={"displayModeBar": False})

    # ── Tab 3: Modelos Estatísticos ────────────────────────────────────────────
    with t3:
        mc_col, saz_col = st.columns(2, gap="large")

        with mc_col:
            st.markdown('<p class="sec-hdr">MONTE CARLO — 500 SIMULAÇÕES (30 PREGÕES)</p>', unsafe_allow_html=True)
            st.plotly_chart(mc_fig, use_container_width=True, config={"displayModeBar": False})
            s1, s2, s3 = st.columns(3)
            s1.metric("Mediana (P50)", f"R$ {mc_stats['median']:.2f}")
            s2.metric("Bear (P5)",     f"R$ {mc_stats['p5']:.2f}",   delta_color="off")
            s3.metric("Bull (P95)",    f"R$ {mc_stats['p95']:.2f}")
            pup = mc_stats["prob_up"]
            st.markdown(f"""
            <div class="ibox {'ibox-green' if pup>50 else 'ibox-red'}" style="margin-top:.5rem;">
                Prob. de Alta em 30 pregões:
                <b style="color:{'#10b981' if pup>50 else '#f43f5e'};font-size:1.05rem;"> {pup:.1f}%</b>
            </div>""", unsafe_allow_html=True)

        with saz_col:
            st.markdown('<p class="sec-hdr">SAZONALIDADE HISTÓRICA MENSAL</p>', unsafe_allow_html=True)
            st.plotly_chart(plot_seasonality_fig(saz), use_container_width=True, config={"displayModeBar": False})
            saz_disp = saz.copy()
            saz_disp["Retorno"] = saz_disp["Retorno"].map(lambda x: f"{x:+.2f}%")
            saz_disp["Desvio"]  = saz_disp["Desvio"].map(lambda x: f"±{x:.2f}%" if pd.notna(x) else "N/A")
            saz_disp.columns    = ["Retorno Médio","Desvio Padrão","Amostras"]
            st.dataframe(saz_disp.T, use_container_width=True)

    # ── Tab 4: Derivativos & Sizing ────────────────────────────────────────────
    with t4:
        d_c1, d_c2 = st.columns(2, gap="large")

        with d_c1:
            st.markdown('<p class="sec-hdr">DIMENSIONAMENTO DE POSIÇÃO</p>', unsafe_allow_html=True)
            capital    = st.number_input("Capital (R$)",           value=250_000.0, step=10_000.0, format="%.2f")
            risk_pct   = st.number_input("Risco por Trade (%)",    value=1.0,       step=0.1, min_value=0.1, max_value=5.0)
            entry_p    = st.number_input("Entrada (R$)",           value=float(ultima["Close_Price"]), step=0.01)
            stop_p     = st.number_input("Hard Stop (R$)",         value=float(ultima["Close_Price"] - ultima["ATR"] * 1.5), step=0.01, help="Sugestão: 1.5× ATR")
            target_p   = st.number_input("Alvo de Lucro (R$)",    value=float(ultima["Close_Price"] + ultima["ATR"] * 3.0), step=0.01, help="Sugestão: 3× ATR → RR 2:1")

            if stop_p < entry_p and target_p > entry_p:
                risk_r  = capital * (risk_pct / 100)
                lotes   = int(risk_r // (entry_p - stop_p))
                exp_b   = lotes * entry_p
                max_loss= lotes * (entry_p - stop_p)
                max_win = lotes * (target_p - entry_p)
                rr      = (target_p - entry_p) / (entry_p - stop_p)
                rr_col  = "#10b981" if rr >= 2 else "#eab308" if rr >= 1.5 else "#f43f5e"
                st.markdown(f"""
                <div class="ibox ibox-green" style="margin-top:1rem;">
                    <div class="sec-hdr">ALOCAÇÃO CALCULADA</div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:.6rem;
                                font-family:'JetBrains Mono',monospace;">
                        <div><span style="color:#52525b;font-size:.66rem;">LOTES</span><br>
                             <span style="font-size:1.15rem;color:#fafafa;font-weight:700;">{lotes:,}</span></div>
                        <div><span style="color:#52525b;font-size:.66rem;">EXPOSIÇÃO</span><br>
                             <span style="font-size:1.15rem;color:#fafafa;font-weight:700;">R$ {exp_b:,.0f}</span></div>
                        <div><span style="color:#52525b;font-size:.66rem;">RISCO MÁX</span><br>
                             <span style="font-size:1.05rem;color:#f43f5e;font-weight:700;">R$ {max_loss:,.0f}</span></div>
                        <div><span style="color:#52525b;font-size:.66rem;">GANHO MÁX</span><br>
                             <span style="font-size:1.05rem;color:#10b981;font-weight:700;">R$ {max_win:,.0f}</span></div>
                        <div><span style="color:#52525b;font-size:.66rem;">RATIO R:R</span><br>
                             <span style="font-size:1.05rem;color:{rr_col};font-weight:700;">1 : {rr:.2f}</span></div>
                        <div><span style="color:#52525b;font-size:.66rem;">HALF KELLY</span><br>
                             <span style="font-size:1.05rem;color:#3b82f6;font-weight:700;">{kelly['half']:.1f}%</span></div>
                    </div>
                </div>""", unsafe_allow_html=True)
                if rr < 1.5:
                    st.warning("⚠️ R:R abaixo de 1.5:1 — abaixo do threshold institucional mínimo.")
            else:
                st.error("❌ Stop deve ser inferior à Entrada, e Alvo superior à Entrada.")

        with d_c2:
            st.markdown('<p class="sec-hdr">BLACK-SCHOLES + GREGAS</p>', unsafe_allow_html=True)
            vol_atr  = float((ultima["ATR"] / ultima["Close_Price"]) * math.sqrt(252) * 100)
            bs_k     = st.number_input("Strike (R$)",            value=float(ultima["Close_Price"] * 1.05), step=0.1)
            bs_d     = st.number_input("Dias p/ Vencimento",     value=21, min_value=1, max_value=365)
            bs_vol   = st.number_input("Volatilidade Impl. (%)", value=vol_atr, step=0.5)
            bs_rf    = st.number_input("Taxa Livre de Risco (%)", value=14.50, step=0.1)

            g = black_scholes(ultima["Close_Price"], bs_k, bs_d/252.0, bs_rf/100.0, bs_vol/100.0)

            gc1, gc2, gc3 = st.columns(3)
            gc1.metric("Call",  f"R$ {g['call']:.3f}")
            gc2.metric("Put",   f"R$ {g['put']:.3f}")
            gc3.metric("Delta", f"{g['delta_c']*100:.1f}%")

            gc4, gc5, gc6, gc7 = st.columns(4)
            gc4.metric("Gamma",    f"{g['gamma']:.5f}")
            gc5.metric("Vega",     f"R$ {g['vega']:.4f}")
            gc6.metric("Theta/d",  f"R$ {g['theta_c']:.4f}")
            gc7.metric("Rho",      f"R$ {g['rho_c']:.4f}")

            st.plotly_chart(plot_payoff(ultima["Close_Price"], bs_k, g["call"], g["put"]),
                            use_container_width=True, config={"displayModeBar": False})

    # ── Tab 5: Backtest & Fundamentos ──────────────────────────────────────────
    with t5:
        bc1, bc2 = st.columns(2, gap="large")

        with bc1:
            st.markdown('<p class="sec-hdr">BACKTEST EMA 9×21 — COM CUSTOS (10 bps)</p>', unsafe_allow_html=True)
            b1, b2, b3, b4 = st.columns(4)
            b1.metric("Retorno Algo",  f"{bt_res['total_r']:.1f}%")
            b2.metric("Buy & Hold",    f"{bt_res['bh_r']:.1f}%")
            b3.metric("Max Drawdown",  f"{bt_res['max_dd']:.1f}%",  delta_color="inverse")
            b4.metric("Win Rate",      f"{bt_res['win_rate']:.1f}%")
            b5, b6, b7, b8 = st.columns(4)
            b5.metric("Sortino",        f"{bt_res['sortino']:.2f}")
            b6.metric("Calmar",         f"{bt_res['calmar']:.2f}")
            b7.metric("Profit Factor",  f"{bt_res['profit_factor']:.2f}")
            b8.metric("Trades",         f"{bt_res['trades']}")

            # Equity Curve
            curve  = bt_res["curve"]
            fig_eq = go.Figure()
            fig_eq.add_trace(go.Scatter(x=curve.index, y=curve["Equity"], mode="lines",
                                        line=dict(color="#10b981", width=1.5), name="Algoritmo"))
            fig_eq.add_trace(go.Scatter(x=curve.index, y=curve["BH_Eq"], mode="lines",
                                        line=dict(color="#a1a1aa", width=1, dash="dot"), name="Buy & Hold"))
            fig_eq.update_layout(height=210, margin=dict(l=0,r=0,t=8,b=0),
                                  paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                  font=dict(family="Inter", color="#a1a1aa", size=9),
                                  legend=dict(orientation="h", yanchor="bottom", y=1.01,
                                              font_size=9, bgcolor="rgba(0,0,0,0)"))
            fig_eq.update_xaxes(showgrid=True, gridcolor="#27272a")
            fig_eq.update_yaxes(showgrid=True, gridcolor="#27272a")
            st.plotly_chart(fig_eq, use_container_width=True, config={"displayModeBar": False})

            # Drawdown
            dd_s   = bt_res["drawdown"]
            fig_dd = go.Figure()
            fig_dd.add_trace(go.Scatter(x=dd_s.index, y=dd_s.values * 100, mode="lines",
                                         fill="tozeroy", line=dict(color="#f43f5e", width=1),
                                         fillcolor="rgba(244,63,94,.1)"))
            fig_dd.update_layout(height=110, margin=dict(l=0,r=0,t=4,b=0),
                                  paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                  font=dict(family="Inter", color="#a1a1aa", size=9), showlegend=False)
            fig_dd.update_xaxes(showgrid=True, gridcolor="#27272a")
            fig_dd.update_yaxes(showgrid=True, gridcolor="#27272a", title_text="DD%")
            st.plotly_chart(fig_dd, use_container_width=True, config={"displayModeBar": False})

        with bc2:
            st.markdown('<p class="sec-hdr">MÚLTIPLOS FUNDAMENTALISTAS</p>', unsafe_allow_html=True)
            if fund:
                pct_keys = {"Dividend Yield","Margem EBITDA","Margem Líquida","ROE","ROA"}
                for k, v in fund.items():
                    if k in ("Setor","País"):
                        disp = str(v)
                    elif k == "Market Cap" and isinstance(v, (int, float)) and v:
                        disp = f"R$ {v/1e9:.2f}B"
                    elif k == "Receita TTM" and isinstance(v, (int, float)) and v:
                        disp = f"R$ {v/1e9:.2f}B"
                    elif k in pct_keys and isinstance(v, float) and v:
                        disp = f"{v*100:.2f}%"
                    else:
                        disp = str(v) if v and v != "N/A" else "—"
                    st.markdown(f"""
                    <div class="fund-row">
                        <span class="fund-k">{k}</span>
                        <span class="fund-v">{disp}</span>
                    </div>""", unsafe_allow_html=True)
            else:
                st.info("Múltiplos indisponíveis para índices e ETFs.")

    # ── Tab 6: Inteligência Artificial ────────────────────────────────────────
    with t6:
        st.markdown('<p class="sec-hdr">MOTOR ANALÍTICO — LLAMA 3.1 VIA GROQ</p>', unsafe_allow_html=True)

        ai_c1, ai_c2 = st.columns([4, 1])
        with ai_c1:
            persona = st.radio(
                "Enfoque",
                ["Risco & Valuation", "Estratégia Macro", "Quant & Volatilidade"],
                horizontal=True, label_visibility="collapsed",
            )
        with ai_c2:
            if st.button("🗑 Limpar", use_container_width=True):
                st.session_state.messages = []
                st.rerun()

        ai_ctx = build_ai_context(
            ticker, ultima, fibo, mc_stats, bt_res, saz,
            var_d, kelly, regime, fund, ann_ret, sharpe, sortino, calmar,
        )

        # ── Chat — padrão sem st.rerun() após submit ───────────────────────────
        chat_box = st.container(height=420)
        with chat_box:
            if not st.session_state.messages:
                st.markdown(f"""
                <div style="display:flex;justify-content:center;align-items:center;
                            height:200px;flex-direction:column;gap:8px;">
                    <svg width="30" height="30" viewBox="0 0 24 24" fill="none"
                         stroke="#27272a" stroke-width="1.5">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                    </svg>
                    <p style="color:#3f3f46;font-size:.83rem;">
                        Faça uma pergunta sobre {ticker}
                    </p>
                </div>""", unsafe_allow_html=True)
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        if prompt := st.chat_input(f"Ex: Avalie risco de {ticker} com base no VaR e Kelly atual..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_box:
                with st.chat_message("user"):
                    st.markdown(prompt)
                with st.chat_message("assistant"):
                    with st.spinner("Compilando matriz quantamental..."):
                        reply = generate_ai_response(prompt, ai_ctx, api_key, persona)
                    st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()