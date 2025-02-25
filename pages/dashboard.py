import streamlit as st
import sqlite3
import plotly.graph_objects as go
import plotly.express as px
from auth_guard import verificar_autenticacao
from database import criar_tabelas

# Configuração da página
st.set_page_config(
    page_title="Dashboard Comercial",
    layout="wide"
)

# 🚀 Exigir login antes de carregar a página
verificar_autenticacao()
# Verificar e faz a criação de tabelas caso não exista
criar_tabelas()

st.title("📊 Dashboard Comercial")

# Conectar ao banco de dados
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

# 📌 Obter dados financeiros
cursor.execute("""
    SELECT 
        SUM(CASE WHEN status = 'Em análise' THEN valor ELSE 0 END) as em_analise,
        SUM(CASE WHEN status = 'Aprovada' THEN valor ELSE 0 END) as aprovado,
        SUM(CASE WHEN status = 'Rejeitada' THEN valor ELSE 0 END) as rejeitado,
        COUNT(CASE WHEN status = 'Em análise' THEN 1 END) as qtd_em_analise,
        COUNT(CASE WHEN status = 'Aprovada' THEN 1 END) as qtd_aprovada,
        COUNT(CASE WHEN status = 'Rejeitada' THEN 1 END) as qtd_rejeitada
    FROM propostas
""")
dados_financeiros = cursor.fetchone()

# 📌 Obter dados dos Leads por status
cursor.execute("""
    SELECT status, COUNT(*) as quantidade, 
           COUNT(*) * 100.0 / (SELECT COUNT(*) FROM leads) as porcentagem
    FROM leads 
    GROUP BY status
""")
leads_data = cursor.fetchall()

# 📌 Obter dados das Propostas com valores
cursor.execute("""
    SELECT status, COUNT(*) as quantidade, SUM(valor) as valor_total
    FROM propostas 
    GROUP BY status
""")
propostas_data = cursor.fetchall()

# 📌 Obter top 5 empresas por valor em propostas
cursor.execute("""
    SELECT l.empresa, SUM(p.valor) as valor_total, COUNT(*) as num_propostas
    FROM propostas p
    JOIN leads l ON p.lead_id = l.id
    GROUP BY l.empresa
    ORDER BY valor_total DESC
    LIMIT 5
""")
top_empresas = cursor.fetchall()

conn.close()

# 📌 Cards com métricas principais
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="💰 Em Análise",
        value=f"R$ {dados_financeiros[0]:,.2f}",
        delta=f"{dados_financeiros[3]} propostas"
    )
with col2:
    st.metric(
        label="✅ Aprovado",
        value=f"R$ {dados_financeiros[1]:,.2f}",
        delta=f"{dados_financeiros[4]} propostas"
    )
with col3:
    st.metric(
        label="❌ Rejeitado",
        value=f"R$ {dados_financeiros[2]:,.2f}",
        delta=f"{dados_financeiros[5]} propostas"
    )

st.divider()

# 📌 Gráficos na mesma linha
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Funil de Leads")
    # Criar gráfico de funil para Leads
    fig_leads = go.Figure(go.Funnel(
        y=[status for status, qtd, pct in leads_data],
        x=[qtd for status, qtd, pct in leads_data],
        textinfo="value+percent initial",
        textposition="inside",
        marker=dict(color=["#2E86C1", "#F1C40F", "#27AE60", "#E74C3C"])
    ))
    fig_leads.update_layout(
        showlegend=False,
        height=400,
        margin=dict(t=0, b=0)
    )
    st.plotly_chart(fig_leads, use_container_width=True)

with col2:
    st.subheader("💰 Valor por Status das Propostas")
    # Criar gráfico de barras para valores das propostas
    fig_propostas = go.Figure(data=[
        go.Bar(
            x=[status for status, qtd, valor in propostas_data],
            y=[valor for status, qtd, valor in propostas_data],
            text=[f"R$ {valor:,.2f}" for status, qtd, valor in propostas_data],
            textposition='auto',
            marker_color=["#2E86C1", "#27AE60", "#E74C3C"]
        )
    ])
    fig_propostas.update_layout(
        yaxis_title="Valor Total (R$)",
        showlegend=False,
        height=400,
        margin=dict(t=0, b=0)
    )
    st.plotly_chart(fig_propostas, use_container_width=True)

st.divider()

# 📌 Top 5 Empresas
st.subheader("🏢 Top 5 Empresas por Valor em Propostas")
fig_empresas = go.Figure(data=[
    go.Bar(
        x=[empresa for empresa, valor, num in top_empresas],
        y=[valor for empresa, valor, num in top_empresas],
        text=[f"R$ {valor:,.2f}<br>{num} propostas" for empresa, valor, num in top_empresas],
        textposition='auto',
        marker_color="#2E86C1"
    )
])
fig_empresas.update_layout(
    yaxis_title="Valor Total em Propostas (R$)",
    showlegend=False,
    height=400,
    margin=dict(t=0, b=0)
)
st.plotly_chart(fig_empresas, use_container_width=True)
