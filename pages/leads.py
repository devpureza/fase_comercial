import streamlit as st
import sqlite3
import re
from auth_guard import verificar_autenticacao
from database import criar_tabelas
# 🚀 Exigir login antes de carregar a página
verificar_autenticacao()

criar_tabelas()


st.title("📋 Gestão de Leads")

# Conectar ao banco de dados
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

# Funções para validação
def validar_email(email):
    """ Valida o formato do e-mail """
    padrao_email = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(padrao_email, email)

def validar_telefone(telefone):
    """ Valida se o telefone tem entre 8 e 12 dígitos numéricos """
    numeros = re.sub(r"\D", "", telefone)
    return 8 <= len(numeros) <= 12


# 📌 Formulário para adicionar lead
st.subheader("➕ Adicionar Novo Lead")
with st.form("form_adicionar_lead"):
    nome = st.text_input("Nome")
    empresa = st.text_input("Empresa")
    contato = st.text_input("Telefone (ex: (11) 98765-4321)")
    email = st.text_input("E-mail do Lead")

    if st.form_submit_button("Adicionar Lead"):
        if not nome or not empresa or not contato or not email:
            st.error("❌ Preencha todos os campos!")
        elif not validar_email(email):
            st.error("❌ E-mail inválido! Use o formato correto: nome@dominio.com")
        elif not validar_telefone(contato):
            st.error("❌ Telefone inválido! Use o formato correto: (11) 98765-4321 ou (11) 1234-5678")
        else:
            cursor.execute("INSERT INTO leads (nome, empresa, contato, email) VALUES (?, ?, ?, ?)", 
                           (nome, empresa, contato, email))
            conn.commit()
            st.success("✅ Lead cadastrado com sucesso!")
            st.rerun()

# 📌 Listagem de Leads
st.subheader("📌 Leads Cadastrados")
leads = cursor.execute("SELECT id, nome, empresa, contato, email, status FROM leads").fetchall()

if leads:
    for lead in leads:
        with st.expander(f"📍 {lead[1]} - {lead[2]}"):
            st.write(f"**Contato:** {lead[3]}")
            st.write(f"**E-mail:** {lead[4]}")
            st.write(f"**Status:** {lead[5]}")

            # Atualizar Status
            novo_status = st.selectbox(
                "Atualizar Status",
                ["Novo", "Em negociação", "Fechado", "Perdido"],
                index=["Novo", "Em negociação", "Fechado", "Perdido"].index(lead[5]),
                key=f"status_{lead[0]}"
            )
            if st.button("Salvar Status", key=f"salvar_{lead[0]}"):
                cursor.execute("UPDATE leads SET status = ? WHERE id = ?", (novo_status, lead[0]))
                conn.commit()
                st.success("✅ Status atualizado!")
                st.rerun()

            # Excluir Lead
            if st.button("❌ Excluir Lead", key=f"excluir_{lead[0]}"):
                cursor.execute("DELETE FROM leads WHERE id = ?", (lead[0],))
                conn.commit()
                st.warning("🚨 Lead excluído!")
                st.rerun()
else:
    st.info("Nenhum lead cadastrado ainda.")

conn.close()
