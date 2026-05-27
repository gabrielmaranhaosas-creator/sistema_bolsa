import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from groq import Groq

# ==========================================
# CONFIGURAÇÃO DE UI (FRONT-END)
# ==========================================
st.set_page_config(
    page_title="Copiloto Financeiro IA", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Inicializa o histórico de chat na sessão
if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================================
# MÓDULO 1: MARKET DATA ENGINE (EXPANDIDO)
# ==========================================
@st.cache_data(ttl=900)
def fetch_market_data(ticker: str, period: str = "1y") -> pd.DataFrame:
    """Extrai histórico global de preços."""
    try:
        ticker_obj = yf.Ticker(ticker)
        data = ticker_obj.history(period=period)
        if data.empty:
            return None
        if data.index.tz is not None:
            data.index = data.index.tz_localize(None)
        return data
    except Exception as e:
        return None

# ==========================================
# MÓDULO 2: STRATEGY ENGINE (PROFUNDO)
# ==========================================
def calculate_indicators(df: pd.DataFrame, ma_window: int = 20) -> pd.DataFrame:
    """Calcula SMA, RSI (14) e MACD para dossiê quantitativo."""
    df_calc = df.copy()
    close_col = 'Close'
    df_calc['Close_Price'] = df_calc[close_col]
    
    # 1. Média Móvel Simples (SMA)
    df_calc['SMA'] = df_calc[close_col].rolling(window=ma_window).mean()
    
    # 2. Relative Strength Index (RSI - 14 períodos)
    delta = df_calc[close_col].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df_calc['RSI'] = 100 - (100 / (1 + rs))
    
    # 3. MACD (Moving Average Convergence Divergence)
    exp1 = df_calc[close_col].ewm(span=12, adjust=False).mean()
    exp2 = df_calc[close_col].ewm(span=26, adjust=False).mean()
    df_calc['MACD'] = exp1 - exp2
    df_calc['Signal_Line'] = df_calc['MACD'].ewm(span=9, adjust=False).mean()
    
    return df_calc

def plot_interactive_chart(df: pd.DataFrame, ticker: str):
    """Renderiza gráficos em alta performance."""
    fig = go.Figure()
    
    # Candlesticks
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close_Price'], name='Preço'
    ))
    
    # Média Móvel
    fig.add_trace(go.Scatter(
        x=df.index, y=df['SMA'], mode='lines', line=dict(color='orange', width=2), name='Média Móvel'
    ))
    
    fig.update_layout(
        title=f"Ação de Preço e Tendência: {ticker}",
        yaxis_title="Preço", xaxis_title="Data",
        template="plotly_dark", xaxis_rangeslider_visible=False,
        height=450, margin=dict(l=0, r=0, t=40, b=0)
    )
    return fig

# ==========================================
# MÓDULO 3: RISK ENGINE
# ==========================================
def calculate_position_size(capital: float, risk_pct: float, entry_price: float, stop_loss: float):
    if stop_loss >= entry_price:
        return None, "O preço de Stop Loss deve ser menor que o Preço de Entrada."
    max_risk_amount = capital * (risk_pct / 100)
    risk_per_share = entry_price - stop_loss
    if risk_per_share <= 0:
        return None, "Configuração inválida."
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
    """Processa o dossiê na Groq via Llama 3.1."""
    try:
        client = Groq(api_key=api_key)
        
        system_instruction = """Você é o 'Copiloto Financeiro IA', um mentor financeiro quantitativo de elite.
        REGRAS INEGOCIÁVEIS:
        1. RESPONDA SEMPRE EM PORTUGUÊS DO BRASIL.
        2. NUNCA dê recomendações diretas de compra ou venda de ativos.
        3. Explique os cenários cruzando os dados técnicos (RSI, MACD, Médias) com a macroeconomia.
        4. PROIBIDO USAR FORMATAÇÃO LATEX. Nunca use o símbolo de cifrão isolado. Use apenas 'R$' ou 'USD'.
        5. Demonstre alto QI financeiro, seja direto, profissional e use tópicos claros.
        """
        
        user_message = f"[DOSSIÊ QUANTITATIVO DO ATIVO]\n{context_data}\n\n[PERGUNTA DO INVESTIDOR]\n{prompt}"
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_message}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.2, 
        )
        
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Erro na comunicação com a IA (Groq). Detalhe: {e}"

