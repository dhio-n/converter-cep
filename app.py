import streamlit as st
import pandas as pd
import brazilcep
from geopy.geocoders import Nominatim
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from io import BytesIO

# Desativar avisos de SSL
urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Configurações iniciais
st.set_page_config(page_title="Conversor de CEPs", layout="centered")
st.title("📍 Conversor de CEPs para Latitude/Longitude")

# Geolocalizador
geolocator = Nominatim(user_agent="app_streamlit_cep")

# Função para obter endereço a partir do CEP
def consultar_endereco(cep):
    try:
        endereco = brazilcep.get_address_from_cep(cep)
        return f"{endereco['street']} {endereco['city']} Brasil"
    except:
        return "-"

# Função para converter CEP em coordenadas
def cep_para_coordenadas(cep):
    endereco = consultar_endereco(cep)
    if endereco == "-":
        return None, None
    try:
        location = geolocator.geocode(endereco)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except:
        return None, None

# Upload do arquivo Excel
uploaded_file = st.file_uploader("📤 Carregue sua planilha com uma coluna chamada 'cep'", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    if 'cep' not in df.columns:
        st.error("A planilha deve conter uma coluna chamada 'cep'.")
    else:
        st.info("🔄 Processando CEPs únicos...")
        ceps_unicos = df['cep'].astype(str).str.replace("-", "").str.zfill(8).unique()

        resultados = []
        for i, cep in enumerate(ceps_unicos, 1):
            lat, lon = cep_para_coordenadas(cep)
            resultados.append({"cep": cep, "latitude": lat, "longitude": lon})
            st.write(f"✅ ({i}/{len(ceps_unicos)}) CEP: {cep} - Lat: {lat} | Lon: {lon}")

        df_resultado = pd.DataFrame(resultados)
        df_final = df.merge(df_resultado, on="cep", how="left")

        st.success("✅ Conversão finalizada!")
        st.dataframe(df_final)

        # Preparar download do Excel
        output = BytesIO()
        df_final.to_excel(output, index=False)
        st.download_button(
            label="📥 Baixar resultado como Excel",
            data=output.getvalue(),
            file_name="ceps_com_coordenadas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
