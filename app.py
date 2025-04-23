import streamlit as st
import pandas as pd
from brazilcep import get_address_from_cep, WebService
import requests
import io

GOOGLE_API_KEY = st.secrets["google_api_key"]

# Função para buscar a latitude e longitude usando a API do Google a partir do endereço
def buscar_endereco_google(endereco):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={endereco}&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            location = data["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
    return None, None

# Função que tenta buscar as coordenadas usando brazilcep e, se necessário, a API do Google
def buscar_lat_lng(cep):
    try:
        endereco = get_address_from_cep(cep, webservice=WebService.APICEP)
        if endereco is None:
            raise ValueError("CEP não encontrado na primeira tentativa")
        
        # Extraindo o endereço completo fornecido pelo brazilcep
        endereco_completo = endereco.get("logradouro", "") + ", " + endereco.get("bairro", "") + ", " + endereco.get("cidade", "") + ", " + endereco.get("uf", "")
        
        # Buscando a latitude e longitude do endereço completo via API do Google
        latitude, longitude = buscar_endereco_google(endereco_completo)
        
        if latitude and longitude:
            return latitude, longitude
    except Exception as e:
        pass
    return None, None

# Função para processar o arquivo e adicionar as coordenadas
def process_ceps(file):
    df = pd.read_excel(file)
    df.columns = df.columns.str.strip()
    
    if "CEP" not in df.columns:
        st.error(f"❌ A coluna 'CEP' não foi encontrada no arquivo. Colunas encontradas: {', '.join(df.columns)}")
        st.stop()

    ceps = df["CEP"].astype(str)
    latitudes = []
    longitudes = []

    for cep in ceps:
        lat, lng = buscar_lat_lng(cep)
        # Garantir que a latitude e longitude tenham 6 casas decimais
        latitudes.append(round(lat, 6) if lat is not None else None)
        longitudes.append(round(lng, 6) if lng is not None else None)

    df["Latitude"] = latitudes
    df["Longitude"] = longitudes
    return df

# Função principal do Streamlit
def main():
    st.set_page_config(page_title="Conversor de CEP para Coordenadas", layout="centered")
    st.title("📍 Conversor de CEPs para Coordenadas")
    st.write("Carregue um arquivo Excel com a coluna `CEP` para obter as coordenadas geográficas.")

    uploaded_file = st.file_uploader("Escolha um arquivo Excel (.xlsx)", type="xlsx")

    if uploaded_file:
        with st.spinner("Processando..."):
            try:
                df_resultado = process_ceps(uploaded_file)
                st.success("Conversão concluída!")
                st.dataframe(df_resultado)

                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_resultado.to_excel(writer, index=False, sheet_name='Resultados')
                st.download_button("📥 Baixar resultados", output.getvalue(), "coordenadas.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            except Exception as e:
                st.error(f"Erro ao processar: {e}")

if __name__ == "__main__":
    main()
