import streamlit as st
import sqlite3

st.set_page_config(page_title="Painel Geral", layout="wide")

st.title("📊 Painel Geral - Sistema Comercial")

# Conectar ao banco de dados
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

# 📌 Obter Contagem de Leads e Propostas
cursor.execute("SELECT COUNT(*) FROM leads")
total_leads = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM propostas")
total_propostas = cursor.fetchone()[0]

# 📌 Obter Valores Financeiros
cursor.execute("SELECT SUM(valor) FROM propostas WHERE status = 'Em negociação'")
valor_em_negociacao = cursor.fetchone()[0] or 0

cursor.execute("SELECT SUM(valor) FROM propostas WHERE status = 'Aprovada'")
valor_aprovado = cursor.fetchone()[0] or 0

conn.close()

# 📌 Criar Cards de Visão Geral
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="📋 Total de Leads", value=total_leads)

with col2:
    st.metric(label="📑 Total de Propostas", value=total_propostas)

with col3:
    st.metric(label="💰 Valor em Negociação", value=f"R$ {valor_em_negociacao:,.2f}")

with col4:
    st.metric(label="✅ Valor Aprovado", value=f"R$ {valor_aprovado:,.2f}")

st.divider()

# 📌 Atalhos para Outras Páginas
st.subheader("📌 Acesso Rápido")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📋 Gestão de Leads"):
        st.switch_page("pages/leads.py")

with col2:
    if st.button("📑 Gestão de Propostas"):
        st.switch_page("pages/propostas.py")

with col3:
    if st.button("📊 Pipeline de Vendas"):
        st.switch_page("pages/pipeline.py")

with col4:
    if st.button("📈 Relatórios e Dashboards"):
        st.switch_page("pages/dashboard.py")
