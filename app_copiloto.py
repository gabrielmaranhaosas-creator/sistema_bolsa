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

# ==============================================================================
# 1. CONFIGURAÇÃO DE INFRAESTRUTURA DE UI (FRONT-END INSTITUCIONAL)
# ==============================================================================
st.set_page_config(
    page_title="Copiloto Financeiro IA | Oráculo Quantamental V11.0", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Estilização Global CSS para Dark-Mode Premium - Padrão Bloomberg Terminal
st.markdown("""
<style>
    .stMetric { background-color: #0f172a; padding: 20px; border-radius: 10px; border: 1px solid #1e293b; border-left: 5px solid #38bdf8; box-shadow: 0 4px 6px rgba(0,0,0,0.3);}
    .stMetric label { color: #94a3b8 !important; font-weight: 600; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px;}
    .stMetric div { color: #f8fafc !important; font-weight: 800; }
    .css-1d391kg { background-color: #020617; }
    h1, h2, h3, h4 { color: #f8fafc; font-family: 'Helvetica Neue', sans-serif; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: 2px solid #1e293b; }
    .stTabs [data-baseweb="tab"] { background-color: #0f172a; border-radius: 6px 6px 0px 0px; padding: 12px 24px; border: 1px solid #1e293b; border-bottom: none; transition: all 0.3s ease;}
    .stTabs [aria-selected="true"] { background-color: #38bdf8; color: #020617 !important; font-weight: 900; }
    .stButton>button { background-color: #38bdf8; color: #020617; font-weight: bold; border-radius: 6px; border: none; padding: 10px 20px; transition: all 0.3s; }
    .stButton>button:hover { background-color: #0ea5e9; color: #ffffff; box-shadow: 0 0 15px rgba(56, 189, 248, 0.4); }
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# ==============================================================================
# 2. BASE DE DADOS MACROECONÔMICA GLOBAL (KNOWLEDGE BASE V11.0)
# ==============================================================================
GLOBAL_MACRO_CONTEXT = """
[CENÁRIO MACROECONÔMICO E GEOPOLÍTICO GLOBAL - V11.0]
- BRASIL (COPOM): Taxa Selic mantida em 14.50% ao ano, configurando um dos maiores juros reais do planeta. Este cenário restritivo asfixia o varejo, alavanca a dívida das empresas de construção e atrai massivamente o capital para a Renda Fixa (CDI). A curva DI Futuro (Jan/31 a 13.36%) precifica risco fiscal elevado (descontrole de gastos públicos). A desancoragem do IPCA (5.04% Focus) anula qualquer chance de corte de juros a curto prazo.
- ESTADOS UNIDOS (FED): Federal Reserve mantém Fed Funds Rate no patamar de 3.50% - 3.75%. O Core CPI (inflação núcleo) cravado em 2.8% demonstra uma inflação de serviços rígida e resistente. O Dólar (DXY) fortalecido drena o capital de risco dos países emergentes, impactando a bolsa brasileira diretamente. O mercado de Treasuries (títulos de 10 anos) suga a liquidez de ações de dividendos.
- EUROPA (BCE): Zona do Euro enfrenta estagnação econômica, liderada pela recessão industrial da Alemanha. O BCE encontra dificuldades entre cortar juros para salvar o crescimento ou mantê-los para combater a inflação fragmentada.
- CHINA (PBoC): Crise imobiliária sistêmica (pós-Evergrande/Country Garden) sem resolução. Os estímulos monetários do Banco do Povo da China têm sido insuficientes para reativar o consumo interno e a construção civil, o que derruba a demanda global por aço e minério de ferro.
- GEOPOLÍTICA DE ENERGIA E LOGÍSTICA: O bloqueio persistente do Estreito de Ormuz pelo Irã e os ataques no Mar Vermelho (Canal de Suez) forçaram frotas globais a contornarem o Cabo da Boa Esperança. Resultados: fretes marítimos multiplicados em até 400%, rupturas na cadeia de suprimentos e o petróleo Brent negociado com prêmio de guerra (+25%). Isso cria um cenário de "estagflação" iminente (inflação de custos + baixo crescimento).

[MATRIZ CORPORATIVA E SETORIAL - MAPEAMENTO PROFUNDO]
- SETOR DE ÓLEO E GÁS (PETR4, PRIO3, ENAT3): Beneficiárias diretas e absolutas do caos geopolítico no Oriente Médio. Com o Brent sustentado acima de USD 70 e o Dólar fortalecido, estas empresas geram fluxo de caixa trilionário. Funcionam como hedge natural na carteira.
- SETOR DE MINERAÇÃO E SIDERURGIA (VALE3, GGBR4, CSNA3, USIM5): Maiores vítimas da desaceleração da China. Suas margens estão sendo duplamente espremidas: queda no preço de venda do minério de ferro/aço e aumento brutal no custo logístico de extração (diesel mais caro devido à alta do petróleo).
- SETOR DE PAPEL E CELULOSE (SUZB3, KLBN11): Exportadoras natas. O dólar alto favorece as receitas e protege o investidor contra a desvalorização do Real. Contudo, o bloqueio logístico no Mar Vermelho e a escassez de contêineres globais impõem desafios logísticos perigosos, podendo impactar o faturamento trimestral.
- SETOR BANCÁRIO (ITUB4, BBDC4, BBAS3, SANB11): ITUB4 opera como bunker (lucro recorde, ROE alto, inadimplência mínima sob controle em 1.9%). O BBAS3 foi severamente penalizado pela crise climática e inadimplência no agronegócio (provisionamento PDD recorde). O BBDC4 tenta turnaround em meio à deterioração do crédito pessoa física.
- SETOR DE UTILITIES / ELÉTRICAS (ELET3, TAEE11, EQTL3, TRPL4, EGIE3): Setor de proteção (defensivo) fundamental. Receitas 100% previsíveis atreladas à inflação (IGP-M/IPCA). Blindadas contra as oscilações violentas da Selic. 
- SETOR DE SANEAMENTO (SBSP3, CSMG3): Foco na eficiência pós-privatização. A principal métrica de risco é o peso da dívida, já que possuem alto passivo indexado ao CDI, IPCA e Dólar. Juro a 14.50% eleva o serviço da dívida.
- CONSTRUÇÃO E IMOBILIÁRIO (CYRE3, EZTC3, MRVE3): Em colapso. O custo do crédito imobiliário trava a venda de imóveis. Apenas o segmento de luxo/alta renda (JHSF3) demonstra alguma resiliência estatística.
- VAREJO E CONSUMO DOMÉSTICO (MGLU3, LREN3, BHIA3, CRFB3, ASAI3): Setor asfixiado pela macroeconomia. Inversamente correlacionados à curva de juros DI. O alto custo da dívida corrói os balanços operacionais, gerando queima de caixa constante.
- AGRONEGÓCIO (SLCE3, SMTO3, TTEN3): O setor sofre as consequências diretas das anomalias climáticas globais (El Niño/La Niña), quebra de safras e os juros elevados do financiamento via Plano Safra. 
- TECNOLOGIA GLOBAL / MAGNIFICENT 7 (NVDA, AAPL, MSFT, META, GOOGL): O capital global busca segurança institucional e hipercrescimento no monopólio de Inteligência Artificial. Elas descolam da macroeconomia de commodities e operam como "Estados Nação" independentes.
- FUNDOS IMOBILIÁRIOS (FIIS): Os fundos de papel (CRI) indexados ao CDI/IPCA distribuem dividendos irreais em razão da Selic em 14.50%. Em contrapartida, os fundos de tijolo (HGLG11, KNRI11) sofrem desvalorização patrimonial aguda devido à alta taxa de desconto (juro livre de risco) aplicada aos seus fluxos futuros.
"""

# ==============================================================================
# 3. DICIONÁRIO INSTITUCIONAL DE ATIVOS (CATÁLOGO GLOBAL)
# ==============================================================================
CATALOGO_INSTITUCIONAL = {
    # ÍNDICES E ETFS GLOBAIS
    "Índice Bovespa (BVSP)": "^BVSP", "S&P 500 EUA (SPY)": "SPY", "Nasdaq 100 EUA (QQQ)": "QQQ", 
    "Ibovespa ETF (BOVA11)": "BOVA11.SA", "S&P 500 B3 (IVVB11)": "IVVB11.SA", "Índice Small Caps (SMAL11)": "SMAL11.SA",
    "Ouro Físico (GLD)": "GLD", "Petróleo Brent ETF (BNO)": "BNO", "IFIX - Fundos Imobiliários": "^IFIX",
    
    # COMMODITIES, ÓLEO E GÁS, MINERAÇÃO
    "Petrobras PN (PETR4)": "PETR4.SA", "Petrobras ON (PETR3)": "PETR3.SA", "Vale S.A (VALE3)": "VALE3.SA", 
    "Gerdau Metalúrgica (GGBR4)": "GGBR4.SA", "CSN Siderurgia (CSNA3)": "CSNA3.SA", "Usiminas (USIM5)": "USIM5.SA",
    "Prio Petróleo (PRIO3)": "PRIO3.SA", "Enauta Petróleo (ENAT3)": "ENAT3.SA", "Suzano Celulose (SUZB3)": "SUZB3.SA", "Klabin (KLBN11)": "KLBN11.SA",
    
    # AGRONEGÓCIO & PROTEÍNAS
    "SLC Agrícola (SLCE3)": "SLCE3.SA", "São Martinho (SMTO3)": "SMTO3.SA", "JBS (JBSS3)": "JBSS3.SA", 
    "BRF Foods (BRFS3)": "BRFS3.SA", "Marfrig (MRFG3)": "MRFG3.SA",
    
    # SETOR FINANCEIRO & SEGURADORAS
    "Itaú Unibanco (ITUB4)": "ITUB4.SA", "Banco do Brasil (BBAS3)": "BBAS3.SA", "Bradesco PN (BBDC4)": "BBDC4.SA", 
    "Santander Brasil (SANB11)": "SANB11.SA", "BTG Pactual (BPAC11)": "BPAC11.SA", "B3 S.A. (B3SA3)": "B3SA3.SA", 
    "BB Seguridade (BBSE3)": "BBSE3.SA", "Porto Seguro (PSSA3)": "PSSA3.SA",
    
    # UTILITIES (ELÉTRICAS E SANEAMENTO)
    "Eletrobras ON (ELET3)": "ELET3.SA", "Taesa (TAEE11)": "TAEE11.SA", "Equatorial Energia (EQTL3)": "EQTL3.SA", 
    "Isa Cteep (TRPL4)": "TRPL4.SA", "Engie Brasil (EGIE3)": "EGIE3.SA", "Copel (CPLE6)": "CPLE6.SA",
    "Sabesp (SBSP3)": "SBSP3.SA", "Copasa (CSMG3)": "CSMG3.SA",
    
    # VAREJO, SAÚDE, LOGÍSTICA E CONSUMO DOMÉSTICO
    "Weg Equipamentos (WEGE3)": "WEGE3.SA", "Localiza (RENT3)": "RENT3.SA", "Magazine Luiza (MGLU3)": "MGLU3.SA", 
    "Lojas Renner (LREN3)": "LREN3.SA", "Assaí Atacadista (ASAI3)": "ASAI3.SA", "Carrefour (CRFB3)": "CRFB3.SA",
    "Rede D'Or (RDOR3)": "RDOR3.SA", "Hapvida (HAPV3)": "HAPV3.SA", "Rumo Logística (RAIL3)": "RAIL3.SA",
    
    # CONSTRUÇÃO E FUNDOS IMOBILIÁRIOS (FIIS)
    "Cyrela (CYRE3)": "CYRE3.SA", "JHSF (JHSF3)": "JHSF3.SA", "MRV Engenharia (MRVE3)": "MRVE3.SA",
    "Maxi Renda FII (MXRF11)": "MXRF11.SA", "CSHG Logística (HGLG11)": "HGLG11.SA", "Kinea Renda (KNRI11)": "KNRI11.SA",
    
    # TECNOLOGIA E MERCADO INTERNACIONAL (EUA)
    "Nvidia Corp (NVDA)": "NVDA", "Apple Inc (AAPL)": "AAPL", "Microsoft (MSFT)": "MSFT", 
    "Alphabet / Google (GOOGL)": "GOOGL", "Amazon (AMZN)": "AMZN", "Tesla Inc (TSLA)": "TSLA", 
    "TSMC Semicondutores (TSM)": "TSM", "Mercado Livre (MELI)": "MELI", "Palantir (PLTR)": "PLTR",
    
    # MOEDAS E CRIPTOATIVOS
    "Bitcoin (BTC-USD)": "BTC-USD", "Ethereum (ETH-USD)": "ETH-USD", "Solana (SOL-USD)": "SOL-USD", 
    "Dólar / Real (BRL=X)": "BRL=X", "Euro / Real (EURBRL=X)": "EURBRL=X",
    
    # PESQUISA ABERTA
    "Pesquisa Manual de Ticker": "OUTRO"
}

# ==============================================================================
# 4. MÓDULO DE INGESTÃO DE DADOS (MARKET DATA & FUNDAMENTOS)
# ==============================================================================
@st.cache_data(ttl=600)
def fetch_market_data(ticker: str, period: str = "2y") -> Optional[pd.DataFrame]:
    """
    Motor de extração robusta de série temporal com normalização de Timezone.
    Exige no mínimo 50 pregões de liquidez para validar os cálculos quantitativos pesados.
    """
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
    """
    Motor de extração de indicadores fundamentalistas (P/L, Div Yield, Margens, etc) via API.
    Isola erros quando fundos ou índices não possuem DRE estruturado.
    """
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

# ==============================================================================
# 5. MOTOR MATEMÁTICO INSTITUCIONAL (INDICADORES AVANÇADOS)
# ==============================================================================
def calculate_advanced_indicators(df: pd.DataFrame, ma_window: int = 20) -> Tuple[pd.DataFrame, Dict[str, float], float, float]:
    """
    Computa a matriz quantitativa extrema:
    - SMA, EMA 9/21
    - Bandas de Bollinger, ATR, RSI, MACD, Estocástico
    - Nuvem de Ichimoku (Kumo)
    - On-Balance Volume (OBV) e Money Flow Index (MFI)
    - Retornos Anualizados e Índice de Sharpe
    - Retrações de Fibonacci
    """
    df_calc = df.copy()
    close = df_calc['Close']
    high = df_calc['High']
    low = df_calc['Low']
    volume = df_calc['Volume']
    df_calc['Close_Price'] = close
    
    # --- MÉDIAS DIRECIONAIS ---
    df_calc['SMA'] = close.rolling(window=ma_window).mean()
    df_calc['EMA_9'] = close.ewm(span=9, adjust=False).mean()
    df_calc['EMA_21'] = close.ewm(span=21, adjust=False).mean()
    
    # --- BANDAS DE BOLLINGER (Volatilidade) ---
    std_dev = close.rolling(window=ma_window).std()
    df_calc['BB_Upper'] = df_calc['SMA'] + (std_dev * 2)
    df_calc['BB_Lower'] = df_calc['SMA'] - (std_dev * 2)
    df_calc['BB_Width'] = (df_calc['BB_Upper'] - df_calc['BB_Lower']) / df_calc['SMA']
    
    # --- RSI 14 (Força Relativa) ---
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df_calc['RSI'] = 100 - (100 / (1 + (gain / loss)))
    
    # --- MACD (Momentum) ---
    df_calc['MACD'] = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
    df_calc['Signal_Line'] = df_calc['MACD'].ewm(span=9, adjust=False).mean()
    df_calc['MACD_Hist'] = df_calc['MACD'] - df_calc['Signal_Line']
    
    # --- ATR 14 (Volatilidade Absoluta e Risco) ---
    tr = pd.concat([high - low, abs(high - close.shift(1)), abs(low - close.shift(1))], axis=1).max(axis=1)
    df_calc['ATR'] = tr.rolling(window=14).mean()
    
    # --- ESTOCÁSTICO 14,3 ---
    lowest_low = low.rolling(window=14).min()
    highest_high = high.rolling(window=14).max()
    df_calc['Stoch_K'] = 100 * ((close - lowest_low) / (highest_high - lowest_low))
    
    # --- ON-BALANCE VOLUME (OBV) ---
    obv = np.where(close > close.shift(1), volume, np.where(close < close.shift(1), -volume, 0))
    df_calc['OBV'] = pd.Series(obv, index=df_calc.index).cumsum()
    
    # --- MONEY FLOW INDEX (MFI 14) ---
    typical_price = (high + low + close) / 3
    raw_money_flow = typical_price * volume
    positive_flow = np.where(typical_price > typical_price.shift(1), raw_money_flow, 0)
    negative_flow = np.where(typical_price < typical_price.shift(1), raw_money_flow, 0)
    positive_mf = pd.Series(positive_flow, index=df_calc.index).rolling(window=14).sum()
    negative_mf = pd.Series(negative_flow, index=df_calc.index).rolling(window=14).sum()
    mfi_ratio = positive_mf / negative_mf
    df_calc['MFI'] = 100 - (100 / (1 + mfi_ratio))
    
    # --- NUVEM DE ICHIMOKU (Kumo) ---
    nine_period_high = high.rolling(window=9).max()
    nine_period_low = low.rolling(window=9).min()
    df_calc['Tenkan_sen'] = (nine_period_high + nine_period_low) / 2
    period26_high = high.rolling(window=26).max()
    period26_low = low.rolling(window=26).min()
    df_calc['Kijun_sen'] = (period26_high + period26_low) / 2
    df_calc['Senkou_Span_A'] = ((df_calc['Tenkan_sen'] + df_calc['Kijun_sen']) / 2).shift(26)
    period52_high = high.rolling(window=52).max()
    period52_low = low.rolling(window=52).min()
    df_calc['Senkou_Span_B'] = ((period52_high + period52_low) / 2).shift(26)
    
    # --- RETRAÇÕES DE FIBONACCI (Base Anual - 252 sessões) ---
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

    # --- PERFORMANCE E SHARPE RATIO ---
    daily_returns = close.pct_change()
    ann_return = daily_returns.mean() * 252 * 100 
    ann_vol = daily_returns.std() * np.sqrt(252) * 100
    risk_free_rate = 14.50 
    sharpe_ratio = (ann_return - risk_free_rate) / ann_vol if ann_vol > 0 else 0

    return df_calc, fibo_levels, ann_return, sharpe_ratio

def plot_master_chart(df: pd.DataFrame, ticker: str, fibo: Dict[str, float]) -> go.Figure:
    """Renderizador Gráfico Master Class (Subplots Complexos)."""
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.04, 
                        subplot_titles=(f'Price Action & Bollinger', 'Fluxo Institucional (MFI & OBV Normalizado)', 'Momentum (MACD)'),
                        row_width=[0.2, 0.2, 0.6])
    
    # ROW 1: Candlestick, Bollinger
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close_Price'], name='Preço'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], mode='lines', line=dict(color='#eab308', width=1.5), name='SMA'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], mode='lines', line=dict(color='rgba(255, 255, 255, 0.2)', width=1, dash='dash'), name='Bollinger Sup'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], mode='lines', line=dict(color='rgba(255, 255, 255, 0.2)', width=1, dash='dash'), name='Bollinger Inf', fill='tonexty', fillcolor='rgba(255, 255, 255, 0.05)'), row=1, col=1)
    
    # Fibo Overlays
    fibo_colors = ['#ef4444', '#f97316', '#3b82f6', '#22c55e', '#a855f7']
    for (level_name, price), color in zip(fibo.items(), fibo_colors):
        fig.add_hline(y=price, line_dash="dot", line_color=color, line_width=1, annotation_text=level_name, annotation_position="top right", row=1, col=1)

    # ROW 2: MFI (Money Flow Index)
    fig.add_trace(go.Scatter(x=df.index, y=df['MFI'], mode='lines', line=dict(color='#8b5cf6', width=2), name='MFI (Fluxo de Dinheiro)'), row=2, col=1)
    fig.add_hline(y=80, line_dash="dot", line_color="red", row=2, col=1)
    fig.add_hline(y=20, line_dash="dot", line_color="green", row=2, col=1)

    # ROW 3: MACD
    colors_macd = ['#22c55e' if val >= 0 else '#ef4444' for val in df['MACD_Hist']]
    fig.add_trace(go.Bar(x=df.index, y=df['MACD_Hist'], marker_color=colors_macd, name='Histograma'), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], mode='lines', line=dict(color='#3b82f6', width=1.5), name='MACD'), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Signal_Line'], mode='lines', line=dict(color='#f97316', width=1.5), name='Sinal'), row=3, col=1)
    
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=850, 
                      margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor="#020617", plot_bgcolor="#0f172a",
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    return fig

# ==============================================================================
# 6. MOTOR DE BACKTESTING VETORIZADO (NOVO)
# ==============================================================================
def run_vectorized_backtest(df: pd.DataFrame, fast_period: int = 9, slow_period: int = 21) -> Dict[str, Any]:
    """
    Roda um backtest algorítmico da estratégia de Cruzamento de Médias Exponenciais.
    Avalia a aderência do ativo à tendência pura no histórico carregado.
    """
    bt_df = df.copy()
    bt_df['EMA_Fast'] = bt_df['Close_Price'].ewm(span=fast_period, adjust=False).mean()
    bt_df['EMA_Slow'] = bt_df['Close_Price'].ewm(span=slow_period, adjust=False).mean()
    
    # Geração de Sinais Lógicos (1 = Comprado, 0 = Fora)
    bt_df['Signal'] = 0
    bt_df.loc[bt_df['EMA_Fast'] > bt_df['EMA_Slow'], 'Signal'] = 1
    
    # Calcula retornos diários
    bt_df['Daily_Return'] = bt_df['Close_Price'].pct_change()
    
    # Aplica o sinal deslocado em 1 dia (para evitar look-ahead bias - compra no fechamento, ganha no dia seguinte)
    bt_df['Strategy_Return'] = bt_df['Signal'].shift(1) * bt_df['Daily_Return']
    
    # Curvas de Capital Acumuladas
    bt_df['Equity_Curve'] = (1 + bt_df['Strategy_Return'].fillna(0)).cumprod()
    bt_df['Buy_Hold_Curve'] = (1 + bt_df['Daily_Return'].fillna(0)).cumprod()
    
    # Métricas de Desempenho
    total_strat_return = (bt_df['Equity_Curve'].iloc[-1] - 1) * 100
    total_bh_return = (bt_df['Buy_Hold_Curve'].iloc[-1] - 1) * 100
    
    # Análise de Drawdown da Estratégia
    rolling_max = bt_df['Equity_Curve'].cummax()
    drawdown = (bt_df['Equity_Curve'] - rolling_max) / rolling_max
    max_drawdown = drawdown.min() * 100
    
    # Contagem de Trades e Taxa de Acerto (Win Rate)
    bt_df['Trade_Change'] = bt_df['Signal'].diff()
    trades = bt_df[bt_df['Trade_Change'] == 1] # Pontos de Entrada
    
    # Estimativa simples de Win Rate baseada em retornos positivos nos dias comprados
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
# 7. MOTOR DE SAZONALIDADE HISTÓRICA (NOVO)
# ==============================================================================
def calculate_seasonality(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula o retorno médio percentual do ativo para cada mês do ano (Janeiro a Dezembro)."""
    df_saz = df.copy()
    # Resample para mensal
    monthly = df_saz['Close_Price'].resample('M').last()
    monthly_ret = monthly.pct_change() * 100
    
    # Agrupa por mês do ano (1 a 12)
    seasonality = monthly_ret.groupby(monthly_ret.index.month).mean().to_frame(name='Avg_Return_Pct')
    
    # Converte índices numéricos para nomes curtos
    meses = {1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun', 
             7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'}
    seasonality.index = seasonality.index.map(meses)
    
    return seasonality

def plot_seasonality(seasonality_df: pd.DataFrame, ticker: str) -> go.Figure:
    """Gera o gráfico de barras da sazonalidade."""
    colors = ['#22c55e' if val >= 0 else '#ef4444' for val in seasonality_df['Avg_Return_Pct']]
    fig = go.Figure(data=[go.Bar(
        x=seasonality_df.index, 
        y=seasonality_df['Avg_Return_Pct'],
        marker_color=colors,
        text=[f"{val:.2f}%" for val in seasonality_df['Avg_Return_Pct']],
        textposition='auto'
    )])
    fig.update_layout(title=f"Mapa de Sazonalidade Histórica Mensal: {ticker}",
                      yaxis_title="Retorno Médio (%)", template="plotly_dark", 
                      height=400, paper_bgcolor="#020617", plot_bgcolor="#0f172a")
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
        fig.add_trace(go.Scatter(y=price_paths[:, i], mode='lines', line=dict(color='rgba(56, 189, 248, 0.03)', width=1), showlegend=False))
    
    fig.add_trace(go.Scatter(y=price_paths.mean(axis=1), mode='lines', line=dict(color='#eab308', width=3), name='Caminho Médio Esperado'))
    fig.update_layout(title=f"Motor Estocástico: {simulations} Caminhos Aleatórios ({days_ahead} pregões)",
                      yaxis_title="Projeção de Preço (R$ / USD)", template="plotly_dark", height=450, paper_bgcolor="#020617", plot_bgcolor="#0f172a")
    return price_paths, fig, expected_price

# ==============================================================================
# 9. MOTOR DE PRECIFICAÇÃO DE OPÇÕES (BLACK-SCHOLES)
# ==============================================================================
def norm_cdf(x: float) -> float:
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

def black_scholes_pricing(S: float, K: float, T: float, r: float, sigma: float) -> Tuple[float, float, float]:
    if T <= 0 or sigma <= 0: return 0.0, 0.0, 0.0
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    call_price = S * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)
    put_price = K * math.exp(-r * T) * norm_cdf(-d2) - S * norm_cdf(-d1)
    return call_price, put_price, norm_cdf(d1)

# ==============================================================================
# 10. O ORÁCULO QUANTAMENTAL (MOTOR GENERATIVO GROQ CLOUD MULTI-PERSONA)
# ==============================================================================
def generate_ai_response(prompt: str, context_data: str, api_key: str, persona: str) -> str:
    """
    O cérebro absoluto do sistema. Processa o vasto Dossiê de Dados (Backtest, Monte Carlo, Fibo, Macro)
    e adota a Persona Institucional solicitada pelo usuário para responder.
    """
    try:
        client = Groq(api_key=api_key)
        
        # Injeção dinâmica de comportamento baseada na escolha da interface
        if persona == "Estrategista Macro (Foco em Juros e Geopolítica)":
            foco = "Sua prioridade máxima é cruzar o preço do ativo com a taxa Selic (14.50%), inflação e crises mundiais. Explique o cenário sistêmico."
        elif persona == "Quant Trader (Foco em Backtest e Volatilidade)":
            foco = "Sua prioridade máxima é analisar o Backtest da estratégia EMA, os níveis de Fibonacci, o Monte Carlo e a volatilidade ATR. Despreze um pouco a macroeconomia e foque na matemática gráfica."
        else:
            foco = "Sua prioridade é analisar os fundamentos, o Balanço (P/L, ROE) e avaliar o risco paramétrico de Position Sizing."
        
        system_instruction = f"""Você é o 'Oráculo Quantamental V11.0', o Cérebro Neural de uma Tesouraria Institucional de Elite.
        
        DIRETRIZES DA PERSONA ATUAL:
        {foco}
        
        REGRAS INQUEBRÁVEIS:
        1. Você acaba de receber um dossiê monumental de dados. NUNCA invente números. Use exatamente os dados estatísticos que lhe foram fornecidos no Payload.
        2. Aja como um gestor cínico, impiedoso com falsas esperanças e brutalmente analítico.
        3. FORMATAÇÃO: É PROIBIDO o uso de LaTeX no texto. Use EXCLUSIVAMENTE 'R$' ou 'USD'. Utilize Bullet Points massivamente para criar relatórios táticos de fácil leitura.
        4. O operador depende da sua inteligência para alocar milhões. Seja preciso, denso e cite a matriz estatística.
        """
        
        payload = f"{GLOBAL_MACRO_CONTEXT}\n\n[MATRIZ ALGORÍTMICA ABSOLUTA DO ATIVO (BACKTEST, ESTOCÁSTICO, FUNDAMENTOS)]\n{context_data}"
        user_message = f"[DATA LAKE INJETADO]\n{payload}\n\n[PERGUNTA/COMANDO DO OPERADOR DA MESA]\n{prompt}"
        
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": user_message}],
            model="llama-3.1-8b-instant",
            temperature=0.35, # Mantém coerência matemática sem perder capacidade criativa de cruzar dados dispersos
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"ALERTA CRÍTICO: Colapso na sinapse neural (API Groq). Verifique chave e conexão. Erro: {e}"

# ==============================================================================
# 11. THREAD PRINCIPAL DO TERMINAL (DASHBOARD & INTERFACE V11.0)
# ==============================================================================
def main():
    st.title("Copiloto Financeiro IA | Oráculo Quantamental V11.0")
    st.markdown("---")

    # BARRA LATERAL (CONTROLE DE MISSÃO)
    with st.sidebar:
        st.header("🗄️ Controle de Missão")
        selecao_ativo = st.selectbox("Selecione o Ativo Global:", list(CATALOGO_INSTITUCIONAL.keys()))
        
        if selecao_ativo == "Pesquisa Manual de Ticker":
            ticker = st.text_input("Ticker Yahoo Finance (Ex: BBDC4.SA, TQQQ):", value="PETR4.SA").upper()
        else:
            ticker = CATALOGO_INSTITUCIONAL[selecao_ativo]
            
        col_t1, col_t2 = st.columns(2)
        with col_t1: period = st.selectbox("Range Histórico", ["6mo", "1y", "2y", "5y", "max"], index=2)
        with col_t2: ma_window = st.number_input("SMA Base", min_value=5, max_value=200, value=20)
        
        st.markdown("---")
        # Injeção Direta da API Key 
        api_key = "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"
        st.success("🟢 SISTEMA CORE V11.0: ONLINE\n\n🔹 Backtest Engine: Operacional\n🔹 Sazonalidade: Operacional\n🔹 Oráculo Multi-Persona: Ativo")

    # INGESTÃO DE DADOS ASSÍNCRONA (CACHED)
    df_raw = fetch_market_data(ticker, period)
    fundament_data = fetch_fundamental_data(ticker)
    
    contexto_invisivel = "Pipeline Vazio."
    
    if df_raw is not None:
        # PIPELINE MATEMÁTICO PESADO
        df_processed, fibo_levels, ann_return, sharpe_ratio = calculate_advanced_indicators(df_raw, ma_window)
        mc_paths, mc_fig, mc_expected_price = run_monte_carlo_simulation(df_processed, days_ahead=30, simulations=100)
        backtest_results = run_vectorized_backtest(df_processed, fast_period=9, slow_period=21)
        seasonality_df = calculate_seasonality(df_processed)
        
        # FOTOGRAFIA DO MILISSEGUNDO ATUAL
        ultima = df_processed.iloc[-1]
        c_price, c_sma, c_rsi, c_macd, c_sig = ultima['Close_Price'], ultima['SMA'], ultima['RSI'], ultima['MACD'], ultima['Signal_Line']
        c_atr, c_bbw, c_stoch, c_obv, c_mfi = ultima['ATR'], ultima['BB_Width'], ultima['Stoch_K'], ultima['OBV'], ultima['MFI']
        
        # TRADUÇÕES LÓGICAS PARA O ORÁCULO
        trend = "ALTA TÉCNICA" if c_price > c_sma else "PRESSÃO VENDEDORA"
        if pd.isna(c_rsi): rsi_txt = "Falta dados"
        elif c_rsi > 70: rsi_txt = f"{c_rsi:.1f} (SOBRECOMPRADO)"
        elif c_rsi < 30: rsi_txt = f"{c_rsi:.1f} (SOBREVENDIDO)"
        else: rsi_txt = f"{c_rsi:.1f} (NEUTRO)"
        
        # FORMATAÇÃO DO DOSSIÊ PARA A IA (O DATA LAKE INVISÍVEL)
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
        
        [NÍVEIS ÁUREOS DE FIBONACCI]
        {fibo_str}
        
        [MONTE CARLO RANDOM WALK (Próximos 30 dias)]
        - Preço Médio Esperado (Média 100 Simulações): R$ {mc_expected_price:.2f}
        
        [BACKTEST ESTRATÉGIA CRUZAMENTO EMA 9 vs 21]
        - Retorno Total da Estratégia: {backtest_results['total_return_pct']:.2f}% (vs Buy & Hold: {backtest_results['buy_hold_pct']:.2f}%)
        - Max Drawdown (Risco): {backtest_results['max_drawdown_pct']:.2f}%
        - Taxa de Acerto dos Dias Comprados (Win Rate Estimado): {backtest_results['win_rate_pct']:.1f}%
        
        [SAZONALIDADE]
        - Mês Atual ({current_month_str}): Historicamente, o ativo rende em média {saz_atual:.2f}% neste mês.
        
        [BALANÇO FUNDAMENTALISTA (MÚLTIPLOS)]
        {fundamentos_str}
        """

    # -------------------------------------------------------------------------
    # LAYOUT DE 6 ABAS MASTERCLASS
    # -------------------------------------------------------------------------
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Gráfico Institucional", 
        "⚙️ Risco & Black-Scholes", 
        "🎲 Algoritmos & Estatística",
        "🏢 Valuation Contábil",
        "📈 Backtest Estratégico",
        "🧠 ORÁCULO IA (O CÉREBRO)"
    ])

    with tab1: # ABA 1: GRÁFICO 
        if df_raw is not None:
            c1, c2, c3, c4 = st.columns(4)
            delta_pct = ((c_price / df_raw['Close'].iloc[-2]) - 1) * 100 if len(df_raw) > 1 else 0
            c1.metric("Preço Mercado", f"R$ {c_price:.2f}", delta=f"{delta_pct:.2f}%")
            c2.metric("Risco Diário (ATR)", f"R$ {c_atr:.2f}")
            c3.metric("Money Flow (MFI 14)", f"{c_mfi:.1f}")
            c4.metric("Desempenho (Drift)", f"{ann_return:.1f}%", delta=f"Sharpe: {sharpe_ratio:.2f}")
            
            st.markdown("---")
            fig_master = plot_master_chart(df_processed, ticker, fibo_levels)
            st.plotly_chart(fig_master, use_container_width=True)
        else:
            st.error("Erro fatal: Série temporal corrompida ou ticker inexistente.")

    with tab2: # ABA 2: RISCO E OPÇÕES
        if df_raw is not None:
            st.markdown("### Dimensionamento Paramétrico de Exposição (Spot)")
            with st.form("risk_form_v11"):
                c_f1, c_f2 = st.columns(2)
                with c_f1:
                    capital = st.number_input("Capital da Operação (R$)", min_value=0.0, value=250000.0, step=10000.0)
                    risk_pct = st.number_input("Limiar de Risco / Drawdown (%)", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
                with c_f2:
                    entry_price = st.number_input("Alvo de Execução (Compra)", min_value=0.0, value=c_price, step=0.01)
                    stop_loss = st.number_input("Proteção Fixa (Stop Loss)", min_value=0.0, value=c_price - (c_atr * 1.5), step=0.01)
                sub_btn = st.form_submit_button("Gerar Boleta de Risco")

            if sub_btn:
                if stop_loss >= entry_price:
                    st.error("ERRO: Stop Loss deve ser menor que o preço de entrada (Operação Long).")
                else:
                    risk_val = capital * (risk_pct / 100)
                    shares = int(risk_val // (entry_price - stop_loss))
                    st.success("✅ Dimensionamento Autorizado pelo Comitê de Risco.")
                    cr1, cr2, cr3 = st.columns(3)
                    cr1.metric("Lotes Liberados", f"{shares} ações")
                    cr2.metric("Caixa Consumido Bruto", f"R$ {(shares * entry_price):,.2f}")
                    cr3.metric("Perda Estritamente Controlada", f"R$ {risk_val:,.2f}")
            
            st.markdown("---")
            st.markdown("### Precificação Teórica Europeia (Motor Black-Scholes)")
            with st.form("bs_form_v11"):
                cb1, cb2, cb3 = st.columns(3)
                with cb1:
                    bs_spot = st.number_input("Spot Atual", value=c_price, step=0.1)
                    bs_strike = st.number_input("Strike Desejado", value=c_price * 1.05, step=0.1)
                with cb2:
                    bs_days = st.number_input("Dias Vencimento", value=21, min_value=1)
                    bs_rf = st.number_input("Taxa Selic Anual (%)", value=14.50, step=0.10)
                with cb3:
                    vol_estimada = (c_atr / c_price) * math.sqrt(252) * 100
                    bs_vol = st.number_input("Volatilidade Implícita Anual (%)", value=float(vol_estimada), step=1.0)
                bs_submit = st.form_submit_button("Rodar Black-Scholes")
                
            if bs_submit:
                call_p, put_p, call_delta = black_scholes_pricing(bs_spot, bs_strike, bs_days/252.0, bs_rf/100.0, bs_vol/100.0)
                st.success("✅ Cálculo Computacional Efetuado.")
                crr1, crr2, crr3 = st.columns(3)
                crr1.metric("Prêmio CALL (Justo)", f"R$ {call_p:.3f}")
                crr2.metric("Prêmio PUT (Justo)", f"R$ {put_p:.3f}")
                crr3.metric("Delta (Prob. Exercício Call)", f"{call_delta * 100:.1f}%")

    with tab3: # ABA 3: ALGORITMOS (MONTE CARLO E SAZONALIDADE)
        if df_raw is not None:
            c_alg1, c_alg2 = st.columns(2)
            with c_alg1:
                st.markdown("### Mapa de Sazonalidade (Ciclos Históricos)")
                st.markdown("Identifica anomalias de mercado. Mapeia o retorno médio do ativo em cada mês baseado em seu histórico carregado.")
                fig_saz = plot_seasonality(seasonality_df, ticker)
                st.plotly_chart(fig_saz, use_container_width=True)
            with c_alg2:
                st.markdown("### Simulador Random Walk (Monte Carlo)")
                st.markdown("Projeta 100 cenários prováveis para os próximos 30 dias com base na variância e deriva (drift) histórica da série.")
                st.plotly_chart(mc_fig, use_container_width=True)
                st.info(f"O Algoritmo de Monte Carlo estima o preço de convergência em **R$ {mc_expected_price:.2f}**.")

    with tab4: # ABA 4: VALUATION
        st.markdown("### Diagnóstico Contábil de Valuation")
        if fundament_data:
            col_f1, col_f2, col_f3 = st.columns(3)
            col_f1.metric("Market Cap (Tamanho)", f"{fundament_data.get('Market Cap', 'N/A')}")
            col_f1.metric("P/L (Múltiplo de Lucro)", f"{fundament_data.get('P/E Ratio (P/L)', 'N/A')}")
            col_f1.metric("Div. Yield", f"{fundament_data.get('Dividend Yield', 0) * 100 if isinstance(fundament_data.get('Dividend Yield'), (int, float)) else 'N/A'}%")
            
            col_f2.metric("P/VP (Valor Patrimonial)", f"{fundament_data.get('Price to Book (P/VP)', 'N/A')}")
            col_f2.metric("ROE (Eficiência do Capital)", f"{fundament_data.get('ROE (Retorno s/ Patrimônio)', 0) * 100 if isinstance(fundament_data.get('ROE (Retorno s/ Patrimônio)'), (int, float)) else 'N/A'}%")
            col_f2.metric("Margem Líquida", f"{fundament_data.get('Profit Margin', 0) * 100 if isinstance(fundament_data.get('Profit Margin'), (int, float)) else 'N/A'}%")
            
            col_f3.metric("Dívida / Patrimônio Líquido", f"{fundament_data.get('Debt to Equity (Dívida/Patrimônio)', 'N/A')}")
            col_f3.metric("Liquidez Corrente", f"{fundament_data.get('Current Ratio (Liquidez)', 'N/A')}")
            col_f3.metric("Margem EBITDA", f"{fundament_data.get('EBITDA Margin', 0) * 100 if isinstance(fundament_data.get('EBITDA Margin'), (int, float)) else 'N/A'}%")
        else:
            st.warning("Indicadores não mapeados (Comum em Índices, Fundos ou ETFs sintéticos).")

    with tab5: # ABA 5: BACKTEST
        if df_raw is not None:
            st.markdown("### Motor de Backtesting (Cruzamento de EMA 9 vs 21)")
            st.markdown(f"O algoritmo rodou a estratégia de cruzamento em **{len(df_processed)} sessões** de histórico. Resultado abaixo:")
            
            c_bt1, c_bt2, c_bt3, c_bt4 = st.columns(4)
            c_bt1.metric("Retorno da Estratégia", f"{backtest_results['total_return_pct']:.2f}%", help="Capital acumulado comprando no cruzamento de alta e zerando no cruzamento de baixa.")
            c_bt2.metric("Buy & Hold (Para Comparação)", f"{backtest_results['buy_hold_pct']:.2f}%")
            c_bt3.metric("Risco Absoluto (Max Drawdown)", f"{backtest_results['max_drawdown_pct']:.2f}%")
            c_bt4.metric("Taxa de Eficiência (Win Rate)", f"{backtest_results['win_rate_pct']:.1f}%")
            
            # Plot da Curva de Capital (Equity Curve)
            curve_df = backtest_results['curve_df']
            fig_eq = go.Figure()
            fig_eq.add_trace(go.Scatter(x=curve_df.index, y=curve_df['Equity_Curve'], mode='lines', name='Algoritmo (EMA Cross)', line=dict(color='#22c55e', width=2)))
            fig_eq.add_trace(go.Scatter(x=curve_df.index, y=curve_df['Buy_Hold_Curve'], mode='lines', name='Buy & Hold', line=dict(color='#94a3b8', width=1, dash='dot')))
            fig_eq.update_layout(title="Curva de Capital Histórica (Equity Curve)", template="plotly_dark", height=400, paper_bgcolor="#020617", plot_bgcolor="#0f172a")
            st.plotly_chart(fig_eq, use_container_width=True)

    with tab6: # ABA 6: O ORÁCULO IA (O CÉREBRO)
        if df_raw is not None:
            st.markdown("### Oráculo Quantamental: Inteligência Híbrida Llama 3.1")
            st.markdown("O cérebro absorve todas as abas anteriores (Matemática, Valuation, Sazonalidade, Macro e Backtest) em um único dossiê invisível e formula respostas estruturais táticas.")
            
            col_persona, col_btn = st.columns([3, 1])
            with col_persona:
                persona_ia = st.radio("Selecione a Persona / Modo de Raciocínio da IA:", 
                                     ["Analista Fundamentalista (Valuation & Risco)", 
                                      "Estrategista Macro (Foco em Juros e Geopolítica)", 
                                      "Quant Trader (Foco em Backtest e Volatilidade)"], horizontal=True)
            with col_btn:
                if st.button("🧹 Reboot Neural", use_container_width=True):
                    st.session_state.messages = []
                    st.rerun()
            
            st.markdown("---")
            chat_container = st.container(height=500)
            with chat_container:
                for msg in st.session_state.messages:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

            if prompt := st.chat_input("Insira o comando. Ex: 'Analisando o Win Rate do Backtest e o indicador MFI atual, existe assimetria lógica?'"):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with chat_container:
                    with st.chat_message("user"): st.markdown(prompt)
                
                with chat_container:
                    with st.chat_message("assistant"):
                        with st.spinner(f"O Oráculo ({persona_ia}) está processando o data lake quantamental..."):
                            resp = generate_ai_response(prompt, contexto_invisivel, api_key, persona_ia)
                            st.markdown(resp)
                            st.session_state.messages.append({"role": "assistant", "content": resp})

if __name__ == "__main__":
    main()