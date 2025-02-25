import streamlit as st
import sqlite3
from auth_guard import verificar_autenticacao

# 🚀 Exigir login antes de carregar a página
verificar_autenticacao()

st.title("📑 Gestão de Propostas")

# Conectar ao banco de dados
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

# 📌 Obter Leads para associar às propostas
leads = cursor.execute("SELECT id, nome FROM leads").fetchall()
lead_dict = {lead[1]: lead[0] for lead in leads}

# 📌 Formulário para adicionar proposta
st.subheader("➕ Criar Nova Proposta")
if not lead_dict:
    st.warning("⚠️ Nenhum lead cadastrado. Adicione leads primeiro!")
else:
    with st.form("form_adicionar_proposta"):
        lead_nome = st.selectbox("Selecionar Lead", options=list(lead_dict.keys()))
        descricao = st.text_area("Descrição da Proposta")
        valor = st.number_input("Valor da Proposta", min_value=0.0, format="%.2f")
        
        if st.form_submit_button("Salvar Proposta"):
            if descricao and valor > 0:
                cursor.execute("INSERT INTO propostas (lead_id, descricao, valor) VALUES (?, ?, ?)",
                               (lead_dict[lead_nome], descricao, valor))
                conn.commit()
                st.success("✅ Proposta cadastrada com sucesso!")
                st.rerun()
            else:
                st.error("❌ Preencha todos os campos!")

# 📌 Listagem de Propostas
st.subheader("📌 Propostas Cadastradas")
propostas = cursor.execute("""
    SELECT propostas.id, leads.nome, propostas.descricao, propostas.valor, propostas.status 
    FROM propostas 
    JOIN leads ON propostas.lead_id = leads.id
""").fetchall()

if propostas:
    for proposta in propostas:
        with st.expander(f"📄 {proposta[1]} - R${proposta[3]:,.2f}"):
            st.write(f"**Descrição:** {proposta[2]}")
            st.write(f"**Status:** {proposta[4]}")

            # Atualizar Status
            novo_status = st.selectbox(
                "Atualizar Status",
                ["Em análise", "Aprovada", "Rejeitada"],
                index=["Em análise", "Aprovada", "Rejeitada"].index(proposta[4]),
                key=f"status_{proposta[0]}"
            )
            if st.button("Salvar Status", key=f"salvar_{proposta[0]}"):
                cursor.execute("UPDATE propostas SET status = ? WHERE id = ?", (novo_status, proposta[0]))
                conn.commit()
                st.success("✅ Status atualizado!")
                st.rerun()

            # Excluir Proposta
            if st.button("❌ Excluir Proposta", key=f"excluir_{proposta[0]}"):
                cursor.execute("DELETE FROM propostas WHERE id = ?", (proposta[0],))
                conn.commit()
                st.warning("🚨 Proposta excluída!")
                st.rerun()
else:
    st.info("Nenhuma proposta cadastrada ainda.")

conn.close()
