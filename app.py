import streamlit as st
import pandas as pd
import requests
import time

# Substitua pela sua chave da API do Google Maps
GOOGLE_API_KEY = st.secrets["google_api_key"]

def buscar_lat_lon_google(cep, api_key):
    time.sleep(1.5)  # Atraso para evitar problemas de cache
    try:
        # Monta a URL para consulta na API do Google Geocoding
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={cep},Brazil&key={api_key}"

        # Realiza a requisição para a API
        response = requests.get(url)
        data = response.json()

        # Verifica se a consulta foi bem-sucedida
        if data['status'] == 'OK':
            # Extrai as coordenadas (latitude e longitude)
            lat = data['results'][0]['geometry']['location']['lat']
            lon = data['results'][0]['geometry']['location']['lng']

            # Exibe o CEP e as coordenadas na tela
            st.write(f"CEP: {cep}, Latitude: {lat}, Longitude: {lon}")

            return lat, lon
        else:
            # Exibe o status da API se houver um erro
            st.write(f"Erro na API para o CEP {cep}: {data['status']}")
            return None, None
    except Exception as e:
        # Captura qualquer exceção e exibe erro no Streamlit
        st.error(f"Erro ao consultar o CEP {cep}: {e}")
        return None, None

# Streamlit UI
st.set_page_config(page_title="Conversor de CEPs", layout="centered")
st.title("📍 Conversor de CEPs para Latitude e Longitude")

# Upload de arquivo
arquivo = st.file_uploader("Envie sua planilha XLSX com a coluna 'cep'", type=["xlsx"])

if arquivo:
    df = pd.read_excel(arquivo)

    # Verifica se a coluna 'cep' está presente na planilha
    if 'cep' not in df.columns:
        st.error("A planilha precisa conter uma coluna chamada 'cep'.")
    else:
        st.info("Processando os CEPs... isso pode levar alguns segundos.")

        # Limpa os CEPs, garantindo que sejam 8 dígitos
        df['cep'] = df['cep'].astype(str).str.replace(r'\D', '', regex=True).str.zfill(8)

        # Obtém a lista de CEPs únicos
        ceps_unicos = df['cep'].unique()

        # Inicializa listas para latitude e longitude
        latitudes = []
        longitudes = []

        # Faz a consulta de coordenadas para cada CEP único
        for cep in ceps_unicos:
            lat, lon = buscar_lat_lon_google(cep, GOOGLE_API_KEY)
            latitudes.append(lat)
            longitudes.append(lon)

        # Cria um DataFrame com os CEPs únicos e suas coordenadas
        df_coords = pd.DataFrame({'cep': ceps_unicos, 'latitude': latitudes, 'longitude': longitudes})

        # Mescla as coordenadas com o DataFrame original
        df = pd.merge(df, df_coords, on='cep', how='left')

        st.success("Processamento concluído com sucesso!")
        st.dataframe(df)

        # Exporta a planilha com coordenadas
        output_file = "ceps_com_coordenadas_google.xlsx"
        df.to_excel(output_file, index=False)

        with open(output_file, "rb") as f:
            st.download_button("Baixar planilha com coordenadas", f, file_name=output_file)
