import sqlite3
import bcrypt

# Conectar ao banco SQLite
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

# Criar tabelas se não existirem
def criar_tabelas():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha_hash TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        empresa TEXT NOT NULL,
        contato TEXT NOT NULL,
        email TEXT NOT NULL,
        status TEXT DEFAULT 'Novo'
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS propostas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_id INTEGER NOT NULL,
        descricao TEXT NOT NULL,
        valor REAL NOT NULL,
        status TEXT DEFAULT 'Em análise',
        FOREIGN KEY (lead_id) REFERENCES leads(id)
    )
    """)

    conn.commit()

# Função para cadastrar usuário (com senha hash)
def cadastrar_usuario(nome, email, senha):
    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
    try:
        cursor.execute("INSERT INTO usuarios (nome, email, senha_hash) VALUES (?, ?, ?)", (nome, email, senha_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # E-mail já cadastrado

# Testar conexão e criar tabelas
if __name__ == "__main__":
    criar_tabelas()
    print("Banco de dados configurado com sucesso!")
