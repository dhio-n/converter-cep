import streamlit as st
import pandas as pd
import brazilcep
from photon import geocode
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# Desativar warnings de SSL
urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

st.set_page_config(page_title="Conversor de CEPs", layout="centered")
st.title("📍 Conversor de CEPs para Latitude/Longitude")

uploaded_file = st.file_uploader("📤 Carregue sua planilha com uma coluna chamada 'cep'", type=["xlsx"])

def consultar_endereco(cep):
    try:
        endereco = brazilcep.get_address_from_cep(cep)
        return f"{endereco['street']} {endereco['city']} Brasil"
    except:
        return "-"

def cep_para_coordenadas(cep):
    endereco = consultar_endereco(cep)
    if endereco == "-":
        return None, None
    resultado = geocode(endereco, limit=1)
    if resultado.empty:
        return None, None
    return resultado.lat[0], resultado.lon[0]

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

        # Download da planilha com coordenadas
        st.download_button(
            label="📥 Baixar resultado como Excel",
            data=df_final.to_excel(index=False),
            file_name="ceps_com_coordenadas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
