# 📍 Conversor de CEPs para Coordenadas

Aplicação web desenvolvida com **Python + Streamlit** para conversão de CEPs em coordenadas geográficas (latitude e longitude), com autenticação de usuários e integração com APIs externas.

---

## 📦 Funcionalidades

- ✅ Login com autenticação segura usando `bcrypt` e PostgreSQL (via Supabase).
- 📥 Upload de arquivos `.xlsx` contendo CEPs.
- 🔍 Busca de endereço a partir do CEP via `brazilcep`.
- 🌐 Obtenção de coordenadas via API do Google Maps.
- 🧾 Download da planilha de resultados com CEP, endereço, latitude e longitude.
- 🛡️ Tela de login com proteção de rotas.
- 🖼️ Logo personalizada e layout responsivo.

---

## 📁 Estrutura de Pastas

```
projeto_cep/
│
├── main.py                  # Código principal (Streamlit App)
├── auth.py                  # Lógica de autenticação de usuários
├── database.py              # Conexão com o banco Supabase
├── utils.py                 # Funções auxiliares (CEP, coordenadas)
├── requirements.txt         # Dependências do projeto
└── assets/
    └── LOGO2.png            # Imagem da logo usada no login
```

---

## ⚙️ Requisitos

- Python 3.9+
- Conta e banco no Supabase
- Chave da API do Google Maps (Geocoding API ativada)

---

## 📌 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seuusuario/projeto_cep.git
cd projeto_cep
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Defina as variáveis de ambiente:
```bash
export SENHA="sua_senha_supabase"
```

5. Configure as credenciais no `secrets.toml` do Streamlit:
```toml
# .streamlit/secrets.toml
google_api_key = "SUA_GOOGLE_API_KEY"
```

---

## 🚀 Execução

Rode o app localmente com:

```bash
streamlit run main.py
```

---

## 🧠 Tecnologias Utilizadas

- **Streamlit** – Interface interativa para o app
- **pandas** – Manipulação de planilhas e dados
- **brazilcep** – Consulta de endereços a partir de CEPs brasileiros
- **Google Maps API** – Obtenção de coordenadas via geocodificação
- **bcrypt** – Hash seguro de senhas
- **PostgreSQL (Supabase)** – Autenticação e armazenamento de usuários

---

## 🔐 Tabela `usuarios` no Supabase

```sql
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(255) UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    admin BOOLEAN DEFAULT FALSE
);
```

Senhas devem ser salvas já com:

```python
bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
```

---

## 📤 Exemplo de Entrada

Planilha `.xlsx` com a coluna `CEP`:

| CEP        |
|------------|
| 01310-000  |
| 30130-110  |
| 01001-000  |

---

## 📥 Exemplo de Saída

| CEP       | Endereço                                      | Latitude   | Longitude   |
|-----------|-----------------------------------------------|------------|-------------|
| 01310-000 | Av. Paulista, Bela Vista, São Paulo, SP       | -23.561399 | -46.655881  |
| 30130-110 | Av. Afonso Pena, Centro, Belo Horizonte, MG   | -19.921196 | -43.937523  |
| 01001-000 | Praça da Sé, Sé, São Paulo, SP                | -23.55052  | -46.63331   |

---

## 🧪 Teste Rápido

- Faça login com um usuário do banco.
- Faça upload de um arquivo `.xlsx` com CEPs.
- Baixe a planilha com coordenadas.

---

## 📮 Contato

Desenvolvido por [Seu Nome]  
✉️ Email: dhionatan.sh@gmail.com  
🔗 LinkedIn: [linkedin.com/in/seuperfil]([https://linkedin.com/in/seuperfil](https://www.linkedin.com/in/dhionatanbarbosa/))
