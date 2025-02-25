import streamlit as st
import time

st.set_page_config(page_title="Sistema Comercial", layout="wide")

# Lista de e-mails autorizados
EMAILS_PERMITIDOS = [
    "mateus.pureza@eplugin.app.br"
]


# Verifica se o usuário está logado
if not st.experimental_user.is_logged_in:
    st.write("🔐 Faça login com sua conta Google para acessar o sistema.")
    
    if st.button("Log in com Google"):
        st.login("google")

else:
    email_usuario = st.experimental_user.email  # Captura o e-mail do usuário

    # Verifica se o e-mail está na lista de autorizados
    if email_usuario not in EMAILS_PERMITIDOS:
        st.error("❌ Acesso negado! Seu e-mail não tem permissão para acessar este sistema!")
        time.sleep(3)
        st.logout()  # Desloga o usuário automaticamente
        st.stop()  # Interrompe a execução da aplicação

    # Se o e-mail for permitido, exibe o painel
    
    with st.sidebar:
        st.sidebar.write(f"👤 Usuário: **{st.experimental_user.name}**")
        st.sidebar.write(f"📧 E-mail: {email_usuario}")
    
    if st.sidebar.button("Sair"):
        st.logout()

    st.write(f"✅ Bem-vindo, {st.experimental_user.name}!")
    st.write("Aqui vai o painel comercial...")