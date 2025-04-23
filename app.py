import streamlit as st
import pandas as pd
import requests
import time

# Lê a chave da API diretamente dos secrets do Streamlit
OPENCAGE_API_KEY = st.secrets["api_key"]

def buscar_lat_lon(cep):
    try:
        url = f"https://api.opencagedata.com/geocode/v1/json?q={cep},+Brazil&key={OPENCAGE_API_KEY}"
        response = requests.get(url)
        data = response.json()

        if data["results"]:
            lat = data["results"][0]["geometry"]["lat"]
            lon = data["results"][0]["geometry"]["lng"]
            return lat, lon
        else:
            return None, None
    except:
        return None, None

st.set_page_config(page_title="Conversor de CEPs", layout="centered")
st.title("📍 Conversor de CEPs para Latitude e Longitude")

arquivo = st.file_uploader("Envie sua planilha XLSX com a coluna 'cep'", type=["xlsx"])

if arquivo:
    df = pd.read_excel(arquivo)

    if 'cep' not in df.columns:
        st.error("A planilha precisa conter uma coluna chamada 'cep'.")
    else:
        st.info("Processando os CEPs...")

        df['cep'] = df['cep'].astype(str).str.replace(r'\D', '', regex=True).str.zfill(8)
        
        latitudes = []
        longitudes = []
        
        for cep in df['cep']:
            lat, lon = buscar_lat_lon(cep)
            latitudes.append(lat)
            longitudes.append(lon)
            time.sleep(1.1)  # Respeita limites da API gratuita

        df['latitude'] = latitudes
        df['longitude'] = longitudes

        st.success("Processamento concluído!")
        st.dataframe(df)

        # Exporta planilha com coordenadas
        output_file = "ceps_com_coordenadas.xlsx"
        df.to_excel(output_file, index=False)

        with open(output_file, "rb") as f:
            st.download_button("📥 Baixar planilha com coordenadas", f, file_name=output_file)
