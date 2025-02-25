import streamlit as st
import sqlite3
from auth_guard import verificar_autenticacao
from database import criar_tabelas

# Configuração da página
st.set_page_config(
    page_title="Pipeline de Vendas",
    layout="wide"
)

# 🚀 Exigir login antes de carregar a página
verificar_autenticacao()

criar_tabelas()

st.title("📊 Pipeline de Vendas - Kanban")

# Inicializar o estado
if 'need_update' not in st.session_state:
    st.session_state.need_update = False

# Função para atualizar o status
def atualizar_status(proposta_id, novo_status):
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE propostas SET status = ? WHERE id = ?", (novo_status, proposta_id))
        conn.commit()
    st.session_state.need_update = True

# 📌 Definição dos Status (sem "Em negociação")
status_opcoes = ["Em análise", "Aprovada", "Rejeitada"]
status_movimento = {
    "Em análise": {"left": None, "right": "Aprovada"},
    "Aprovada": {"left": "Em análise", "right": "Rejeitada"},
    "Rejeitada": {"left": "Aprovada", "right": None}
}

# 📌 Buscar propostas que já passaram do status "Novo"
pipeline = {status: [] for status in status_opcoes}

# Buscar propostas usando with para garantir que a conexão seja fechada
with sqlite3.connect("database.db") as conn:
    cursor = conn.cursor()
    propostas = cursor.execute("""
        SELECT 
            propostas.id,
            leads.nome,
            leads.empresa,
            propostas.descricao,
            propostas.valor,
            propostas.status
        FROM propostas 
        JOIN leads ON propostas.lead_id = leads.id
        WHERE propostas.status != 'Novo'
        AND propostas.status != 'Em negociação'
    """).fetchall()

for proposta in propostas:
    pipeline[proposta[5]].append(proposta)

# 📌 Criar colunas do Pipeline
st.markdown("---")
cols = st.columns(len(status_opcoes))

for i, status in enumerate(status_opcoes):
    with cols[i]:
        st.subheader(f"{status} ({len(pipeline[status])})")
        st.markdown("---")
        
        for proposta in pipeline[status]:
            with st.container():
                st.info(f"""
                **🏢 {proposta[2]}**  
                **👤 {proposta[1]}**
                """)
                st.caption(f"💰 Valor: R$ {proposta[4]:,.2f}")
                st.text_area("Descrição", proposta[3], height=100, disabled=True, key=f"desc_{proposta[0]}")
                
                col1, col2, col3 = st.columns([1, 2, 1])
                
                # Botão para mover à esquerda
                if status_movimento[status]["left"]:
                    with col1:
                        st.button(
                            "⬅ Voltar", 
                            key=f"left_{proposta[0]}", 
                            on_click=atualizar_status,
                            args=(proposta[0], status_movimento[status]["left"])
                        )

                # Status atual no centro
                with col2:
                    st.caption(f"📌 Status atual: {status}")

                # Botão para mover à direita
                if status_movimento[status]["right"]:
                    with col3:
                        st.button(
                            "Avançar ➡", 
                            key=f"right_{proposta[0]}", 
                            on_click=atualizar_status,
                            args=(proposta[0], status_movimento[status]["right"])
                        )
                
                st.markdown("---")

# Verificar se precisa atualizar a página
if st.session_state.need_update:
    st.session_state.need_update = False
    st.experimental_rerun()

