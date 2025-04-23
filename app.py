import streamlit as st
import pandas as pd
from pycep_correios import get_address_from_cep, WebService, exceptions
from urllib3.exceptions import InsecureRequestWarning
import urllib3
import requests
from photon import geocode

# Desativar warnings SSL
urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

st.set_page_config(page_title="Conversor de CEPs", layout="centered")
st.title("🔍 Conversor de CEP para Latitude/Longitude")

uploaded_file = st.file_uploader("📤 Carregue sua planilha com CEPs (.xlsx)", type=["xlsx"])

def consultar_endereco(cep):
    try:
        endereco = get_address_from_cep(cep, webservice=WebService.APICEP)
        return f"{endereco['logradouro']} {endereco['cidade']} Brasil"
    except exceptions.BaseException:
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
    
    # Garantir que a coluna se chame 'cep' (ou ajustar)
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
        
        # Merge com o original para manter os dados completos
        df_final = df.merge(df_resultado, on="cep", how="left")
        
        st.success("✅ Conversão finalizada!")
        st.dataframe(df_final)
        
        # Baixar resultado
        st.download_button(
            label="📥 Baixar resultado como Excel",
            data=df_final.to_excel(index=False),
            file_name="ceps_com_coordenadas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
