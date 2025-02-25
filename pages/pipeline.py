import streamlit as st
import sqlite3
from auth_guard import verificar_autenticacao
from database import criar_tabelas


# 🚀 Exigir login antes de carregar a página
verificar_autenticacao()

criar_tabelas()

st.title("📊 Pipeline de Vendas - Kanban")

# Conectar ao banco de dados
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

# 📌 Definição dos Status (sem "Novo")
status_opcoes = ["Em análise", "Em negociação", "Aprovada", "Rejeitada"]
status_movimento = {
    "Em análise": {"left": None, "right": "Em negociação"},
    "Em negociação": {"left": "Em análise", "right": "Aprovada"},
    "Aprovada": {"left": "Em negociação", "right": "Rejeitada"},
    "Rejeitada": {"left": "Aprovada", "right": None}
}

# 📌 Buscar propostas que já passaram do status "Novo"
pipeline = {status: [] for status in status_opcoes}

propostas = cursor.execute("""
    SELECT propostas.id, leads.nome, propostas.descricao, propostas.valor, propostas.status 
    FROM propostas 
    JOIN leads ON propostas.lead_id = leads.id
    WHERE propostas.status != 'Novo'
""").fetchall()

for proposta in propostas:
    pipeline[proposta[4]].append(proposta)

# 📌 Criar colunas do Pipeline
cols = st.columns(len(status_opcoes))

for i, status in enumerate(status_opcoes):
    with cols[i]:
        st.subheader(f"{status} ({len(pipeline[status])})")
        
        for proposta in pipeline[status]:
            with st.expander(f"📄 {proposta[1]} - R${proposta[3]:,.2f}"):
                st.write(f"**Descrição:** {proposta[2]}")
                
                col1, col2, col3 = st.columns([1, 2, 1])
                
                # Botão para mover à esquerda
                if status_movimento[status]["left"]:
                    with col1:
                        if st.button("⬅", key=f"left_{proposta[0]}"):
                            cursor.execute("UPDATE propostas SET status = ? WHERE id = ?", 
                                           (status_movimento[status]["left"], proposta[0]))
                            conn.commit()
                            st.rerun()

                # Status atual no centro
                with col2:
                    st.write(f"📌 {status}")

                # Botão para mover à direita
                if status_movimento[status]["right"]:
                    with col3:
                        if st.button("➡", key=f"right_{proposta[0]}"):
                            cursor.execute("UPDATE propostas SET status = ? WHERE id = ?", 
                                           (status_movimento[status]["right"], proposta[0]))
                            conn.commit()
                            st.rerun()

conn.close()
