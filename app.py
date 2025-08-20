import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Viabilidade Residencial", layout="wide")
st.title("🚀 Viabilidade de Empreendimentos Residenciais")

# === 1. Entrada de Dados Gerais e Financeiros ===
with st.sidebar:
    st.header("Parâmetros do Projeto e Finanças")
    
    st.subheader("Dimensões e Estrutura")
    area_construida = st.number_input(
        "Área construída total (m²)", min_value=0.0, value=5000.0, step=100.0
    )
    area_privativa = st.number_input(
        "Área privativa total (m²)", min_value=0.0, value=3000.0, step=100.0
    )
    num_unidades = st.number_input(
        "Número de unidades residenciais", min_value=1, value=50, step=1
    )
    
    st.subheader("Garagem e Elevadores")
    garagem_tipo = st.selectbox(
        "Tipo de garagem",
        ("Subsolo", "Sobressolo", "Prédio Garagem")
    )
    num_vagas = st.number_input(
        "Total de vagas de garagem", min_value=0, value=75, step=1
    )
    num_elevadores = st.number_input(
        "Número de elevadores", min_value=0, value=2, step=1
    )
    
    st.subheader("Investimentos e Custos")
    custo_terreno = st.number_input(
        "Custo do terreno (R$)", min_value=0.0, value=1_000_000.0, step=10000.0, format="%.2f"
    )
    custo_construcao_m2 = st.number_input(
        "Custo de construção (R$/m²)", min_value=0.0, value=2000.0, step=100.0, format="%.2f"
    )
    preco_venda_medio = st.number_input(
        "Preço médio de venda por unidade (R$)", min_value=0.0, value=350_000.0, step=5000.0, format="%.2f"
    )
    
    st.subheader("Parâmetros do Projeto")
    tipologia_garagem = st.radio(
        "Configuração da garagem",
        ("1 nível", "2 níveis", "Multi-nível")
    )

st.markdown("---")

# === 2. Descrição das Unidades ===
st.subheader("Descrição das Unidades")
st.markdown("Informe, por tipologia, quantas unidades e as áreas médias correspondentes.")
default_tipos = {
    "Tipologia": ["1Q + Sala", "2Q + Sala", "3Q + Sala"],
    "Qtd Unidades": [20, 20, 10],
    "Área Média (m²)": [60, 80, 100],
}

try:
    df_tipos = st.experimental_data_editor(
        pd.DataFrame(default_tipos),
        num_rows="dynamic",
        use_container_width=True
    )
except AttributeError:
    st.warning(
        "A funcionalidade de edição direta de dados não está disponível "
        "na versão do Streamlit que você está usando."
    )
    df_tipos = pd.DataFrame(default_tipos)
    st.dataframe(df_tipos, use_container_width=True)

# === 3. Cálculos dos Indicadores e Viabilidade ===
st.subheader("Indicadores de Viabilidade")

# Indicadores estruturais
area_media_unidade = area_construida / num_unidades
vagas_por_unidade = num_vagas / num_unidades if num_unidades else np.nan
elevadores_por_unidade = num_elevadores / num_unidades if num_unidades else np.nan

# Composição de áreas por tipologia
df_tipos["% Área Total"] = (
    df_tipos["Qtd Unidades"] * df_tipos["Área Média (m²)"]
) / area_construida * 100

# Indicadores financeiros
custo_construcao_total = area_construida * custo_construcao_m2
investimento_total = custo_terreno + custo_construcao_total
receita_estimadas = num_unidades * preco_venda_medio
lucro_estimado = receita_estimadas - investimento_total
custo_por_unidade = investimento_total / num_unidades

# Exibição dos indicadores
col1, col2, col3 = st.columns(3)
col1.metric("Área média/unidade (m²)", f"{area_media_unidade:.1f}")
col2.metric("Vagas por unidade", f"{vagas_por_unidade:.2f}")
col3.metric("Elevadores/unidade", f"{elevadores_por_unidade:.3f}")

st.markdown("**Distribuição de área por tipologia:**")
st.dataframe(
    df_tipos.style.format({
        "Área Média (m²)": "{:.1f}",
        "% Área Total": "{:.1f}%"
    }),
    use_container_width=True
)

st.markdown("---")
st.subheader("Análise Financeira")
st.write(f"**Custo total de construção:** R$ {custo_construcao_total:,.2f}")
st.write(f"**Investimento total (terreno + construção):** R$ {investimento_total:,.2f}")
st.write(f"**Receita estimada (venda de unidades):** R$ {receita_estimadas:,.2f}")
st.write(f"**Lucro estimado:** R$ {lucro_estimado:,.2f}")
st.write(f"**Custo por unidade:** R$ {custo_por_unidade:,.2f}")

# === 4. Alertas e Recomendações ===
st.subheader("Alertas e Recomendações")

if vagas_por_unidade < 1:
    st.warning("Média de vagas inferior a 1 por unidade. Verifique o atendimento mínimo.")

if elevadores_por_unidade < 0.05:
    st.warning("Poucos elevadores para o número de unidades; considere aumentar.")

if garagem_tipo == "Subsolo" and area_construida > 10000:
    st.info("Subsolo em grandes áreas pode elevar custos de escavação.")

if lucro_estimado < 0:
    st.error("Projeto apresenta prejuízo. Avalie custos ou preços de venda.")
elif lucro_estimado / investimento_total < 0.1:
    st.warning("Margem de lucro baixa. Considere revisar custos e preços.")

st.info(
    "Recomenda-se análise detalhada dos custos de construção "
    "e pesquisa de mercado atualizada para confirmar preços de venda."
)

# === 5. Futuras Evoluções ===
st.markdown("---")
st.caption("Feito com ❤️ por sua equipe de engenharia de software.")
