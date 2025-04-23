import streamlit as st
import pandas as pd
from brazilcep import get_address_from_cep, WebService
import requests
import io

GOOGLE_API_KEY = st.secrets["google_api_key"]

def buscar_endereco_google(endereco_completo):
    # Consulta a API do Google para obter latitude, longitude e endereço completo a partir do endereço
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={endereco_completo},Brazil&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            location = data["results"][0]["geometry"]["location"]
            latitude = location["lat"]
            longitude = location["lng"]
            return latitude, longitude
    return None, None

def buscar_endereco_brasil_cep(cep):
    # Utiliza o BrasilCEP apenas para obter o endereço completo
    try:
        endereco = get_address_from_cep(cep)
        if endereco:
            endereco_completo = f"{endereco.get('street', '')}, {endereco.get('district', '')}, {endereco.get('city', '')}, {endereco.get('uf', '')}"

        return endereco_completo
    except Exception as e:
        st.error(f"Erro ao buscar endereço no BrasilCEP: {str(e)}")
    return "Endereço não encontrado"

def process_ceps(file):
    df = pd.read_excel(file)
    df.columns = df.columns.str.strip()
    
    if "CEP" not in df.columns:
        st.error(f"❌ A coluna 'CEP' não foi encontrada no arquivo. Colunas encontradas: {', '.join(df.columns)}")
        st.stop()

    # Normaliza os CEPs: remove espaços e garante formato com hífen
    df["CEP"] = df["CEP"].astype(str).str.strip().str.replace(r"[^\d]", "", regex=True).str.zfill(8)
    ceps_formatados = df["CEP"].apply(lambda x: f"{x[:5]}-{x[5:]}")
    
    latitudes = []
    longitudes = []
    enderecos = {}

    st.markdown("### 🔍 Processando CEPs:")

   ''' for cep in ceps_formatados:
        endereco_completo = buscar_endereco_brasil_cep(cep)
        enderecos[cep] = endereco_completo
        st.markdown(f"✅ **{cep}** → `{endereco_completo}`")
        '''

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
