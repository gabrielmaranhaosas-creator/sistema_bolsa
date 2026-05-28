import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from groq import Groq
from typing import Tuple, Dict, Optional, Any
import math

# ==============================================================================
# CONFIGURAÇÃO DE INFRAESTRUTURA DE UI (FRONT-END INSTITUCIONAL)
# ==============================================================================
st.set_page_config(
    page_title="Copiloto Financeiro IA | Terminal Quantamental V10.0", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Estilização Global CSS para Dark-Mode Premium - Padrão Bloomberg Terminal
st.markdown("""
<style>
    .stMetric { background-color: #0f172a; padding: 20px; border-radius: 10px; border: 1px solid #1e293b; border-left: 5px solid #38bdf8; box-shadow: 0 4px 6px rgba(0,0,0,0.3);}
    .stMetric label { color: #94a3b8 !important; font-weight: 600; font-size: 14px; }
    .stMetric div { color: #f8fafc !important; font-weight: 800; }
    .css-1d391kg { background-color: #020617; }
    h1, h2, h3, h4 { color: #f8fafc; font-family: 'Helvetica Neue', sans-serif; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background-color: #0f172a; border-radius: 4px 4px 0px 0px; padding: 10px 20px; border: 1px solid #1e293b; border-bottom: none; }
    .stTabs [aria-selected="true"] { background-color: #38bdf8; color: #020617 !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# ==============================================================================
# BASE DE DADOS MACROECONÔMICA GLOBAL (KNOWLEDGE BASE V10.0 - EXPANDIDA)
# ==============================================================================
GLOBAL_MACRO_CONTEXT = """
[CENÁRIO MACROECONÔMICO E GEOPOLÍTICO GLOBAL - V10.0]
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
# DICIONÁRIO INSTITUCIONAL DE ATIVOS (CATÁLOGO GLOBAL EXPANDIDO)
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
# MÓDULO 1: MOTOR DE INGESTÃO DE DADOS (MARKET DATA & FUNDAMENTOS)
# ==============================================================================
@st.cache_data(ttl=600)
def fetch_market_data(ticker: str, period: str = "2y") -> Optional[pd.DataFrame]:
    """Extração robusta de série temporal com normalização de Timezone para processamento quantitativo."""
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
    """Extração de indicadores fundamentalistas (P/L, Div Yield, Margens) via API."""
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
# MÓDULO 2: MOTOR MATEMÁTICO INSTITUCIONAL (INDICADORES AVANÇADOS)
# ==============================================================================
def calculate_advanced_indicators(df: pd.DataFrame, ma_window: int = 20) -> Tuple[pd.DataFrame, Dict[str, float], float, float]:
    """
    Computa a matriz quantitativa extrema:
    - SMA, EMA 9/21
    - Bandas de Bollinger, ATR, RSI, MACD, Estocástico
    - Nuvem de Ichimoku (Kumo)
    - On-Balance Volume (OBV)
    - Retornos Anualizados e Índice de Sharpe
    - Retrações de Fibonacci
    """
    df_calc = df.copy()
    close = df_calc['Close']
    high = df_calc['High']
    low = df_calc['Low']
    volume = df_calc['Volume']
    df_calc['Close_Price'] = close
    
    # Médias Móveis Direcionais
    df_calc['SMA'] = close.rolling(window=ma_window).mean()
    df_calc['EMA_9'] = close.ewm(span=9, adjust=False).mean()
    df_calc['EMA_21'] = close.ewm(span=21, adjust=False).mean()
    
    # Bandas de Bollinger
    std_dev = close.rolling(window=ma_window).std()
    df_calc['BB_Upper'] = df_calc['SMA'] + (std_dev * 2)
    df_calc['BB_Lower'] = df_calc['SMA'] - (std_dev * 2)
    df_calc['BB_Width'] = (df_calc['BB_Upper'] - df_calc['BB_Lower']) / df_calc['SMA']
    
    # Força Relativa (RSI 14)
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df_calc['RSI'] = 100 - (100 / (1 + (gain / loss)))
    
    # Momentum (MACD)
    df_calc['MACD'] = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
    df_calc['Signal_Line'] = df_calc['MACD'].ewm(span=9, adjust=False).mean()
    df_calc['MACD_Hist'] = df_calc['MACD'] - df_calc['Signal_Line']
    
    # Volatilidade (ATR 14)
    tr = pd.concat([high - low, abs(high - close.shift(1)), abs(low - close.shift(1))], axis=1).max(axis=1)
    df_calc['ATR'] = tr.rolling(window=14).mean()
    
    # Oscilador Estocástico (14,3)
    lowest_low = low.rolling(window=14).min()
    highest_high = high.rolling(window=14).max()
    df_calc['Stoch_K'] = 100 * ((close - lowest_low) / (highest_high - lowest_low))
    
    # On-Balance Volume (OBV) - Fluxo Institucional
    obv = np.where(close > close.shift(1), volume, np.where(close < close.shift(1), -volume, 0))
    df_calc['OBV'] = pd.Series(obv, index=df_calc.index).cumsum()
    
    # Nuvem de Ichimoku (Ichimoku Kinko Hyo)
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
    
    # Retrações de Fibonacci (Proporções Áureas) baseadas nas últimas 252 sessões (1 ano útil)
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

    # Avaliação de Desempenho Institucional (Sharpe Ratio)
    daily_returns = close.pct_change()
    ann_return = daily_returns.mean() * 252 * 100 
    ann_vol = daily_returns.std() * np.sqrt(252) * 100
    risk_free_rate = 14.50 
    sharpe_ratio = (ann_return - risk_free_rate) / ann_vol if ann_vol > 0 else 0

    return df_calc, fibo_levels, ann_return, sharpe_ratio

def plot_master_chart(df: pd.DataFrame, ticker: str, fibo: Dict[str, float]) -> go.Figure:
    """Renderizador Master Chart de 4 Eixos (Preço/BB, Ichimoku/Fibo, OBV, MACD, RSI)."""
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.04, 
                        subplot_titles=(f'Price Action, Bollinger & Fibonacci', 'Fluxo Institucional (On-Balance Volume)', 'Momentum (MACD)'),
                        row_width=[0.2, 0.2, 0.6])
    
    # ROW 1: Price, Bollinger, MAs, Fibonacci
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close_Price'], name='Preço'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], mode='lines', line=dict(color='#eab308', width=1.5), name='SMA'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], mode='lines', line=dict(color='rgba(255, 255, 255, 0.2)', width=1, dash='dash'), name='Bollinger Sup'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], mode='lines', line=dict(color='rgba(255, 255, 255, 0.2)', width=1, dash='dash'), name='Bollinger Inf', fill='tonexty', fillcolor='rgba(255, 255, 255, 0.05)'), row=1, col=1)
    
    # Fibonacci Lines Overlay
    fibo_colors = ['#ef4444', '#f97316', '#3b82f6', '#22c55e', '#a855f7']
    for (level_name, price), color in zip(fibo.items(), fibo_colors):
        fig.add_hline(y=price, line_dash="dot", line_color=color, line_width=1, annotation_text=level_name, annotation_position="top right", row=1, col=1)

    # ROW 2: On-Balance Volume (Fluxo de Capital)
    fig.add_trace(go.Scatter(x=df.index, y=df['OBV'], mode='lines', line=dict(color='#8b5cf6', width=2), name='OBV'), row=2, col=1)

    # ROW 3: MACD
    colors_macd = ['#22c55e' if val >= 0 else '#ef4444' for val in df['MACD_Hist']]
    fig.add_trace(go.Bar(x=df.index, y=df['MACD_Hist'], marker_color=colors_macd, name='Histograma'), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], mode='lines', line=dict(color='#3b82f6', width=1.5), name='MACD'), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Signal_Line'], mode='lines', line=dict(color='#f97316', width=1.5), name='Sinal'), row=3, col=1)
    
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=900, 
                      margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor="#020617", plot_bgcolor="#0f172a",
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    return fig

