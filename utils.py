import pandas as pd
from brazilcep import get_address_from_cep
import requests
import streamlit as st

GOOGLE_API_KEY = st.secrets["google_api_key"]

def buscar_endereco_google(endereco_completo):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={endereco_completo},Brazil&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            location = data["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
    return None, None

def buscar_endereco_brasil_cep(cep):
    try:
        endereco = get_address_from_cep(cep)
        return f"{endereco.get('street', '')}, {endereco.get('district', '')}, {endereco.get('city', '')}, {endereco.get('uf', '')}"
    except Exception as e:
        st.error(f"Erro ao buscar endereço no BrasilCEP: {str(e)}")
    return "Endereço não encontrado"

def process_ceps(file):
    df = pd.read_excel(file)
    df.columns = df.columns.str.strip()

    if "CEP" not in df.columns:
        st.error(f"❌ A coluna 'CEP' não foi encontrada no arquivo. Colunas encontradas: {', '.join(df.columns)}")
        st.stop()

    df["CEP"] = df["CEP"].astype(str).str.strip().str.replace(r"[^\d]", "", regex=True).str.zfill(8)
    ceps_formatados = df["CEP"].apply(lambda x: f"{x[:5]}-{x[5:]}")

    latitudes, longitudes, enderecos = [], [], {}

    for cep in ceps_formatados:
        enderecos[cep] = buscar_endereco_brasil_cep(cep)

    for cep in ceps_formatados:
        endereco_completo = enderecos[cep]
        lat, lng = buscar_endereco_google(endereco_completo)
        latitudes.append(round(lat, 6) if lat is not None else None)
        longitudes.append(round(lng, 6) if lng is not None else None)

    df["Latitude"] = latitudes
    df["Longitude"] = longitudes
    df["Endereço"] = ceps_formatados.map(enderecos)

    df["Latitude"] = df["Latitude"].apply(lambda x: f"{x:.6f}" if x is not None else None)
    df["Longitude"] = df["Longitude"].apply(lambda x: f"{x:.6f}" if x is not None else None)

    return df
