import streamlit as st
import pandas as pd
import requests

def buscar_lat_lon(cep):
    # Utilizando a API do OpenCage ou similar
    try:
        # Aqui está um exemplo genérico com o Nominatim (OpenStreetMap)
        response = requests.get(f"https://nominatim.openstreetmap.org/search?postalcode={cep}&country=Brazil&format=json")
        data = response.json()
        if data:
            return data[0]['lat'], data[0]['lon']
        else:
            return None, None
    except:
        return None, None

st.title("Conversor de CEPs para Coordenadas Geográficas")

arquivo = st.file_uploader("Envie seu arquivo XLSX com a coluna 'cep'", type=["xlsx"])

if arquivo:
    df = pd.read_excel(arquivo)

    if 'cep' not in df.columns:
        st.error("A planilha precisa conter uma coluna chamada 'cep'.")
    else:
        st.write("Processando os CEPs...")
        df['cep'] = df['cep'].astype(str).str.replace(r'\D', '', regex=True).str.zfill(8)
        df['latitude'], df['longitude'] = zip(*df['cep'].apply(buscar_lat_lon))
        
        st.success("Processamento concluído!")
        st.dataframe(df)

        # Download
        output_file = "ceps_com_coordenadas.xlsx"
        df.to_excel(output_file, index=False)

        with open(output_file, "rb") as f:
            st.download_button("📥 Baixar arquivo com coordenadas", f, file_name=output_file)