# ==============================================================================
# MÓDULO 3: SIMULADOR ESTOCÁSTICO (MONTE CARLO RANDOM WALK)
# ==============================================================================
def run_monte_carlo_simulation(df: pd.DataFrame, days_ahead: int = 30, simulations: int = 200) -> Tuple[np.ndarray, go.Figure, float]:
    """Cálculo estocástico de múltiplos caminhos futuros baseado na variância histórica."""
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
    
    fig.add_trace(go.Scatter(y=price_paths.mean(axis=1), mode='lines', line=dict(color='#eab308', width=3), name='Caminho Médio (Esperança Matemática)'))
    
    fig.update_layout(title=f"Motor Estocástico: {simulations} Caminhos Aleatórios ({days_ahead} pregões)",
                      yaxis_title="Projeção de Preço (R$ / USD)", xaxis_title="Linha do Tempo (Dias Futuros)",
                      template="plotly_dark", height=500, paper_bgcolor="#020617", plot_bgcolor="#0f172a")
    return price_paths, fig, expected_price

# ==============================================================================
# MÓDULO 4: MOTOR DE PRECIFICAÇÃO DE OPÇÕES (BLACK-SCHOLES)
# ==============================================================================
def norm_cdf(x: float) -> float:
    """Implementação da Função de Distribuição Acumulada Normal para evitar dependência externa pesada do SciPy."""
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

