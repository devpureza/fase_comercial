import streamlit as st
import time
import sqlite3
from datetime import datetime, timedelta
import plotly.graph_objects as go
from database import criar_tabelas

#Verifica e cria tabelas caso necessário
criar_tabelas()

st.set_page_config(page_title="Sistema Comercial", layout="wide")

# Lista de e-mails autorizados
EMAILS_PERMITIDOS = [
    "mateus.pureza@eplugin.app.br",
    "devpureza@gmail.com",
    "juliana.debortolo@eplugin.app.br",
    "matheus.santos@eplugin.app.br",
    "mapureza@gmail.com"
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

    # Título com boas-vindas e hora do dia
    hora_atual = datetime.now().hour
    if 5 <= hora_atual < 12:
        saudacao = "Bom dia"
    elif 12 <= hora_atual < 18:
        saudacao = "Boa tarde"
    else:
        saudacao = "Boa noite"
    
    st.title(f"👋 {saudacao}, {st.experimental_user.name}!")

    # Conectar ao banco de dados
    conn = sqlite3.connect("database.db", check_same_thread=False)
    cursor = conn.cursor()

    # Obter métricas gerais
    cursor.execute("""
        SELECT 
            (SELECT COUNT(*) FROM leads) as total_leads,
            (SELECT COUNT(*) FROM propostas) as total_propostas,
            (SELECT COUNT(*) FROM leads WHERE status = 'Em negociação') as leads_ativos,
            (SELECT SUM(valor) FROM propostas WHERE status = 'Aprovada') as valor_aprovado
    """)
    metricas = cursor.fetchone()

    # Cards com métricas principais
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.info("📊 Total de Leads", icon="📊")
        st.header(f"{metricas[0]}")
    with col2:
        st.info("📝 Total de Propostas", icon="📝")
        st.header(f"{metricas[1]}")
    with col3:
        st.info("🔥 Leads Ativos", icon="🔥")
        st.header(f"{metricas[2]}")
    with col4:
        st.success("💰 Valor Aprovado", icon="💰")
        st.header(f"R$ {metricas[3]:,.2f}" if metricas[3] else "R$ 0,00")

    st.divider()

    # Atividades Recentes e Próximas Ações
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📅 Atividades Recentes")
        # Últimos 5 leads cadastrados
        cursor.execute("""
            SELECT nome, empresa, status, datetime('now', '-' || ABS(RANDOM() % 7) || ' days') as data_cadastro
            FROM leads 
            ORDER BY RANDOM()
            LIMIT 5
        """)
        leads_recentes = cursor.fetchall()

        for lead in leads_recentes:
            with st.container():
                st.write(f"🏢 **{lead[1]}** - 👤 {lead[0]}")
                st.caption(f"Status: {lead[2]} | Data: {lead[3]}")

    with col2:
        st.subheader("⚡ Leads Quentes")
        # Leads em negociação
        cursor.execute("""
            SELECT l.nome, l.empresa, p.valor
            FROM leads l
            JOIN propostas p ON l.id = p.lead_id
            WHERE l.status = 'Em negociação'
            AND p.status = 'Em análise'
            ORDER BY p.valor DESC
            LIMIT 5
        """)
        leads_quentes = cursor.fetchall()

        for lead in leads_quentes:
            with st.container():
                st.write(f"🔥 **{lead[1]}** - {lead[0]}")
                st.caption(f"Valor da Proposta: R$ {lead[2]:,.2f}")

    st.divider()

    # Dicas e Links Rápidos
    st.subheader("🚀 Links Rápidos")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Cadastrar Novo Lead", use_container_width=True):
            st.switch_page("pages/leads.py")
    with col2:
        if st.button("💼 Criar Nova Proposta", use_container_width=True):
            st.switch_page("pages/propostas.py")
    with col3:
        if st.button("📊 Ver Dashboard Completo", use_container_width=True):
            st.switch_page("pages/dashboard.py")

    # Fechar conexão
    conn.close()