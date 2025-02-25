import sqlite3
import bcrypt

# Conectar ao banco de dados
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

# Função para cadastrar usuário
def cadastrar_usuario(nome, email, senha):
    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
    try:
        cursor.execute("INSERT INTO usuarios (nome, email, senha_hash) VALUES (?, ?, ?)", (nome, email, senha_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Se o e-mail já estiver cadastrado

# Função para autenticar usuário
def autenticar_usuario(email, senha):
    cursor.execute("SELECT id, nome, senha_hash FROM usuarios WHERE email = ?", (email,))
    usuario = cursor.fetchone()
    if usuario and bcrypt.checkpw(senha.encode(), usuario[2].encode()):
        return {"id": usuario[0], "nome": usuario[1], "email": email}
    return None
