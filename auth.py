import bcrypt
from database import conectar

def autenticar_usuario(usuario, senha):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT senha FROM usuarios WHERE usuario = %s", (usuario,))
    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        senha_hash = resultado["senha"]
        return bcrypt.checkpw(senha.encode(), senha_hash.encode())
    return False