def black_scholes_pricing(S: float, K: float, T: float, r: float, sigma: float) -> Tuple[float, float, float]:
    """
    Algoritmo Black-Scholes-Merton para precificação teórica de derivativos (Opções Europeias).
    S: Preço atual do ativo (Spot)
    K: Preço de exercício da opção (Strike)
    T: Tempo até o vencimento em anos (Dias / 252)
    r: Taxa de juros livre de risco anualizada (Selic formatada em decimal)
    sigma: Volatilidade anualizada do ativo
    Retorna: (Preço da Call, Preço da Put, d1/Delta da Call)
    """
    if T <= 0 or sigma <= 0:
        return 0.0, 0.0, 0.0
        
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    
    call_price = S * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)
    put_price = K * math.exp(-r * T) * norm_cdf(-d2) - S * norm_cdf(-d1)
    
    return call_price, put_price, norm_cdf(d1)

# ==============================================================================
# MÓDULO 5: MOTOR GENERATIVO DE INTELIGÊNCIA ARTIFICIAL (GROQ CLOUD)
# ==============================================================================
def generate_ai_response(prompt: str, context_data: str, api_key: str) -> str:
    """Interface neural com o Llama 3.1. Funde os módulos de matemática, estatística estocástica e macroeconomia global."""
    try:
        client = Groq(api_key=api_key)
        
        system_instruction = """Você é o 'Copiloto Financeiro IA', Arquiteto-Chefe Quantamental de uma Tesouraria Institucional de Elite.
        
        DIRETRIZES DO NÚCLEO COGNITIVO (MANDATÓRIO):
        1. MATEMÁTICA ESTATÍSTICA: O operador vai lhe enviar dados brutais: RSI, MACD, Níveis de Fibonacci, Volatilidade ATR, Dados do OBV (Fluxo Institucional), Índices Fundamentalistas (P/L, Div Yield) e Projeções de Monte Carlo. Você deve ler e correlacionar essas camadas. NUNCA analise um dado isolado.
        2. ANÁLISE MACRO E GEOPOLÍTICA: O contexto inclui a Selic a 14.50%, inflação EUA, guerras tarifárias e crises no Mar Vermelho/Ormuz. Fundamente toda a oscilação do gráfico nessa gravidade macroeconômica. Exemplo: "O varejo derrete graficamente não por acaso, mas porque a Selic de 14.50% destrói a margem líquida".
        3. ASSIMETRIA DE RISCO E CÁLCULO DE BLACK-SCHOLES: Se o operador perguntar sobre opções, cite o prêmio de risco. Aja como um gestor calculista de Hedge Fund, sempre pesando o Índice de Sharpe.
        4. TOM INSTITUCIONAL SÊNIOR: Frio, técnico, brutalmente realista, cínico quanto às histerias de mercado de varejo, denso e complexo.
        5. FORMATAÇÃO: PROIBIDO usar formatação LaTeX. Valores sempre em "R$" ou "USD". Utilize Bullet Points para estruturar diagnósticos e cenários. 
        """
        
        payload = f"{GLOBAL_MACRO_CONTEXT}\n\n[MATRIZ QUANTITATIVA ESTOCÁSTICA, BLACK-SCHOLES E FUNDAMENTOS]\n{context_data}"
        user_message = f"[DATA LAKE INJETADO DO MOTOR PYTHON]\n{payload}\n\n[COMANDO DA MESA DE OPERAÇÕES]\n{prompt}"
        
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": user_message}],
            model="llama-3.1-8b-instant",
            temperature=0.35, # Temperatura balanceada entre racionalidade determinística e conexões criativas complexas
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"ALERTA CRÍTICO: Rompimento na sinapse neural (API Groq / Conexão HTTP). Detalhe técnico: {e}"

