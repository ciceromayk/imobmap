import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as npf  # Para cálculos financeiros

st.set_page_config(page_title="Viabilidade Imobiliária", layout="wide")
st.title("Análise de Viabilidade de Empreendimentos Imobiliários")

# =============================================================================
# 1. Dados do Terreno
# =============================================================================
st.sidebar.header("Dados do Terreno")
preco_terreno = st.sidebar.number_input(
    "Preço de aquisição do terreno (R$)",
    value=1_000_000.0,
    step=10_000.0,
    format="%.2f"
)
area_terreno = st.sidebar.number_input(
    "Área total do terreno (m²)",
    value=1000.0,
    step=10.0
)
custos_regularizacao = st.sidebar.number_input(
    "Custos de regularização (R$)",
    value=50_000.0,
    step=1_000.0,
    format="%.2f"
)

# =============================================================================
# 2. Dados do Projeto
# =============================================================================
st.sidebar.header("Dados do Projeto")
area_construida = st.sidebar.number_input(
    "Área total construída (m²)",
    value=5000.0,
    step=100.0
)
area_privativa = st.sidebar.number_input(
    "Área privativa total (m²)",
    value=3000.0,
    step=100.0
)
num_unidades = st.sidebar.number_input(
    "Número de unidades",
    value=50,
    step=1
)

st.sidebar.subheader("Tipologia das Unidades")
st.sidebar.info(
    "Utilize o formato:\n"
    "Tipologia: Quantidade, Área Média\n"
    "Exemplos:\n"
    "1Q + Sala: 20, 60\n"
    "2Q + Sala: 20, 80\n"
    "3Q + Sala: 10, 100"
)
tipos_text = st.sidebar.text_area(
    "Defina as tipologias:",
    value="1Q + Sala: 20, 60\n2Q + Sala: 20, 80\n3Q + Sala: 10, 100",
    help="Cada linha representa uma tipologia: nome, quantidade, área média (m²)"
)

def parse_tipologias(text):
    linhas = text.strip().split("\n")
    data = {"Tipologia": [], "Qtd Unidades": [], "Área Média (m²)": []}
    for linha in linhas:
        try:
            nome, valores = linha.split(":")
            q, area = valores.split(",")
            data["Tipologia"].append(nome.strip())
            data["Qtd Unidades"].append(int(q.strip()))
            data["Área Média (m²)"].append(float(area.strip()))
        except Exception as e:
            pass
    return pd.DataFrame(data)

df_tipologias = parse_tipologias(tipos_text)

# =============================================================================
# 3. Custos de Construção
# =============================================================================
st.sidebar.header("Custos de Construção")
custo_construcao_m2 = st.sidebar.number_input(
    "Custo de construção (R$/m²)",
    value=2000.0,
    step=100.0,
    format="%.2f"
)
custos_indiretos = st.sidebar.number_input(
    "Custos indiretos (R$)",
    value=200_000.0,
    step=1_000.0,
    format="%.2f"
)
custos_licenciamento = st.sidebar.number_input(
    "Custos de projeto e licenciamento (R$)",
    value=100_000.0,
    step=1_000.0,
    format="%.2f"
)

# =============================================================================
# 4. Vendas e Marketing
# =============================================================================
st.sidebar.header("Vendas e Marketing")
comissao_vendas = st.sidebar.number_input(
    "Comissão de vendas (%)",
    value=2.0,
    step=0.1,
    format="%.1f"
) / 100.0
custos_marketing = st.sidebar.number_input(
    "Custos de marketing (R$)",
    value=50_000.0,
    step=1_000.0,
    format="%.2f"
)

# =============================================================================
# 5. Parâmetros Financeiros
# =============================================================================
st.sidebar.header("Parâmetros Financeiros")
taxa_juros = st.sidebar.number_input(
    "Taxa de juros anual (%)",
    value=10.0,
    step=0.1,
    format="%.1f"
) / 100.0
preco_venda_medio = st.sidebar.number_input(
    "Preço médio de venda por unidade (R$)",
    value=350_000.0,
    step=5_000.0,
    format="%.2f"
)

