import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from groq import Groq
from typing import Tuple, Dict, Optional, Any

# ==========================================
# CONFIGURAÇÃO DE UI (FRONT-END)
# ==========================================
st.set_page_config(
    page_title="Copiloto Financeiro IA | Elite", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================================
# KNOWLEDGE BASE: DATA LAKE EM MEMÓRIA (V6.0)
# ==========================================
GLOBAL_MACRO_CONTEXT = """
[CENÁRIO MACROECONÓMICO E GEOPOLÍTICO ATUAL]
- SELIC: 14.50% ao ano (após corte de 0.25 p.p.). Juro real restritivo; contrai consumo e encarece crédito imobiliário.
- PROJEÇÃO FOCUS: Selic terminal de 13.25% no final de 2026.
- INFLAÇÃO BRASIL: Focus projeta IPCA a 5.04% (desancorado da meta de 4.50%). IPCA-15 a 4.64% com pressão em habitação/energia.
- JUROS EUA (FED): 3.50% - 3.75%. Mantém custo global de capital elevado.
- INFLAÇÃO EUA: CPI a 3.8% (Core a 2.8%), impulsionada por energia.
- GEOPOLÍTICA (ORMUZ E SUEZ): Bloqueio no Irão e desvio no Mar Vermelho elevam fretes marítimos em até 4x e causam choque de +25% no barril de petróleo.
- CURVA DE JUROS (DI FUTURO): Jan/2031 a 13.36% e Jan/2035 a 13.535%. Reflete elevado prémio de risco e incerteza fiscal.

[INVENTÁRIO CORPORATIVO E CORRELAÇÕES]
- PETR4/PRIO3 (Petróleo): Hedge natural; altamente correlacionadas ao Brent. Forte geração de caixa.
- VALE3/GGBR4 (Materiais Básicos): Indexadas à China. Prejudicadas pelo encarecimento global do diesel.
- SUZB3/KLBN11 (Celulose): Receita dolarizada (proteção cambial), penalizadas por custos de frete global (Suez).
- ITUB4/BBAS3/BBDC4 (Bancos): ITUB4 defensivo (inadimplência de 1.9%). BBDC4 em turnaround. BBAS3 penalizado pelo agronegócio.
- TAEE11/EQTL3/ELET3 (Utilities): Fluxo previsível, blindadas contra inflação local (indexadas a IPCA/IGPM).
- VAREJO (MGLU3/LREN3/RENT3): Altamente sensíveis à curva de juros (DI). Sofrem compressão de margens com Selic restritiva.
- TECH EUA (NVDA/AAPL/MSFT): Sensíveis às treasuries americanas, mas sustentadas pela escalada secular de Inteligência Artificial.
"""

# ==========================================
# MÓDULO 1: MARKET DATA ENGINE
# ==========================================
@st.cache_data(ttl=900)
def fetch_market_data(ticker: str, period: str = "1y") -> Optional[pd.DataFrame]:
    """Extrai histórico global de preços com resiliência contra falhas de rede."""
    try:
        data = yf.Ticker(ticker).history(period=period)
        if data.empty:
            return None
        if data.index.tz is not None:
            data.index = data.index.tz_localize(None)
        return data
    except Exception:
        return None

# ==========================================
# MÓDULO 2: STRATEGY ENGINE (QUANTITATIVO)
# ==========================================
def calculate_indicators(df: pd.DataFrame, ma_window: int = 20) -> pd.DataFrame:
    """Calcula indicadores técnicos avançados: SMA, RSI (14) e MACD."""
    df_calc = df.copy()
    close_col = 'Close'
    df_calc['Close_Price'] = df_calc[close_col]
    
    # Média Móvel
    df_calc['SMA'] = df_calc[close_col].rolling(window=ma_window).mean()
    
    # Índice de Força Relativa (RSI)
    delta = df_calc[close_col].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df_calc['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = df_calc[close_col].ewm(span=12, adjust=False).mean()
    exp2 = df_calc[close_col].ewm(span=26, adjust=False).mean()
    df_calc['MACD'] = exp1 - exp2
    df_calc['Signal_Line'] = df_calc['MACD'].ewm(span=9, adjust=False).mean()
    
    return df_calc

def plot_interactive_chart(df: pd.DataFrame, ticker: str) -> go.Figure:
    """Renderização de gráficos de alta fidelidade visual (Dark Mode)."""
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close_Price'], name='Preço'
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df['SMA'], mode='lines', line=dict(color='#f59e0b', width=2), name='Média Móvel'
    ))
    fig.update_layout(
        title=f"Ação de Preço (Price Action): {ticker}",
        yaxis_title="Preço (Moeda Local)", xaxis_title="Linha Temporal",
        template="plotly_dark", xaxis_rangeslider_visible=False,
        height=450, margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor="#0f172a", plot_bgcolor="#0f172a"
    )
    return fig