# ==============================================================================
# THREAD PRINCIPAL DO TERMINAL (DASHBOARD E LAYOUT)
# ==============================================================================
def main():
    st.title("Copiloto Financeiro IA | Terminal Quantamental V10.0 TITANIUM")
    st.markdown("---")

    with st.sidebar:
        st.header("🗄️ Controle de Missão")
        
        selecao_ativo = st.selectbox("Selecione o Ativo Global:", list(CATALOGO_INSTITUCIONAL.keys()))
        
        if selecao_ativo == "Pesquisa Manual de Ticker":
            ticker = st.text_input("Ticker Yahoo Finance (Ex: EMBR3.SA, URGO-USD, TQQQ):", value="NVDA").upper()
        else:
            ticker = CATALOGO_INSTITUCIONAL[selecao_ativo]
            
        col_t1, col_t2 = st.columns(2)
        with col_t1: period = st.selectbox("Range Histórico", ["3mo", "6mo", "1y", "2y", "5y", "max"], index=3)
        with col_t2: ma_window = st.number_input("Suavização (SMA)", min_value=5, max_value=200, value=20)
        
        st.markdown("---")
        # Injeção Direta da API Key para evitar complexidade no deploy
        api_key = "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"
        
        st.success("🟢 SISTEMA CORE V10.0: ONLINE\n\n🔹 Motor Monte Carlo: Operacional\n🔹 Black-Scholes Engine: Operacional\n🔹 Inteligência Híbrida: Conectada")

    # Ingestão de Dados
    df_raw = fetch_market_data(ticker, period)
    fundament_data = fetch_fundamental_data(ticker)
    
    # Variáveis Globais Vazias (Proteção contra Erros)
    contexto_invisivel = "Erro no pipeline de dados."
    
    if df_raw is not None:
        # Pipeline Matemático
        df_processed, fibo_levels, ann_return, sharpe_ratio = calculate_advanced_indicators(df_raw, ma_window)
        
        # Pipeline Monte Carlo
        mc_paths, mc_fig, mc_expected_price = run_monte_carlo_simulation(df_processed, days_ahead=30, simulations=100)
        
        # Leitura da Última Linha (Milissegundo Atual)
        ultima = df_processed.iloc[-1]
        c_price = float(ultima['Close_Price'])
        c_sma = float(ultima['SMA'])
        c_rsi = float(ultima['RSI'])
        c_macd = float(ultima['MACD'])
        c_sig = float(ultima['Signal_Line'])
        c_atr = float(ultima['ATR'])
        c_bbw = float(ultima['BB_Width'])
        c_stoch = float(ultima['Stoch_K'])
        c_obv = float(ultima['OBV'])
        
        # Traduções Lógicas Humanizadas
        trend = "ALTA TÉCNICA (Suportado na SMA)" if c_price > c_sma else "PRESSÃO VENDEDORA (Rejeição da SMA)"
        if pd.isna(c_rsi): rsi_txt = "Falta liquidez na série de dados"
        elif c_rsi > 70: rsi_txt = f"{c_rsi:.1f} (ZONA DE SOBRECOMPRA / EXAUSTÃO)"
        elif c_rsi < 30: rsi_txt = f"{c_rsi:.1f} (ZONA DE SOBREVENDA / DESCONTO)"
        else: rsi_txt = f"{c_rsi:.1f} (CONSOLIDAÇÃO NEUTRA)"
        
        # Compilação do Dossiê Neural para a IA
        fibo_str = ", ".join([f"{k}: R$ {v:.2f}" for k, v in fibo_levels.items()])
        fundamentos_str = ", ".join([f"{k}: {v}" for k, v in fundament_data.items()]) if fundament_data else "Dados fundamentalistas indisponíveis no Yahoo Finance para este ativo."
        
        contexto_invisivel = f"""
        [TELEMETRIA QUANTITATIVA E TÉCNICA - ATIVO: {ticker}]
        - Cotação de Fechamento Atual: R$ {c_price:.2f}
        - Comportamento de Tendência (Média {ma_window}d): {trend}
        - Indicador de Força (RSI 14): {rsi_txt}
        - Dinâmica de MACD: MACD Line {c_macd:.3f} vs Sinal {c_sig:.3f}
        - Volatilidade Diária Estressada (ATR 14): R$ {c_atr:.2f}
        - Acumulação de Fluxo de Institucionais (OBV): {c_obv:,.0f}
        - Estocástico Lento (%K): {c_stoch:.1f}%
        - Estrangulamento de Bollinger (Largura): {c_bbw:.3f}
        
        [MÉTRICAS DE DESEMPENHO AJUSTADO AO RISCO]
        - Retorno Histórico Anualizado da Série: {ann_return:.2f}%
        - Índice de Sharpe: {sharpe_ratio:.2f} (Calculado contra uma Taxa Livre de Risco de 14.50%)
        
        [ZONAS MATEMÁTICAS DE FIBONACCI]
        {fibo_str}
        
        [PROJEÇÃO ESTOCÁSTICA MONTE CARLO (Média de 100 Cenários para os próximos 30 dias)]
        - Preço Médio Esperado: R$ {mc_expected_price:.2f}
        
        [BALANÇO FUNDAMENTALISTA CORPORATIVO]
        {fundamentos_str}
        """

    # -------------------------------------------------------------------------
    # ESTRUTURA DE ABAS (TABS) - VISUALIZAÇÃO INSTITUCIONAL
    # -------------------------------------------------------------------------
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Terminal Gráfico Master", 
        "🏢 Análise Fundamentalista",
        "🎲 Monte Carlo Estocástico", 
        "⚙️ Black-Scholes & Risco Paramétrico", 
        "🧠 Cérebro Analítico IA"
    ])

    with tab1:
        if df_raw is not None:
            st.markdown("### Painel de Telemetria Multieixo")
            c1, c2, c3, c4 = st.columns(4)
            delta_pct = ((c_price / df_raw['Close'].iloc[-2]) - 1) * 100 if len(df_raw) > 1 else 0
            c1.metric("Cotação em Tempo Real", f"R$ {c_price:.2f}", delta=f"{delta_pct:.2f}%")
            c2.metric("ATR (Volatilidade Diária Risco)", f"R$ {c_atr:.2f}")
            c3.metric("RSI (Índice de Força 14d)", f"{c_rsi:.1f}")
            c4.metric("Desempenho Anual (Drift)", f"{ann_return:.1f}%", delta=f"Sharpe: {sharpe_ratio:.2f}")
            
            st.markdown("---")
            fig_master = plot_master_chart(df_processed, ticker, fibo_levels)
            st.plotly_chart(fig_master, use_container_width=True)
        else:
            st.error("Rompimento no feed de dados de mercado. Verifique a sintaxe do Ticker ou a conexão de rede.")

    with tab2:
        st.markdown("### Dossiê de Valuation e Saúde Financeira")
        st.markdown("Os dados abaixo são processados diretamente do DRE e Balanço Patrimonial da companhia, refletindo seus múltiplos atuais em relação ao mercado global.")
        if fundament_data:
            col_f1, col_f2, col_f3 = st.columns(3)
            col_f1.metric("Valor de Mercado (Market Cap)", f"{fundament_data.get('Market Cap', 'N/A')}")
            col_f1.metric("P/L (Preço sobre Lucro Atual)", f"{fundament_data.get('P/E Ratio (P/L)', 'N/A')}")
            col_f1.metric("Forward P/L (Expectativa)", f"{fundament_data.get('Forward P/E', 'N/A')}")
            
            col_f2.metric("Dividend Yield (Proventos)", f"{fundament_data.get('Dividend Yield', 0) * 100 if isinstance(fundament_data.get('Dividend Yield'), (int, float)) else 'N/A'}%")
            col_f2.metric("P/VP (Preço / Valor Patrimonial)", f"{fundament_data.get('Price to Book (P/VP)', 'N/A')}")
            col_f2.metric("Liquidez Corrente", f"{fundament_data.get('Current Ratio (Liquidez)', 'N/A')}")

            col_f3.metric("Margem de Lucro Líquida", f"{fundament_data.get('Profit Margin', 0) * 100 if isinstance(fundament_data.get('Profit Margin'), (int, float)) else 'N/A'}%")
            col_f3.metric("Margem Operacional EBITDA", f"{fundament_data.get('EBITDA Margin', 0) * 100 if isinstance(fundament_data.get('EBITDA Margin'), (int, float)) else 'N/A'}%")
            col_f3.metric("ROE (Retorno s/ Patrimônio Líq.)", f"{fundament_data.get('ROE (Retorno s/ Patrimônio)', 0) * 100 if isinstance(fundament_data.get('ROE (Retorno s/ Patrimônio)'), (int, float)) else 'N/A'}%")
        else:
            st.warning("Dados fundamentalistas não estão disponíveis para este ativo (geralmente ocorre em Índices puros ou ETFs sintéticos).")

    with tab3:
        if df_raw is not None:
            st.markdown("### Laboratório de Probabilidade e Caminho Aleatório (Random Walk)")
            st.markdown("Cálculo computacional pesado que simula o preço futuro iterando a volatilidade histórica em uma distribuição normal de probabilidades.")
            c_mc1, c_mc2 = st.columns(2)
            c_mc1.metric("Esperança Matemática (Média Ponderada a 30 dias)", f"R$ {mc_expected_price:.2f}", delta=f"{((mc_expected_price/c_price)-1)*100:.2f}% de Assimetria Prevista")
            c_mc2.metric("Base de Cálculo: Dias Úteis de Histórico", f"{len(df_processed)} sessões ingeridas")
            st.plotly_chart(mc_fig, use_container_width=True)

    with tab4:
        if df_raw is not None:
            st.markdown("### Algoritmo de Precificação Black-Scholes (Derivativos / Opções)")
            st.markdown("Precifica o prêmio justo teórico de opções Europeias utilizando volatilidade anualizada, tempo restante e a Taxa Selic.")
            
            with st.form("bs_form"):
                col_bs1, col_bs2, col_bs3 = st.columns(3)
                with col_bs1:
                    bs_spot = st.number_input("Spot Price (Preço Atual Ativo)", value=c_price, step=0.1)
                    bs_strike = st.number_input("Strike (Preço Alvo da Opção)", value=c_price * 1.05, step=0.1)
                with col_bs2:
                    bs_days = st.number_input("Dias Úteis até Vencimento", value=21, min_value=1, max_value=252)
                    bs_riskfree = st.number_input("Risk-Free Rate (Selic Anual %)", value=14.50, step=0.10)
                with col_bs3:
                    # Anualizando o ATR como aproximação simples de volatilidade histórica para derivativos
                    hist_vol_estimate = (c_atr / c_price) * math.sqrt(252) * 100
                    bs_vol = st.number_input("Volatilidade Implícita (Anual %)", value=float(hist_vol_estimate), step=1.0)
                
                bs_submit = st.form_submit_button("Executar Precificação Black-Scholes")
                
            if bs_submit:
                T_years = bs_days / 252.0
                r_decimal = bs_riskfree / 100.0
                vol_decimal = bs_vol / 100.0
                
                call_p, put_p, call_delta = black_scholes_pricing(bs_spot, bs_strike, T_years, r_decimal, vol_decimal)
                
                st.success("✅ Precificação Teórica Concluída.")
                c_res1, c_res2, c_res3 = st.columns(3)
                c_res1.metric("Prêmio Justo - Opção de COMPRA (CALL)", f"R$ {call_p:.3f}")
                c_res2.metric("Prêmio Justo - Opção de VENDA (PUT)", f"R$ {put_p:.3f}")
                c_res3.metric("Probabilidade de Exercício (Delta Call)", f"{call_delta * 100:.1f}%")
            
            st.markdown("---")
            st.markdown("### Calculadora Institucional de Position Sizing (Spot/Ações)")
            
            # Position Sizing Simples que já tínhamos
            with st.form("risk_form_v10"):
                c_f1, c_f2 = st.columns(2)
                with c_f1:
                    capital = st.number_input("Capital Operacional Alocado (R$)", min_value=0.0, value=150000.0, step=5000.0)
                    risk_pct = st.number_input("Trava de Drawdown por Trade (%)", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
                with c_f2:
                    entry_price = st.number_input("Preço Alvo de Execução (Entrada)", min_value=0.0, value=c_price, step=0.01)
                    stop_loss = st.number_input("Preço Trava de Segurança (Stop Loss)", min_value=0.0, value=c_price - (c_atr * 1.5), step=0.01)
                
                sub_btn = st.form_submit_button("Dimensionar Ordem de Operação")

            if sub_btn:
                if stop_loss >= entry_price:
                    st.error("ERRO GRAVE DE TESOURARIA: Operação direcional comprada (Long) exige Stop Loss inferior ao preço de mercado de entrada.")
                else:
                    risk_val = capital * (risk_pct / 100)
                    risk_per_share = entry_price - stop_loss
                    shares = int(risk_val // risk_per_share)
                    total_val = shares * entry_price
                    
                    st.success("✅ Protocolo de Proteção e Liquidez Aprovado.")
                    c_rs1, c_rs2, c_rs3 = st.columns(3)
                    c_rs1.metric("Lotes de Compra Autorizados", f"{shares} ações")
                    c_rs2.metric("Alocação Bruta Demandada", f"R$ {total_val:,.2f}")
                    c_rs3.metric("Risco Absoluto Bloqueado", f"R$ {risk_val:,.2f}")

    with tab5:
        if df_raw is not None:
            c_t, c_b = st.columns([4, 1])
            with c_t: st.subheader("Cérebro Quantamental IA: Interpretação Algorítmica e Macroeconômica")
            with c_b:
                if st.button("🧹 Reboot na Memória Neural", use_container_width=True):
                    st.session_state.messages = []
                    st.rerun()
            
            chat_container = st.container(height=550)
            with chat_container:
                for msg in st.session_state.messages:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

            if prompt := st.chat_input("Ex: 'Cruze os dados da Projeção de Monte Carlo, o P/L Fundamentalista e o OBV (Volume). Vale o risco frente a Selic?'"):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with chat_container:
                    with st.chat_message("user"): st.markdown(prompt)
                
                with chat_container:
                    with st.chat_message("assistant"):
                        with st.spinner("Decodificando série temporal, cruzando fundamentos com fluxo institucional de capital (OBV)..."):
                            resp = generate_ai_response(prompt, contexto_invisivel, api_key)
                            st.markdown(resp)
                            st.session_state.messages.append({"role": "assistant", "content": resp})

if __name__ == "__main__":
    main()