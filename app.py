import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as nf
import plotly.graph_objects as go

st.set_page_config(
    page_title="Viabilidade Imobiliária", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏘️ Análise de Viabilidade de Empreendimentos Imobiliários")

#
# --- SIDEBAR COM EXPANDERS PARA INPUTS ---
#
with st.sidebar.expander("🔶 1. Dados do Terreno", expanded=True):
    preco_terreno = st.number_input(
        "Preço de aquisição do terreno (R$)", 
        value=1_000_000.0, step=50_000.0, format="%.2f"
    )
    area_terreno = st.number_input(
        "Área total do terreno (m²)", 
        value=1_000.0, step=10.0
    )
    custos_regularizacao = st.number_input(
        "Custos de regularização (R$)", 
        value=50_000.0, step=5_000.0, format="%.2f"
    )

with st.sidebar.expander("🔷 2. Dados do Projeto"):
    area_construida = st.number_input(
        "Área total construída (m²)", 
        value=5_000.0, step=100.0
    )
    area_privativa = st.number_input(
        "Área privativa total (m²)", 
        value=3_000.0, step=100.0
    )
    num_unidades = st.number_input(
        "Número de unidades", 
        value=50, step=1
    )
    st.markdown("**Tipologias (nome: qtd, área média)**")
    tipos_raw = st.text_area(
        "Exemplo:\n1Q+Sala:20,60\n2Q+Sala:20,80\n3Q+Sala:10,100",
        height=120
    )

with st.sidebar.expander("🔶 3. Custos de Construção"):
    custo_construcao_m2 = st.number_input(
        "Custo de construção (R$/m²)", 
        value=2_000.0, step=100.0, format="%.2f"
    )
    custos_indiretos = st.number_input(
        "Custos indiretos (R$)", 
        value=200_000.0, step=10_000.0, format="%.2f"
    )
    custos_licenciamento = st.number_input(
        "Custos de licenciamento (R$)", 
        value=100_000.0, step=10_000.0, format="%.2f"
    )

with st.sidebar.expander("🔷 4. Vendas & Marketing"):
    preco_venda_medio = st.number_input(
        "Preço médio de venda/unidade (R$)", 
        value=350_000.0, step=10_000.0, format="%.2f"
    )
    comissao_vendas = st.slider(
        "Comissão de vendas (%)", 
        min_value=0.0, max_value=10.0, value=2.0, step=0.1
    ) / 100.0
    custos_marketing = st.number_input(
        "Custos de marketing (R$)", 
        value=50_000.0, step=5_000.0, format="%.2f"
    )

with st.sidebar.expander("🔶 5. Parâmetros Financeiros"):
    taxa_juros = st.slider(
        "Taxa de desconto anual (%)", 
        min_value=0.0, max_value=20.0, value=10.0, step=0.1
    ) / 100.0

#
# --- PARSE DAS TIPOLOGIAS ---
#
def parse_tipologias(text):
    linhas = [l for l in text.splitlines() if l.strip()]
    data = {"Tipologia": [], "Qtd": [], "Área Média": []}
    for ln in linhas:
        try:
            nome, vals = ln.split(":")
            q, a = vals.split(",")
            data["Tipologia"].append(nome.strip())
            data["Qtd"].append(int(q.strip()))
            data["Área Média"].append(float(a.strip()))
        except:
            continue
    return pd.DataFrame(data)

df_tipos = parse_tipologias(tipos_raw)

#
# --- CÁLCULOS ---
#
# Construção
custo_prev_construcao = area_construida * custo_construcao_m2
investimento_construcao = (
    custo_prev_construcao + custos_indiretos + custos_licenciamento
)

# Investimento total
investimento_total = (
    preco_terreno + custos_regularizacao 
    + investimento_construcao + custos_marketing
)

# Receita e comissões
receita_total = num_unidades * preco_venda_medio
valor_comissao = receita_total * comissao_vendas

# Lucro bruto
lucro_bruto = receita_total - investimento_total - valor_comissao

# Fluxo de caixa simples: T0 = -investimento; T1 = receita líquida
fluxos = [-investimento_total, receita_total - valor_comissao]
vpl = nf.npv(taxa_juros, fluxos)
tir = nf.irr(fluxos)
payback = (
    investimento_total / (receita_total - valor_comissao)
    if receita_total - valor_comissao > 0 else np.nan
)

#
# --- EXIBIÇÃO EM TABS ---
#
tab1, tab2, tab3 = st.tabs(["📊 Visão Geral", "💰 Financeiro", "🔄 Sensibilidade"])

with tab1:
    st.header("Visão Geral do Projeto")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Investimento Total", f"R$ {investimento_total:,.0f}")
    col2.metric("Receita Total",      f"R$ {receita_total:,.0f}")
    col3.metric("Lucro Bruto",        f"R$ {lucro_bruto:,.0f}")
    col4.metric("Payback (anos)",     f"{payback:.2f}" if not np.isnan(payback) else "–")
    
    st.subheader("Tipologias das Unidades")
    st.dataframe(df_tipos, use_container_width=True)

with tab2:
    st.header("Análise Financeira")
    st.metric("VPL (R$)", f"R$ {vpl:,.0f}")
    st.metric("TIR (%)", f"{tir*100:.2f}%")
    st.markdown("---")
    st.subheader("Fluxo de Caixa Projetado")
    
    years = ["T0", "T1"]
    values = [fluxos[0], fluxos[1]]
    fig = go.Figure([
        go.Bar(x=years, y=values, text=[f"R$ {v:,.0f}" for v in values], textposition="auto",
               marker_color=["crimson", "seagreen"])
    ])
    fig.update_layout(yaxis_title="R$", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("Análise de Sensibilidade")
    st.markdown(
        "Teste variações de ±10% em preço de venda e custo de construção:"
    )
    var_price = st.slider("Variação no preço de venda (%)", -20, 20, 10, 5)
    var_cost  = st.slider("Variação no custo de construção (%)", -20, 20, 10, 5)
    
    # recalcula com variações
    preco_adj = preco_venda_medio * (1 + var_price/100)
    custo_adj = custo_construcao_m2 * (1 + var_cost/100)
    receita_adj = num_unidades * preco_adj
    custo_const_adj = area_construida * custo_adj + custos_indiretos + custos_licenciamento
    invest_adj = preco_terreno + custos_regularizacao + custo_const_adj + custos_marketing
    lucro_adj = receita_adj - invest_adj - (receita_adj * comissao_vendas)
    
    df_sens = pd.DataFrame({
        "Cenário": ["Base", f"Preço {'+' if var_price>0 else ''}{var_price}%", f"Custo {'+' if var_cost>0 else ''}{var_cost}%"],
        "Receita (R$)": [receita_total, receita_adj, receita_total],
        "Investimento (R$)": [investimento_total, investimento_total, invest_adj],
        "Lucro Bruto (R$)": [lucro_bruto, receita_adj - investimento_total - receita_adj*comissao_vendas, lucro_adj],
    })
    st.table(df_sens.style.format({"Receita (R$)": "{:,.0f}", 
                                   "Investimento (R$)": "{:,.0f}",
                                   "Lucro Bruto (R$)": "{:,.0f}"}))

st.markdown("---")
st.caption("Desenvolvido com ❤️ em Streamlit")