# ==========================================
# MÓDULO 3: RISK ENGINE (BLINDAGEM)
# ==========================================
def calculate_position_size(capital: float, risk_pct: float, entry_price: float, stop_loss: float) -> Tuple[Optional[Dict[str, float]], Optional[str]]:
    """Motor de cálculo paramétrico de Risco e Position Sizing."""
    if stop_loss >= entry_price:
        return None, "ERRO CRÍTICO: O parâmetro de Stop Loss deve ser estritamente inferior ao Preço de Entrada (operações Long)."
    
    max_risk_amount = capital * (risk_pct / 100)
    risk_per_share = entry_price - stop_loss
    
    if risk_per_share <= 0:
        return None, "ERRO: Risco por ação nulo ou negativo."
        
    shares_to_buy = int(max_risk_amount // risk_per_share)
    total_position_value = shares_to_buy * entry_price
    
    return {
        "max_risk_amount": max_risk_amount,
        "shares_to_buy": shares_to_buy,
        "total_position_value": total_position_value,
        "risk_per_share": risk_per_share
    }, None

# ==========================================
# MÓDULO 4: CONTEXTUAL GENERATIVE ENGINE
# ==========================================
def generate_ai_response(prompt: str, context_data: str, api_key: str) -> str:
    """Motor Híbrido: Processamento de linguagem natural sobre matrizes quantitativas e macroeconómicas."""
    try:
        client = Groq(api_key=api_key)
        
        system_instruction = """Você é o 'Copiloto Financeiro IA', um mentor financeiro institucional de elite (Quantamental).
        REGRAS INEGOCIÁVEIS:
        1. RESPONDA ESTRITAMENTE EM PORTUGUÊS DO BRASIL.
        2. NUNCA faça recomendações diretas (compra/venda). Aja como um conselheiro analítico sênior.
        3. CRUZE AS VARIÁVEIS: Interligue obrigatoriamente os dados técnicos (RSI, MACD) com o contexto geopolítico/macro económico fornecido.
        4. FORMATAÇÃO: É expressamente PROIBIDO o uso de sintaxe LaTeX. Para valores financeiros, utilize unicamente 'R$' ou 'USD'. Utilize bullet points para clareza estrutural.
        5. O seu QI financeiro é equivalente ao de um Head de Tesouraria. Responda de forma pragmática, cínica quanto aos riscos e altamente profissional.
        """
        
        dossier_absoluto = f"{GLOBAL_MACRO_CONTEXT}\n\n[TELEMETRIA DO ATIVO EM TEMPO REAL]\n{context_data}"
        
        user_message = f"[MATRIZ DE CONHECIMENTO]\n{dossier_absoluto}\n\n[ANÁLISE SOLICITADA PELO OPERADOR]\n{prompt}"
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_message}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.15,
        )
        
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Falha na camada de comunicação neural (Groq API). Relatório de exceção: {e}"

