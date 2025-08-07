# app.py
import streamlit as st
import pandas as pd
from streamlit_folium import folium_static
import requests

from config import GOOGLE_MAPS_API_KEY  # Importar a chave da API do arquivo config.py

# Configuração inicial do aplicativo
st.set_page_config(
    page_title="Mapeamento de Preços em Fortaleza",
    page_icon=":cityscape:",
    layout="wide"
)

# Função para carregar dados (substitua com sua fonte de dados)
@st.cache_data
def carregar_dados():
    # Exemplo de carregamento de dados
    try:
        # Substitua por sua fonte de dados real
        dados = pd.DataFrame({
            'regiao': ['Centro', 'Aldeota', 'Meireles', 'Benfica'],
            'latitude': [-3.7272, -3.7432, -3.7335, -3.7436],
            'longitude': [-38.5275, -38.5041, -38.4989, -38.5434],
            'preco_medio': [500.00, 750.00, 1000.00, 350.00]
        })
        return dados
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

# Função para obter detalhes do Street View
def obter_street_view(latitude, longitude):
    base_url = "https://maps.googleapis.com/maps/api/streetview"
    params = {
        'size': '600x300',
        'location': f'{latitude},{longitude}',
        'key': GOOGLE_MAPS_API_KEY
    }

    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            return response.url
        else:
            return None
    except Exception as e:
        st.error(f"Erro ao obter Street View: {e}")
        return None

# Função principal do aplicativo
def main():
    st.title("🏙️ Mapeamento de Preços em Fortaleza")

    # Carregar dados
    dados = carregar_dados()

    # Sidebar para filtros
    st.sidebar.header("Filtros")

    # Seleção de região
    regioes_selecionadas = st.sidebar.multiselect(
        "Selecione as Regiões:",
        options=dados['regiao'].unique(),
        default=dados['regiao'].unique()
    )

    # Filtrar dados
    dados_filtrados = dados[dados['regiao'].isin(regioes_selecionadas)]

    # Criar mapa
    map_fortaleza = folium.Map(
        location=[-3.7272, -38.5275],
        zoom_start=12
    )

    # Adicionar marcadores
    for idx, row in dados_filtrados.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"Região: {row['regiao']}\nPreço Médio: R${row['preco_medio']:.2f}",
            tooltip=row['regiao']
        ).add_to(map_fortaleza)

    # Exibir mapa
    folium_static(map_fortaleza)

    # Visualização de dados
    st.subheader("Detalhes dos Preços")
    st.dataframe(dados_filtrados)

    # Street View para locais selecionados
    st.subheader("Street View das Regiões")

    # Colunas para exibição de Street View
    cols = st.columns(len(dados_filtrados))

    for i, (_, row) in enumerate(dados_filtrados.iterrows()):
        with cols[i]:
            street_view_url = obter_street_view(row['latitude'], row['longitude'])
            if street_view_url:
                st.image(street_view_url, caption=row['regiao'])

            st.metric(
                label=f"Preço Médio - {row['regiao']}",
                value=f"R$ {row['preco_medio']:.2f}"
            )

# Executar o aplicativo
if __name__ == "__main__":
    main()