# ==========================================
# INTERFACE PRINCIPAL (DASHBOARD)
# ==========================================
def main():
    st.title("Copiloto Financeiro IA - Mesa de Operações Institucional")
    st.markdown("---")

    # --- BARRA LATERAL (BASE DE DADOS E CONTROLES) ---
    with st.sidebar:
        st.header("🔑 Conexão IA (Nuvem Gratuita)")
        api_key = st.text_input("Groq API Key", type="password", value="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")
        
        st.markdown("---")
        st.header("🗄️ Base de Dados Global")
        
        # Dicionário expandido de ativos
        ativos_populares = {
            "Petrobras (PETR4)": "PETR4.SA",
            "Vale (VALE3)": "VALE3.SA",
            "Itaú Unibanco (ITUB4)": "ITUB4.SA",
            "Banco do Brasil (BBAS3)": "BBAS3.SA",
            "WEG (WEGE3)": "WEGE3.SA",
            "Ibovespa - Índice (BVSP)": "^BVSP",
            "S&P 500 - EUA (SPY)": "SPY",
            "Apple (AAPL)": "AAPL",
            "Microsoft (MSFT)": "MSFT",
            "Bitcoin (BTC-USD)": "BTC-USD",
            "Ethereum (ETH-USD)": "ETH-USD",
            "Pesquisa Livre (Digitar Código)": "OUTRO"
        }
        
        selecao_ativo = st.selectbox("Selecione o Ativo:", list(ativos_populares.keys()))
        
        if selecao_ativo == "Pesquisa Livre (Digitar Código)":
            ticker = st.text_input("Digite o Ticker Yahoo Finance (ex: NVDA, BBDC4.SA):", value="NVDA").upper()
        else:
            ticker = ativos_populares[selecao_ativo]
            
        period = st.selectbox("Período Histórico", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
        ma_window = st.slider("Período da Média Móvel", min_value=5, max_value=200, value=20)
        
        st.markdown("---")
        ia_status = "ONLINE (Llama 3.1) 🟢" if api_key else "OFFLINE 🔴"
        st.info(f"Status dos Motores:\n- **Market Data:** ONLINE\n- **Strategy Engine:** ONLINE (RSI/MACD ativos)\n- **Risk Engine:** ONLINE\n- **IA Contextual:** {ia_status}")

    # Ingestão de Dados e Cálculos
    df_raw = fetch_market_data(ticker, period)
    
    current_price = 0.0
    trend_status = "Desconhecida"
    rsi_status = "N/A"
    macd_status = "N/A"
    contexto_invisivel = ""

    if df_raw is not None:
        df_processed = calculate_indicators(df_raw, ma_window)
        
        # Captura dos dados da última linha (mais recente)
        ultima_linha = df_processed.iloc[-1]
        current_price = float(ultima_linha['Close_Price'])
        current_sma = float(ultima_linha['SMA'])
        current_rsi = float(ultima_linha['RSI'])
        current_macd = float(ultima_linha['MACD'])
        current_signal = float(ultima_linha['Signal_Line'])
        
        # Tradução matemática para contexto da IA
        trend_status = "ALTA (Preço acima da SMA)" if current_price > current_sma else "BAIXA (Preço abaixo da SMA)"
        
        if pd.isna(current_rsi):
            rsi_status = "Aguardando mais dados"
        elif current_rsi > 70:
            rsi_status = f"{current_rsi:.1f} (Alerta: Ativo Sobrecomprado / Esticado)"
        elif current_rsi < 30:
            rsi_status = f"{current_rsi:.1f} (Alerta: Ativo Sobrevendido / Descontado)"
        else:
            rsi_status = f"{current_rsi:.1f} (Região Neutra)"
            
        macd_status = "Tendência Ganhando Força (MACD > Sinal)" if current_macd > current_signal else "Tendência Perdendo Força (MACD < Sinal)"

        # O Dossiê que o Python entrega secretamente para a IA
        contexto_invisivel = f"""
        [RAIO-X DO ATIVO: {ticker}]
        - Preço Atual de Mercado: R$ {current_price:.2f}
        - Tendência Curto Prazo (Média {ma_window}): {trend_status}
        - Força Relativa (RSI 14 dias): {rsi_status}
        - Momentum (MACD): {macd_status}
        """

    # --- SISTEMA DE ABAS ---
    tab1, tab2 = st.tabs(["📊 Mesa de Operações (Quant)", "🧠 Mentor IA (Contexto Macroeconômico)"])

    # ABA 1: MESA DE OPERAÇÕES 
    with tab1:
        if df_raw is not None:
            # Exibe um mini-painel com os indicadores técnicos calculados
            st.markdown("### Telemetria do Ativo")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Preço Atual", f"R$ {current_price:.2f}")
            col2.metric(f"Média Móvel ({ma_window}d)", f"R$ {current_sma:.2f}")
            col3.metric("RSI (Força)", f"{current_rsi:.1f}")
            col4.metric("Momento MACD", "Alta" if current_macd > current_signal else "Baixa")
            
            st.markdown("---")
            
            col_chart, col_risk = st.columns([2, 1])
            with col_chart:
                fig = plot_interactive_chart(df_processed, ticker)
                st.plotly_chart(fig, use_container_width=True)

            with col_risk:
                st.subheader("Risk Engine (Simulador)")
                with st.form("risk_form"):
                    capital = st.number_input("Capital Total Disponível (R$)", min_value=0.0, value=10000.0, step=100.0)
                    risk_pct = st.number_input("Risco Máximo Aceitável (%)", min_value=0.1, max_value=10.0, value=2.0, step=0.1)
                    entry_price = st.number_input("Preço de Entrada Planejado", min_value=0.0, value=current_price, step=0.01)
                    stop_loss = st.number_input("Preço de Stop Loss (Saída)", min_value=0.0, value=current_price * 0.95, step=0.01)
                    submit_button = st.form_submit_button("Travar Risco Operacional")

                if submit_button:
                    result, error = calculate_position_size(capital, risk_pct, entry_price, stop_loss)
                    if error:
                        st.error(error)
                    else:
                        st.success("✅ Protocolo de Risco Aprovado")
                        st.metric("Ações Limite para Compra", f"{result['shares_to_buy']} unidades")
                        st.metric("Alocação de Capital (Tamanho da Posição)", f"R$ {result['total_position_value']:,.2f}")
                        st.markdown(f"**Risco Financeiro Máximo:** R$ {result['max_risk_amount']:,.2f}")
        else:
            st.warning("Falha na extração de dados. Verifique a conexão ou a validade do código do ativo.")

    # ABA 2: MENTOR IA
    with tab2:
        col_title, col_btn = st.columns([4, 1])
        with col_title:
            st.subheader("Mentoria Macroeconômica e Análise de Contexto")
        with col_btn:
            if st.button("🧹 Limpar Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        
        if not api_key:
            st.warning("A conexão com a IA requer a chave API ativa.")
        else:
            chat_container = st.container(height=400)
            with chat_container:
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

            if prompt := st.chat_input("Ex: Considerando o RSI atual do ativo, há margem de segurança para entrada?"):
                
                st.session_state.messages.append({"role": "user", "content": prompt})
                with chat_container:
                    with st.chat_message("user"):
                        st.markdown(prompt)
                
                with chat_container:
                    with st.chat_message("assistant"):
                        with st.spinner("Processando dossiê quantitativo (Groq/Llama 3.1)..."):
                            resposta_ia = generate_ai_response(prompt, contexto_invisivel, api_key)
                            st.markdown(resposta_ia)
                            st.session_state.messages.append({"role": "assistant", "content": resposta_ia})

if __name__ == "__main__":
    main()