# ==========================================
# DASHBOARD INSTITUCIONAL (MAIN PROCESS)
# ==========================================
def main():
    st.title("Copiloto Financeiro IA | Mesa Quantitativa")
    st.markdown("---")

    with st.sidebar:
        st.header("🗄️ Hub de Ativos Globais")
        
        # Catálogo expandido com segmentação institucional
        catalogo_institucional = {
            # --- ÍNDICES E ETFS ---
            "Índice Bovespa (BVSP)": "^BVSP",
            "S&P 500 (SPY)": "SPY",
            "Nasdaq 100 (QQQ)": "QQQ",
            "Ibovespa ETF (BOVA11)": "BOVA11.SA",
            "S&P 500 B3 ETF (IVVB11)": "IVVB11.SA",

            # --- COMMODITIES & MINERAÇÃO ---
            "Petrobras PN (PETR4)": "PETR4.SA",
            "Petrobras ON (PETR3)": "PETR3.SA",
            "Vale (VALE3)": "VALE3.SA",
            "Gerdau (GGBR4)": "GGBR4.SA",
            "CSN (CSNA3)": "CSNA3.SA",
            "Prio (PRIO3)": "PRIO3.SA",
            "Suzano (SUZB3)": "SUZB3.SA",
            "Klabin (KLBN11)": "KLBN11.SA",

            # --- SETOR FINANCEIRO ---
            "Itaú Unibanco (ITUB4)": "ITUB4.SA",
            "Banco do Brasil (BBAS3)": "BBAS3.SA",
            "Bradesco PN (BBDC4)": "BBDC4.SA",
            "Santander (SANB11)": "SANB11.SA",
            "BTG Pactual (BPAC11)": "BPAC11.SA",
            "B3 (B3SA3)": "B3SA3.SA",

            # --- ENERGIA E SANEAMENTO (UTILITIES) ---
            "Eletrobras (ELET3)": "ELET3.SA",
            "Equatorial (EQTL3)": "EQTL3.SA",
            "Taesa (TAEE11)": "TAEE11.SA",
            "Isa Cteep (TRPL4)": "TRPL4.SA",
            "Engie (EGIE3)": "EGIE3.SA",
            "Sabesp (SBSP3)": "SBSP3.SA",

            # --- VAREJO E CONSUMO ---
            "Ambev (ABEV3)": "ABEV3.SA",
            "Weg (WEGE3)": "WEGE3.SA",
            "Localiza (RENT3)": "RENT3.SA",
            "Magazine Luiza (MGLU3)": "MGLU3.SA",
            "Lojas Renner (LREN3)": "LREN3.SA",
            "Assaí (ASAI3)": "ASAI3.SA",
            "JBS (JBSS3)": "JBSS3.SA",

            # --- SAÚDE E TECNOLOGIA (BR) ---
            "Rede D'Or (RDOR3)": "RDOR3.SA",
            "Hapvida (HAPV3)": "HAPV3.SA",
            "Totvs (TOTS3)": "TOTS3.SA",

            # --- MERCADO INTERNACIONAL (EUA) ---
            "Apple (AAPL)": "AAPL",
            "Microsoft (MSFT)": "MSFT",
            "Nvidia (NVDA)": "NVDA",
            "Alphabet / Google (GOOGL)": "GOOGL",
            "Amazon (AMZN)": "AMZN",
            "Meta / Facebook (META)": "META",
            "Tesla (TSLA)": "TSLA",
            "Berkshire Hathaway (BRK-B)": "BRK-B",
            "JPMorgan Chase (JPM)": "JPM",

            # --- CRIPTOATIVOS & CÂMBIO ---
            "Bitcoin (BTC-USD)": "BTC-USD",
            "Ethereum (ETH-USD)": "ETH-USD",
            "Dólar / Real (BRL=X)": "BRL=X",
            "Euro / Dólar (EURUSD=X)": "EURUSD=X",

            # --- PESQUISA CUSTOMIZADA ---
            "Pesquisa Manual de Ticker": "OUTRO"
        }
        
        selecao_ativo = st.selectbox("Ativo em Análise:", list(catalogo_institucional.keys()))
        
        if selecao_ativo == "Pesquisa Manual de Ticker":
            ticker = st.text_input("Ticker Yahoo Finance:", value="NVDA").upper()
        else:
            ticker = catalogo_institucional[selecao_ativo]
            
        period = st.selectbox("Horizonte Temporal", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
        ma_window = st.slider("Calibração da Média Móvel", min_value=5, max_value=200, value=20)
        
        st.markdown("---")
        api_key = "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"
        st.info("🟢 Infraestrutura Híbrida: ATIVA\n\nTodos os motores (Market Data, Quant e Llama 3.1) operacionais.")

    df_raw = fetch_market_data(ticker, period)
    
    current_price = 0.0
    trend_status = "Desconhecido"
    rsi_status = "N/A"
    macd_status = "N/A"
    contexto_invisivel = ""

    if df_raw is not None:
        df_processed = calculate_indicators(df_raw, ma_window)
        
        ultima_linha = df_processed.iloc[-1]
        current_price = float(ultima_linha['Close_Price'])
        current_sma = float(ultima_linha['SMA'])
        current_rsi = float(ultima_linha['RSI'])
        current_macd = float(ultima_linha['MACD'])
        current_signal = float(ultima_linha['Signal_Line'])
        
        trend_status = "ALTA (Preço suportado acima da SMA)" if current_price > current_sma else "BAIXA (Preço rejeitado abaixo da SMA)"
        
        if pd.isna(current_rsi):
            rsi_status = "Sem liquidez histórica suficiente"
        elif current_rsi > 70:
            rsi_status = f"{current_rsi:.1f} (ZONA DE RISCO: Sobrecomprado)"
        elif current_rsi < 30:
            rsi_status = f"{current_rsi:.1f} (OPORTUNIDADE: Sobrevendido)"
        else:
            rsi_status = f"{current_rsi:.1f} (Equilíbrio Dinâmico)"
            
        macd_status = "Aceleração de Momentum (MACD > Sinal)" if current_macd > current_signal else "Decaimento de Momentum (MACD < Sinal)"

        contexto_invisivel = f"""
        [ATIVO ALVO: {ticker}]
        - Cotação de Fechamento: R$ {current_price:.2f}
        - Direcionalidade (SMA {ma_window}): {trend_status}
        - Força Relativa da Demanda (RSI 14d): {rsi_status}
        - Rastreio de Tendência (MACD): {macd_status}
        """

    tab1, tab2 = st.tabs(["📊 Mesa Operacional (Quant)", "🧠 Central de Inteligência (Macro & Corporativo)"])

    with tab1:
        if df_raw is not None:
            st.markdown("### Telemetria Quantitativa")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Preço de Mercado", f"R$ {current_price:.2f}")
            c2.metric(f"Suporte/Resistência (Média {ma_window})", f"R$ {current_sma:.2f}")
            c3.metric("Oscilador RSI", f"{current_rsi:.1f}")
            c4.metric("Estrutura MACD", "Compradora" if current_macd > current_signal else "Vendedora")
            
            st.markdown("---")
            
            col_chart, col_risk = st.columns([2, 1])
            with col_chart:
                fig = plot_interactive_chart(df_processed, ticker)
                st.plotly_chart(fig, use_container_width=True)

            with col_risk:
                st.subheader("Motor de Risco Paramétrico")
                with st.form("risk_form"):
                    capital = st.number_input("Exposição Máxima de Caixa (R$)", min_value=0.0, value=10000.0, step=100.0)
                    risk_pct = st.number_input("Tolerância a Drawdown (%)", min_value=0.1, max_value=10.0, value=2.0, step=0.1)
                    entry_price = st.number_input("Alvo de Execução (Preço)", min_value=0.0, value=current_price, step=0.01)
                    stop_loss = st.number_input("Trava de Segurança (Stop)", min_value=0.0, value=current_price * 0.95, step=0.01)
                    submit_button = st.form_submit_button("Validar Parâmetros de Risco")

                if submit_button:
                    result, error = calculate_position_size(capital, risk_pct, entry_price, stop_loss)
                    if error:
                        st.error(error)
                    else:
                        st.success("✅ Veto Superado: Operação enquadrada nos limites de segurança.")
                        st.metric("Teto de Lotes Permitidos", f"{result['shares_to_buy']} unidades")
                        st.metric("Volume Financeiro Bruto", f"R$ {result['total_position_value']:,.2f}")
                        st.markdown(f"**Risco Real Projetado:** R$ {result['max_risk_amount']:,.2f}")
        else:
            st.error("Falha de sincronização. Valide a nomenclatura do Ticker e a latência da rede.")

    with tab2:
        col_title, col_btn = st.columns([4, 1])
        with col_title:
            st.subheader("Processamento Cognitivo e Correlação Intermercados")
        with col_btn:
            if st.button("🧹 Purgar Memória", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        
        chat_container = st.container(height=450)
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        if prompt := st.chat_input("Insira o seu comando ou cenário para análise preditiva..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
            
            with chat_container:
                with st.chat_message("assistant"):
                    with st.spinner("A computar cenários geopolíticos e cruzamento quantitativo..."):
                        resposta_ia = generate_ai_response(prompt, contexto_invisivel, api_key)
                        st.markdown(resposta_ia)
                        st.session_state.messages.append({"role": "assistant", "content": resposta_ia})

if __name__ == "__main__":
    main()