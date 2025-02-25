import streamlit as st
import time

# Lista de e-mails autorizados
EMAILS_PERMITIDOS = [
    "mateus.pureza@eplugin.app.br",
    "devpureza@gmail.com",
    "juliana.debortolo@eplugin.app.br",
    "matheus.santos@eplugin.app.br",
    "mapureza@gmail.com"
]


def verificar_autenticacao():
    """ Verifica se o usuário está autenticado e tem permissão para acessar. """
    if not st.experimental_user.is_logged_in:
        st.error("🔐 Você precisa estar logado para acessar esta página.")
        time.sleep(2)
        st.login("google")
        st.stop()  # Interrompe a execução da página
    
    email_usuario = st.experimental_user.email  # Captura o e-mail do usuário
    
    if email_usuario not in EMAILS_PERMITIDOS:
        st.error("❌ Acesso negado! Seu e-mail não tem permissão.")
        time.sleep(2)
        st.logout()
        st.stop()  # Interrompe a execução da página