# =============================================================================
# Exibição dos Dados de Entrada
# =============================================================================
st.markdown("---")
st.header("Dados de Entrada")
with st.expander("Ver detalhes dos dados informados"):
    st.subheader("Terreno")
    st.write(f"Preço do Terreno: R$ {preco_terreno:,.2f}")
    st.write(f"Área do Terreno: {area_terreno} m²")
    st.write(f"Custos de Regularização: R$ {custos_regularizacao:,.2f}")
    
    st.subheader("Projeto")
    st.write(f"Área Construída: {area_construida} m²")
    st.write(f"Área Privativa: {area_privativa} m²")
    st.write(f"Número de Unidades: {num_unidades}")
    st.write("Tipologias:")
    st.dataframe(df_tipologias)
    
    st.subheader("Construção")
    st.write(f"Custo de Construção: R$ {custo_construcao_m2:,.2f} por m²")
    st.write(f"Custos Indiretos: R$ {custos_indiretos:,.2f}")
    st.write(f"Licenciamento: R$ {custos_licenciamento:,.2f}")
    
    st.subheader("Vendas e Marketing")
    st.write(f"Comissão de Vendas: {comissao_vendas * 100:.1f}%")
    st.write(f"Custos de Marketing: R$ {custos_marketing:,.2f}")
    
    st.subheader("Parâmetros Financeiros")
    st.write(f"Taxa de Juros Anual: {taxa_juros * 100:.1f}%")
    st.write(f"Preço Médio de Venda: R$ {preco_venda_medio:,.2f}")

# =============================================================================
# 6. Cálculos de Viabilidade
# =============================================================================
st.markdown("---")
st.header("Indicadores de Viabilidade")

# Custo de construção total (construção + indiretos + licenciamento)
construcao_total = area_construida * custo_construcao_m2
investimento_construcao = construcao_total + custos_indiretos + custos_licenciamento

# Investimento total (terreno + regularização + construção + marketing)
investimento_total = preco_terreno + custos_regularizacao + investimento_construcao + custos_marketing

# Receita Total de Vendas
receita_total = num_unidades * preco_venda_medio

# Valor da Comissão de Vendas
valor_comissao = receita_total * comissao_vendas

# Lucro Bruto (antes de considerar impostos e demais custos)
lucro_bruto = receita_total - investimento_total - valor_comissao

# Exibição dos indicadores básicos
col1, col2, col3 = st.columns(3)
col1.metric("Investimento Total (R$)", f"{investimento_total:,.2f}")
col2.metric("Receita Total (R$)", f"{receita_total:,.2f}")
col3.metric("Lucro Bruto (R$)", f"{lucro_bruto:,.2f}")

# -----------------------------------------------------------------------------
st.subheader("Análise Financeira")
# Para simplificar, simulamos um fluxo de caixa com:
# T0: investimento negativo, T1: receita líquida (receita total - comissão)
fluxos = [-investimento_total, receita_total - valor_comissao]

# Cálculo do VPL e TIR
npv_valor = npf.npv(taxa_juros, fluxos)
irr_valor = npf.irr(fluxos)

st.write("**Valor Presente Líquido (VPL):**")
st.write(f"R$ {npv_valor:,.2f}")
st.write("**Taxa Interna de Retorno (TIR):**")
st.write(f"{irr_valor*100:.2f}%")

# Payback simples (em anos)
if (receita_total - valor_comissao) > 0:
    payback = investimento_total / (receita_total - valor_comissao)
    st.write("**Payback Simples:**")
    st.write(f"{payback:.2f} anos")
else:
    st.write("**Payback:** Não aplicável (fluxo de caixa negativo)")

st.markdown("---")
st.caption("Aplicativo de Análise de Viabilidade de Empreendimentos Imobiliários desenvolvido com Streamlit.")
