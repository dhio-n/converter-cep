import pandas as pd
import streamlit as st
import brazilcep
import requests
import time
from io import BytesIO

def get_coordinates_from_address(address, max_retries=3, wait_seconds=2):
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }

    headers = {
        "User-Agent": "CEP-Geocoder/1.0 (contato@seudominio.com)"
    }

    for attempt in range(max_retries):
        try:
            response = requests.get(base_url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data:
                return data[0]["lat"], data[0]["lon"]
            else:
                return None, None
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Tentativa {attempt+1}/{max_retries} falhou para '{address}': {e}")
            if attempt < max_retries - 1:
                time.sleep(wait_seconds)
            else:
                return None, None

def process_ceps(file):
    df = pd.read_excel(file)
    ceps = df["CEP"].astype(str)

    resultado = []
    for i, cep in enumerate(ceps, start=1):
        try:
            address_info = brazilcep.get_address_from_cep(cep)
            address_str = f"{address_info['street']}, {address_info['district']}, {address_info['city']}, {address_info['uf']}, {address_info['cep']}, Brasil"
            lat, lon = get_coordinates_from_address(address_str)

            resultado.append({
                "CEP": cep,
                "Endereço": address_str,
                "Latitude": lat,
                "Longitude": lon
            })
            print(f"📌 ({i}/{len(ceps)}) CEP: {cep} - Lat: {lat} | Lon: {lon}")

        except Exception as e:
            print(f"❌ Erro ao processar o CEP {cep}: {e}")
            resultado.append({
                "CEP": cep,
                "Endereço": "Erro ao buscar endereço",
                "Latitude": None,
                "Longitude": None
            })

    return pd.DataFrame(resultado)

# Streamlit App
st.set_page_config(page_title="Geocodificador de CEPs", layout="centered")
st.title("📍 Geocodificador de CEPs com Latitude e Longitude")

st.markdown("""
Envie um arquivo `.xlsx` com uma **coluna chamada `CEP`**. O sistema vai buscar o endereço, latitude e longitude de cada CEP.
""")

file = st.file_uploader("📤 Enviar arquivo Excel", type=["xlsx"])

if file:
    with st.spinner("🔄 Processando os CEPs..."):
        df_resultado = process_ceps(file)

    st.success("✅ Processamento concluído!")
    st.dataframe(df_resultado)

    # Geração do arquivo para download
    output = BytesIO()
    df_resultado.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)

    st.download_button(
        label="📥 Baixar resultado em Excel",
        data=output,
        file_name="ceps_geocodificados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
