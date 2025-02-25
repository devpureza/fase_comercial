import streamlit as st
import sqlite3
import matplotlib.pyplot as plt
from auth_guard import verificar_autenticacao

# 🚀 Exigir login antes de carregar a página
verificar_autenticacao()

st.title("📊 Relatórios e Dashboards")

# Conectar ao banco de dados
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

# 📌 Obter dados dos Leads
cursor.execute("SELECT status, COUNT(*) FROM leads GROUP BY status")
leads_data = dict(cursor.fetchall())

# 📌 Obter dados das Propostas
cursor.execute("SELECT status, COUNT(*) FROM propostas GROUP BY status")
propostas_data = dict(cursor.fetchall())

# 📌 Obter valores financeiros
cursor.execute("SELECT SUM(valor) FROM propostas WHERE status = 'Em negociação'")
valor_em_negociacao = cursor.fetchone()[0] or 0

cursor.execute("SELECT SUM(valor) FROM propostas WHERE status = 'Aprovada'")
valor_aprovado = cursor.fetchone()[0] or 0

conn.close()

# 📌 Criar colunas para indicadores principais
col1, col2 = st.columns(2)

with col1:
    st.metric(label="💰 Total em Negociação", value=f"R$ {valor_em_negociacao:,.2f}")
with col2:
    st.metric(label="✅ Total Aprovado", value=f"R$ {valor_aprovado:,.2f}")

st.divider()

# 📌 Criar Gráfico de Leads por Status
st.subheader("📈 Leads por Status")
fig, ax = plt.subplots()
ax.bar(leads_data.keys(), leads_data.values(), color=['blue', 'orange', 'green', 'red'])
ax.set_xlabel("Status")
ax.set_ylabel("Quantidade")
ax.set_title("Distribuição de Leads")
st.pyplot(fig)

st.divider()

# 📌 Criar Gráfico de Propostas por Status
st.subheader("📊 Propostas por Status")
fig, ax = plt.subplots()
ax.pie(propostas_data.values(), labels=propostas_data.keys(), autopct='%1.1f%%', colors=['blue', 'orange', 'green', 'red'])
ax.set_title("Distribuição de Propostas")
st.pyplot(fig)
