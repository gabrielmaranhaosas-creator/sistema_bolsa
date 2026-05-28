import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from groq import Groq
from typing import Tuple, Dict, Optional, Any

# ==========================================
# CONFIGURAÇÃO DE UI (FRONT-END INSTITUCIONAL)
# ==========================================
st.set_page_config(
    page_title="Copiloto Financeiro IA | Terminal Quantamental", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Estilização global via CSS para garantir formato dark-mode premium
st.markdown("""
<style>
    .stMetric { background-color: #0f172a; padding: 15px; border-radius: 8px; border: 1px solid #1e293b; }
    .css-1d391kg { background-color: #020617; }
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================================
# DATA LAKE EM MEMÓRIA (KNOWLEDGE BASE V8.0 - MASSIFICAÇÃO)
# ==========================================
GLOBAL_MACRO_CONTEXT = """
[CENÁRIO MACROECONÔMICO E GEOPOLÍTICO GLOBAL - ATUALIZADO]
- BRASIL (COPOM): Selic a 14.50% ao ano. Juro real estressado esmaga a liquidez de Small Caps e Varejo. Curva DI precifica alto risco fiscal (Jan/31 a 13.36%). A desancoragem do IPCA (5.04% Focus) impede afrouxamento monetário de curto prazo.
- ESTADOS UNIDOS (FED): Juros mantidos entre 3.50% - 3.75%. O Core CPI de 2.8% mostra inflação de serviços rígida. Dólar forte atrai capital global e drena os mercados emergentes (DXY elevado).
- EUROPA (BCE): Economia estagnada, BCE lutando entre recessão industrial na Alemanha e inflação fragmentada. Euro enfraquecido.
- CHINA (PBoC): Crise imobiliária não resolvida e estímulos monetários insuficientes. Baixa demanda por aço afeta diretamente o mercado de minério de ferro global.
- GEOPOLÍTICA DE ENERGIA: Bloqueio do Estreito de Ormuz e gargalos no Mar Vermelho (Suez). Fretes saltaram 400%. Petróleo Brent negocia com prêmio de guerra (+25%), pressionando a inflação de energia mundial.

[MATRIZ CORPORATIVA E SETORIAL - MAPEAMENTO PROFUNDO]
- ÓLEO E GÁS (PETR4, PRIO3, ENAT3): Beneficiárias diretas do caos geopolítico. Com Brent > USD 70 e Real desvalorizado, geram caixa abundante. Hedge geopolítico perfeito.
- MINERAÇÃO E SIDERURGIA (VALE3, GGBR4, CSNA3): Vítimas da desaceleração chinesa. Margens espremidas entre preço de venda cadente e custo de extração crescente (diesel caro).
- PAPEL E CELULOSE (SUZB3, KLBN11): Exportadoras natas. O dólar alto favorece as receitas, porém o bloqueio no Mar Vermelho impõe desafios de logística marítima severos.
- BANCOS (ITUB4, BBDC4, BBAS3, SANB11): ITUB4 opera como bunker (lucro histórico, inadimplência mínima). BBAS3 penalizado pela crise no agronegócio (quebra de safra e calotes). BBDC4 em longa reestruturação.
- UTILITIES / ELÉTRICAS (ELET3, TAEE11, EQTL3, TRPL4): Setor de proteção (defensivo). Receitas previsíveis atreladas à inflação (IGP-M/IPCA). Blindadas contra oscilações de juros.
- CONSTRUÇÃO E IMOBILIÁRIO (CYRE3, EZTC3): Altamente penalizadas. O custo do crédito (Selic a 14.50%) congela financiamentos imobiliários. Apenas alta renda (JHSF3) demonstra alguma resiliência.
- VAREJO E CONSUMO (MGLU3, LREN3, BHIA3, CRFB3): Em colapso de margens. O custo da dívida corrói os balanços operacionais. Inversamente correlacionadas à curva DI.
- AGRONEGÓCIO (SLCE3, SMTO3, TTEN3): Sofrem com as anomalias climáticas (El Niño/La Niña) e os juros elevados do Plano Safra. Atrasos operacionais impactam os resultados trimestrais.
- TECNOLOGIA GLOBAL (NVDA, AAPL, MSFT, META): O capital global busca segurança e hipercrescimento no monopólio de IA. Descoladas da macroeconomia tradicional.
- FIIS (FUNDOS IMOBILIÁRIOS): Os fundos de papel (CRI) indexados ao CDI/IPCA pagam dividendos recordes, enquanto fundos de tijolo sofrem desvalorização patrimonial devido à taxa de desconto (juro livre de risco) alta.
"""

# ==========================================
# MÓDULO 1: MOTOR DE INGESTÃO DE DADOS (MARKET DATA)
# ==========================================
@st.cache_data(ttl=600) # Cache otimizado para 10 minutos
def fetch_market_data(ticker: str, period: str = "1y") -> Optional[pd.DataFrame]:
    """Extração de série histórica via Yahoo Finance com tratamento rigoroso de exceções e normalização de timezone."""
    try:
        data = yf.Ticker(ticker).history(period=period)
        if data.empty or len(data) < 20: # Exige profundidade mínima de 20 períodos
            return None
        if data.index.tz is not None:
            data.index = data.index.tz_localize(None)
        return data
    except Exception as e:
        return None

# ==========================================
# MÓDULO 2: MOTOR ESTRATÉGICO QUANTITATIVO (EXPANSÃO EXTREMA)
# ==========================================
def calculate_advanced_indicators(df: pd.DataFrame, ma_window: int = 20) -> pd.DataFrame:
    """Computa uma matriz quantitativa complexa: SMA, EMA, RSI, MACD, Bollinger Bands, ATR e Stochastic."""
    df_calc = df.copy()
    close = df_calc['Close']
    high = df_calc['High']
    low = df_calc['Low']
    df_calc['Close_Price'] = close
    
    # 1. Médias Móveis (Simples e Exponencial)
    df_calc['SMA'] = close.rolling(window=ma_window).mean()
    df_calc['EMA_9'] = close.ewm(span=9, adjust=False).mean()
    df_calc['EMA_21'] = close.ewm(span=21, adjust=False).mean()
    
    # 2. Bandas de Bollinger (Volatilidade Relativa)
    std_dev = close.rolling(window=ma_window).std()
    df_calc['BB_Upper'] = df_calc['SMA'] + (std_dev * 2)
    df_calc['BB_Lower'] = df_calc['SMA'] - (std_dev * 2)
    df_calc['BB_Width'] = (df_calc['BB_Upper'] - df_calc['BB_Lower']) / df_calc['SMA']
    
    # 3. Índice de Força Relativa (RSI - 14)
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df_calc['RSI'] = 100 - (100 / (1 + rs))
    
    # 4. MACD (Momentum Direcional)
    exp12 = close.ewm(span=12, adjust=False).mean()
    exp26 = close.ewm(span=26, adjust=False).mean()
    df_calc['MACD'] = exp12 - exp26
    df_calc['Signal_Line'] = df_calc['MACD'].ewm(span=9, adjust=False).mean()
    df_calc['MACD_Hist'] = df_calc['MACD'] - df_calc['Signal_Line']
    
    # 5. ATR - Average True Range (14) - Risco Dinâmico Absoluto
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df_calc['ATR'] = true_range.rolling(window=14).mean()
    
    # 6. Oscilador Estocástico (14, 3) - Sobrecompra/Sobrevenda de microestrutura
    lowest_low = low.rolling(window=14).min()
    highest_high = high.rolling(window=14).max()
    df_calc['Stoch_K'] = 100 * ((close - lowest_low) / (highest_high - lowest_low))
    df_calc['Stoch_D'] = df_calc['Stoch_K'].rolling(window=3).mean()
    
    return df_calc

def plot_master_chart(df: pd.DataFrame, ticker: str) -> go.Figure:
    """Renderiza um gráfico financeiro Master com Preço, Bollinger, Volume e MACD combinados."""
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.03, subplot_titles=(f'Price Action & Bollinger: {ticker}', 'Momentum (MACD)'),
                        row_width=[0.2, 0.7])
    
    # Candlestick
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close_Price'], name='Preço'), row=1, col=1)
    
    # Média e Bollinger
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], mode='lines', line=dict(color='yellow', width=1.5), name='SMA'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], mode='lines', line=dict(color='rgba(255, 255, 255, 0.2)', width=1, dash='dash'), name='BB Upper'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], mode='lines', line=dict(color='rgba(255, 255, 255, 0.2)', width=1, dash='dash'), name='BB Lower', fill='tonexty', fillcolor='rgba(255, 255, 255, 0.05)'), row=1, col=1)
    
    # MACD Subplot
    colors = ['green' if val >= 0 else 'red' for val in df['MACD_Hist']]
    fig.add_trace(go.Bar(x=df.index, y=df['MACD_Hist'], marker_color=colors, name='MACD Hist'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], mode='lines', line=dict(color='blue', width=1), name='MACD Line'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Signal_Line'], mode='lines', line=dict(color='orange', width=1), name='Signal'), row=2, col=1)
    
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=650, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor="#0f172a", plot_bgcolor="#0f172a")
    return fig

# ==========================================
# MÓDULO 3: RISK ENGINE (TRAVAS DE CAPITAL INSTITUCIONAIS)
# ==========================================
def calculate_position_size(capital: float, risk_pct: float, entry_price: float, stop_loss: float, atr: float = None) -> Tuple[Optional[Dict[str, float]], Optional[str]]:
    """Calcula o tamanho da posição com base no risco financeiro e valida se o Stop Loss obedece a volatilidade (ATR)."""
    if stop_loss >= entry_price:
        return None, "ERRO ESTRUTURAL: O Stop Loss deve ser estritamente inferior ao Preço de Entrada em operações de compra (Long)."
    
    max_risk_amount = capital * (risk_pct / 100)
    risk_per_share = entry_price - stop_loss
    
    if risk_per_share <= 0:
        return None, "ERRO MATEMÁTICO: Risco por ação inválido."
        
    shares_to_buy = int(max_risk_amount // risk_per_share)
    total_position_value = shares_to_buy * entry_price
    
    warning = None
    if atr and (entry_price - stop_loss) < (atr * 0.5):
        warning = "ALERTA DE VOLATILIDADE: Seu Stop Loss está posicionado muito próximo da entrada (menos de 0.5x o ATR). Alto risco de ser violinado pelo ruído natural do mercado."

    return {
        "max_risk_amount": max_risk_amount,
        "shares_to_buy": shares_to_buy,
        "total_position_value": total_position_value,
        "risk_per_share": risk_per_share,
        "warning": warning
    }, None

# ==========================================
# MÓDULO 4: MOTOR GENERATIVO QUANTAMENTAL (O CÉREBRO LLAMA 3.1)
# ==========================================
def generate_ai_response(prompt: str, context_data: str, api_key: str) -> str:
    """Motor de orquestração neural via Groq. Cruza dados matemáticos brutos com cenários globais abstratos."""
    try:
        client = Groq(api_key=api_key)
        
        system_instruction = """Você é o 'Copiloto Financeiro IA', o Arquiteto-Chefe e Mentor Financeiro de uma Tesouraria Institucional.
        
        SUA MISSÃO ESTRUTURAL (OBRIGATÓRIA):
        1. ANÁLISE QUANTITATIVA EXTREMA: Não seja superficial. Ao ver os dados (RSI, MACD, Bollinger, ATR), correlacione-os. Ex: "O preço toca a banda inferior de Bollinger enquanto o Estocástico aponta sobrevenda, sinalizando exaustão estatística".
        2. ANÁLISE FUNDAMENTALISTA E MACRO: Conecte o Ticker com o cenário macro injetado. Como a Selic a 14.50%, a inflação de 5.04% e a crise no Estreito de Ormuz destroem ou protegem o fluxo de caixa dessa empresa específica?
        3. AÇÃO E ASSIMETRIA: Defina probabilidades. Nunca garanta resultados. Trabalhe com projeções de risco-retorno. Use o ATR fornecido para sugerir zonas lógicas de Stop Loss.
        4. POSTURA E TOM DE VOZ: Pragmático, brutalmente realista, altamente técnico e denso. Zero emoção. Pense como um algoritmo de hedge fund.
        5. REGRAS DE FORMATAÇÃO: PROIBIDO uso de LaTeX ($, \n, \textbf). Para valores financeiros use APENAS "R$" ou "USD". Utilize Listas (Bullet Points) para organização tática.
        """
        
        # O Payload completo enviado secretamente para a IA
        payload = f"{GLOBAL_MACRO_CONTEXT}\n\n[DADOS DE TELEMETRIA MILISSEGUNDO ATUAL - MATRIZ TÉCNICA]\n{context_data}"
        
        user_message = f"[KNOWLEDGE BASE INJETADA]\n{payload}\n\n[INSTRUÇÃO DO GESTOR DA MESA]\n{prompt}"
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_message}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.35, # Permite correlações criativas entre mercado gráfico e geopolítica, mas sem alucinações.
        )
        
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"ALERTA DO SISTEMA: Interrupção na camada neural (API Groq). Log de falha: {e}"

# ==========================================
# THREAD PRINCIPAL DO DASHBOARD (MAIN PROCESS)
# ==========================================
def main():
    st.title("Copiloto Financeiro IA | Plataforma Quantamental V8.0")
    st.markdown("---")

    with st.sidebar:
        st.header("🗄️ Terminal Global de Ativos")
        
        # Dicionário de ativos massivamente expandido para cobrir múltiplos mercados
        catalogo_institucional = {
            # ÍNDICES E ETFS GLOBAIS
            "Índice Bovespa (BVSP)": "^BVSP",
            "S&P 500 (SPY)": "SPY",
            "Nasdaq 100 (QQQ)": "QQQ",
            "Ibovespa ETF (BOVA11)": "BOVA11.SA",
            "S&P 500 B3 ETF (IVVB11)": "IVVB11.SA",
            "Ouro (GLD)": "GLD",
            "Petróleo Brent ETF (BNO)": "BNO",

            # BLUE CHIPS E COMMODITIES BRASIL
            "Petrobras PN (PETR4)": "PETR4.SA",
            "Petrobras ON (PETR3)": "PETR3.SA",
            "Vale (VALE3)": "VALE3.SA",
            "Gerdau (GGBR4)": "GGBR4.SA",
            "CSN (CSNA3)": "CSNA3.SA",
            "Prio (PRIO3)": "PRIO3.SA",
            "Suzano (SUZB3)": "SUZB3.SA",
            "Klabin (KLBN11)": "KLBN11.SA",
            
            # AGRONEGÓCIO E PROTEÍNAS
            "SLC Agrícola (SLCE3)": "SLCE3.SA",
            "São Martinho (SMTO3)": "SMTO3.SA",
            "JBS (JBSS3)": "JBSS3.SA",
            "BRF (BRFS3)": "BRFS3.SA",

            # SETOR FINANCEIRO E SEGURADORAS
            "Itaú Unibanco (ITUB4)": "ITUB4.SA",
            "Banco do Brasil (BBAS3)": "BBAS3.SA",
            "Bradesco PN (BBDC4)": "BBDC4.SA",
            "BTG Pactual (BPAC11)": "BPAC11.SA",
            "B3 (B3SA3)": "B3SA3.SA",
            "BB Seguridade (BBSE3)": "BBSE3.SA",

            # UTILITIES (ELÉTRICAS E SANEAMENTO)
            "Eletrobras (ELET3)": "ELET3.SA",
            "Taesa (TAEE11)": "TAEE11.SA",
            "Equatorial (EQTL3)": "EQTL3.SA",
            "Isa Cteep (TRPL4)": "TRPL4.SA",
            "Sabesp (SBSP3)": "SBSP3.SA",

            # VAREJO, SAÚDE E CONSUMO DOMÉSTICO
            "Weg (WEGE3)": "WEGE3.SA",
            "Localiza (RENT3)": "RENT3.SA",
            "Magazine Luiza (MGLU3)": "MGLU3.SA",
            "Lojas Renner (LREN3)": "LREN3.SA",
            "Assaí (ASAI3)": "ASAI3.SA",
            "Rede D'Or (RDOR3)": "RDOR3.SA",

            # CONSTRUÇÃO E FUNDOS IMOBILIÁRIOS (FIIS)
            "Cyrela (CYRE3)": "CYRE3.SA",
            "JHSF (JHSF3)": "JHSF3.SA",
            "Maxi Renda FII (MXRF11)": "MXRF11.SA",
            "CSHG Logística (HGLG11)": "HGLG11.SA",
            "Kinea Renda Imobiliária (KNRI11)": "KNRI11.SA",

            # TECNOLOGIA E MERCADO INTERNACIONAL (BDRS/EUA)
            "Nvidia (NVDA)": "NVDA",
            "Apple (AAPL)": "AAPL",
            "Microsoft (MSFT)": "MSFT",
            "Alphabet / Google (GOOGL)": "GOOGL",
            "Amazon (AMZN)": "AMZN",
            "Tesla (TSLA)": "TSLA",
            "TSMC - Semicondutores (TSM)": "TSM",
            "Mercado Livre (MELI)": "MELI",

            # CÂMBIO E CRIPTOATIVOS
            "Bitcoin (BTC-USD)": "BTC-USD",
            "Ethereum (ETH-USD)": "ETH-USD",
            "Solana (SOL-USD)": "SOL-USD",
            "Dólar / Real (BRL=X)": "BRL=X",
            
            # CUSTOM
            "Pesquisa Manual de Ticker": "OUTRO"
        }
        
        selecao_ativo = st.selectbox("Selecione a Classe e o Ativo:", list(catalogo_institucional.keys()))
        
        if selecao_ativo == "Pesquisa Manual de Ticker":
            ticker = st.text_input("Ticker Yahoo Finance (ex: MILS3.SA, URGO-USD):", value="NVDA").upper()
        else:
            ticker = catalogo_institucional[selecao_ativo]
            
        col_t1, col_t2 = st.columns(2)
        with col_t1: period = st.selectbox("Série Histórica", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
        with col_t2: ma_window = st.number_input("Média Móvel Base", min_value=5, max_value=200, value=20)
        
        st.markdown("---")
        api_key = "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"
        st.success("🟢 SISTEMA CORE: OPERACIONAL\n\nNível de Temperatura IA: 0.35\nMotor ATR/Bollinger: Ativo\nMatriz Macro: Atualizada.")

    df_raw = fetch_market_data(ticker, period)
    
    # Variáveis de telemetria
    current_price = current_sma = current_rsi = current_macd = current_signal = current_atr = current_bbw = current_stoch = 0.0
    trend_status = rsi_status = macd_status = bb_status = contexto_invisivel = "Aguardando processamento..."

    if df_raw is not None:
        df_processed = calculate_advanced_indicators(df_raw, ma_window)
        
        ultima_linha = df_processed.iloc[-1]
        current_price = float(ultima_linha['Close_Price'])
        current_sma = float(ultima_linha['SMA'])
        current_rsi = float(ultima_linha['RSI'])
        current_macd = float(ultima_linha['MACD'])
        current_signal = float(ultima_linha['Signal_Line'])
        current_atr = float(ultima_linha['ATR'])
        current_bb_upper = float(ultima_linha['BB_Upper'])
        current_bb_lower = float(ultima_linha['BB_Lower'])
        current_bbw = float(ultima_linha['BB_Width'])
        current_stoch = float(ultima_linha['Stoch_K'])
        
        # Algoritmos de Tradução de Sinais Matemáticos
        trend_status = "ALTA TÉCNICA (Preço cota acima da Média)" if current_price > current_sma else "PRESSÃO VENDEDORA (Preço rejeitado abaixo da Média)"
        
        if pd.isna(current_rsi): rsi_status = "Falta de liquidez histórica"
        elif current_rsi > 70: rsi_status = f"{current_rsi:.1f} (ZONA DE EXAUSTÃO/SOBRECOMPRADO)"
        elif current_rsi < 30: rsi_status = f"{current_rsi:.1f} (ZONA DE ASSIMETRIA/SOBREVENDIDO)"
        else: rsi_status = f"{current_rsi:.1f} (NEUTRO)"
            
        macd_status = "Aceleração Positiva (MACD > Sinal)" if current_macd > current_signal else "Aceleração Negativa (MACD < Sinal)"
        
        if current_price >= current_bb_upper: bb_status = "Esticado: Tocando Banda Superior"
        elif current_price <= current_bb_lower: bb_status = "Amassado: Tocando Banda Inferior"
        else: bb_status = "Preço contido no canal de volatilidade"

        # Dossiê Invisível - A Semente do Cérebro da IA
        contexto_invisivel = f"""
        [TELEMETRIA QUANTITATIVA ABSOLUTA DO ATIVO: {ticker}]
        - Cotação de Fechamento: R$ {current_price:.2f}
        - Direcionalidade (SMA {ma_window}): {trend_status}
        - Força Relativa do Fluxo (RSI 14d): {rsi_status}
        - Momento Estrutural (MACD): {macd_status}
        - Volatilidade Absoluta (ATR 14d): O preço varia em média R$ {current_atr:.2f} por dia.
        - Oscilador Estocástico: {current_stoch:.1f}% (Níveis próximos a 20% indicam sobrevenda micro, 80% sobrecompra).
        - Bandas de Bollinger: {bb_status}. Largura da Banda: {current_bbw:.2f}.
        """

    tab1, tab2, tab3 = st.tabs(["📊 Mesa Quantitativa", "⚡ Risco & Volatilidade", "🧠 Mentor Institucional IA"])

    with tab1:
        if df_raw is not None:
            st.markdown("### Telemetria Gráfica Principal")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Preço Atual", f"R$ {current_price:.2f}", delta=f"{((current_price/df_raw['Close'].iloc[-2])-1)*100:.2f}%")
            c2.metric(f"Média Alvo ({ma_window}d)", f"R$ {current_sma:.2f}")
            c3.metric("RSI (Índice de Força)", f"{current_rsi:.1f}")
            c4.metric("Estrutura MACD", "Fluxo Comprador" if current_macd > current_signal else "Fluxo Vendedor")
            
            st.markdown("---")
            fig = plot_master_chart(df_processed, ticker)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Erro de sincronização HTTP. Verifique o ticker ou a rede.")

    with tab2:
        if df_raw is not None:
            st.markdown("### Análise de Risco Dinâmico e Volatilidade")
            c_v1, c_v2, c_v3 = st.columns(3)
            c_v1.metric("ATR (Amplitude de Preço Diária)", f"R$ {current_atr:.2f}", help="Variação média do ativo por dia (Risco diário)")
            c_v2.metric("Oscilador Estocástico (%K)", f"{current_stoch:.1f}%", help="Momento de curto prazo do preço")
            c_v3.metric("Largura de Bollinger (Squeeze)", f"{current_bbw:.3f}", help="Se o valor estiver muito baixo, indica acúmulo de energia para rompimento violento.")
            
            st.markdown("---")
            st.subheader("Motor de Alocação de Capital (Position Sizing)")
            with st.form("risk_form_advanced"):
                col_form1, col_form2 = st.columns(2)
                with col_form1:
                    capital = st.number_input("Caixa Total da Tesouraria (R$)", min_value=0.0, value=100000.0, step=5000.0)
                    risk_pct = st.number_input("Risco Máximo por Operação (%)", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
                with col_form2:
                    entry_price = st.number_input("Preço de Entrada Target", min_value=0.0, value=current_price, step=0.01)
                    stop_loss = st.number_input("Preço de Stop Loss de Segurança", min_value=0.0, value=current_price - current_atr, step=0.01, help="Por padrão, o Stop está ajustado 1x ATR abaixo do preço.")
                
                submit_button = st.form_submit_button("Validar Parâmetros de Risco")

            if submit_button:
                result, error = calculate_position_size(capital, risk_pct, entry_price, stop_loss, current_atr)
                if error:
                    st.error(error)
                else:
                    if result.get('warning'):
                        st.warning(result['warning'])
                    st.success("✅ Risco Mapeado com Sucesso. Operação Matematicamente Autorizada.")
                    st.metric("Lotes de Compra Autorizados", f"{result['shares_to_buy']} ações")
                    st.metric("Alocação Financeira Bruta", f"R$ {result['total_position_value']:,.2f}")
                    st.markdown(f"**Drawdown Máximo Travado:** R$ {result['max_risk_amount']:,.2f}")

    with tab3:
        col_title, col_btn = st.columns([4, 1])
        with col_title:
            st.subheader("Sincronização Neural: Macro, Micro e Fluxo Quantitativo")
        with col_btn:
            if st.button("🧹 Limpar Cache Cognitivo", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        
        chat_container = st.container(height=500)
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        if prompt := st.chat_input("Ex: Considerando a atual volatilidade (ATR) e o RSI sobrevendido, existe assimetria para uma compra técnica apesar do cenário macro?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
            
            with chat_container:
                with st.chat_message("assistant"):
                    with st.spinner("Processando cruzamento multivariável (Bollinger, ATR, Inflação e Curva de Juros)..."):
                        resposta_ia = generate_ai_response(prompt, contexto_invisivel, api_key)
                        st.markdown(resposta_ia)
                        st.session_state.messages.append({"role": "assistant", "content": resposta_ia})

if __name__ == "__main__":
    main()