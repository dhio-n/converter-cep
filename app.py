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
        st.write(f"📦 Dados brutos do CEP {cep}: {endereco}")  # Log para depuração

        # Campos com fallback vazio
        street = endereco.get('street') or ''
        district = endereco.get('district') or ''
        city = endereco.get('city') or ''
        uf = endereco.get('uf') or ''
        cep_str = endereco.get('cep') or ''

        # Validar campos mínimos para geocodificação
        if not city or not uf:
            st.warning(f"⚠️ Endereço incompleto para o CEP {cep}. Cidade ou estado ausentes.")
            return "-"

        # Monta o endereço completo
        endereco_str = f"{street}, {district}, {city}, {uf}, {cep_str}, Brasil"
        st.write(f"📍 Endereço gerado: {endereco_str}")
        return endereco_str
    except Exception as e:
        st.error(f"❌ Erro ao consultar o endereço para o CEP {cep}: {e}")
        return "-"

# Função para converter CEP em coordenadas
def cep_para_coordenadas(cep):
    endereco = consultar_endereco(cep)
    if endereco == "-":
        return None, None
    try:
        location = geolocator.geocode(endereco)
        if location:
            st.write(f"✅ Localização: {location.latitude}, {location.longitude}")
            return location.latitude, location.longitude
        else:
            st.warning(f"❌ Nenhuma localização encontrada para o endereço: {endereco}")
            return None, None
    except Exception as e:
        st.error(f"❌ Erro na geocodificação para o CEP {cep}: {e}")
        return None, None

# Upload do arquivo Excel
uploaded_file = st.file_uploader("📤 Carregue sua planilha com uma coluna chamada 'cep'", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    if 'cep' not in df.columns:
        st.error("❌ A planilha deve conter uma coluna chamada 'cep'.")
    else:
        # Padronizar CEPs
        df['cep'] = df['cep'].astype(str).str.replace("-", "").str.zfill(8)

        st.info("🔄 Processando CEPs únicos...")
        ceps_unicos = df['cep'].unique()

        resultados = []
        for i, cep in enumerate(ceps_unicos, 1):
            lat, lon = cep_para_coordenadas(cep)
            resultados.append({"cep": cep, "latitude": lat, "longitude": lon})
            st.write(f"📌 ({i}/{len(ceps_unicos)}) CEP: {cep} - Lat: {lat} | Lon: {lon}")

        # Criar dataframe com resultados
        df_resultado = pd.DataFrame(resultados)
        df_resultado["cep"] = df_resultado["cep"].astype(str).str.replace("-", "").str.zfill(8)

        # Merge com o original
        df_final = df.merge(df_resultado, on="cep", how="left")

        st.success("✅ Conversão finalizada!")
        st.dataframe(df_final)

        # Download
        output = BytesIO()
        df_final.to_excel(output, index=False)
        st.download_button(
            label="📥 Baixar resultado como Excel",
            data=output.getvalue(),
            file_name="ceps_com_coordenadas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
