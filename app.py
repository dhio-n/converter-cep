import streamlit as st
import pandas as pd
import requests
import time

# Lê a chave da API diretamente dos secrets do Streamlit Cloud
OPENCAGE_API_KEY = st.secrets["api_key"]

def buscar_lat_lon(cep):
    try:
        # URL da API com o CEP e a chave
        url = f"https://api.opencagedata.com/geocode/v1/json?q={cep},+Brazil&key={OPENCAGE_API_KEY}"
        response = requests.get(url)
        data = response.json()

        # Verifica se há resultados válidos na resposta
        if data["results"]:
            lat = data["results"][0]["geometry"]["lat"]
            lon = data["results"][0]["geometry"]["lng"]
            return lat, lon
        else:
            # Caso não haja resultados, retorna None
            return None, None
    except Exception as e:
        # Caso ocorra erro, retorna None e exibe a exceção
        st.error(f"Erro ao consultar o CEP {cep}: {e}")
        return None, None

# Streamlit UI
st.set_page_config(page_title="Conversor de CEPs", layout="centered")
st.title("📍 Conversor de CEPs para Latitude e Longitude")

# Upload de arquivo
arquivo = st.file_uploader("Envie sua planilha XLSX com a coluna 'cep'", type=["xlsx"])

if arquivo:
    df = pd.read_excel(arquivo)

    # Verifica se a coluna 'cep' está presente
    if 'cep' not in df.columns:
        st.error("A planilha precisa conter uma coluna chamada 'cep'.")
    else:
        st.info("Processando os CEPs... isso pode levar alguns segundos.")
        
        # Limpa os CEPs, garantindo que sejam 8 dígitos
        df['cep'] = df['cep'].astype(str).str.replace(r'\D', '', regex=True).str.zfill(8)

        # Consulta apenas CEPs únicos
        ceps_unicos = df['cep'].unique()
        coord_dict = {}

        for cep in ceps_unicos:
            lat, lon = buscar_lat_lon(cep)
            coord_dict[cep] = (lat, lon)
            time.sleep(1.1)  # Evita atingir o limite da API

        # Aplica as coordenadas no DataFrame original
        df['latitude'] = df['cep'].map(lambda x: coord_dict.get(x, (None, None))[0])
        df['longitude'] = df['cep'].map(lambda x: coord_dict.get(x, (None, None))[1])

        st.success("Processamento concluído com sucesso!")
        st.dataframe(df)

        # Exporta planilha com coordenadas
        output_file = "ceps_com_coordenadas.xlsx"
        df.to_excel(output_file, index=False)

        with open(output_file, "rb") as f:
            st.download_button("📥 Baixar planilha com coordenadas", f, file_name=output_file)
