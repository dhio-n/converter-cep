import streamlit as st
import pandas as pd
import io
import os
import base64

from auth import autenticar_usuario
from utils import process_ceps
from database import conectar

GOOGLE_API_KEY = st.secrets["google_api_key"]

# =========================
# TELA DE LOGIN
# =========================
def tela_login():
    caminho_logo = os.path.join("assets", "LOGO2.png")

    if os.path.exists(caminho_logo):
        with open(caminho_logo, "rb") as image_file:
            encoded_logo = base64.b64encode(image_file.read()).decode()
        st.markdown(f"""
            <style>
                .stApp {{
                    background-image: url("data:image/png;base64,{encoded_logo}");
                    background-size: cover;
                    background-position: center;
                    background-repeat: no-repeat;
                }}
                .block-container {{
                    background-color: rgba(255, 255, 255, 0.85);
                    padding: 2rem;
                    border-radius: 10px;
                    max-width: 400px;
                    margin: auto;
                    margin-top: 100px;
                }}
            </style>
        """, unsafe_allow_html=True)

    st.subheader("🔐 Gerador de número de série - Mundial Refrigeração - Login")
    usuario = st.text_input("Usuário", key="login_usuario")
    senha = st.text_input("Senha", type="password", key="login_senha")

    if st.button("Entrar"):
        if autenticar_usuario(usuario, senha):
            st.session_state.logado = True
            st.session_state.usuario = usuario
            st.success("✅ Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("❌ Usuário ou senha incorretos.")

# =========================
# APP PRINCIPAL
# =========================
def main():
    st.set_page_config(page_title="Conversor de CEP para Coordenadas", layout="centered")

    if not st.session_state.get("logado", False):
        tela_login()
        st.stop()

    st.sidebar.markdown(f"👤 Logado como: **{st.session_state.usuario}**")
    if st.sidebar.button("Logout"):
        st.session_state.logado = False
        st.session_state.usuario = ""
        st.success("✅ Logout realizado com sucesso!")
        st.stop()

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
