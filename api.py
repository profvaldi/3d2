import json
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  

JSON_FILE = 'dados.json'
BANCO = 'dados.db'


def salvar_em_json(dados):
    try:
        with open(JSON_FILE, 'r') as f:
            conteudo = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        conteudo = []

    conteudo.append(dados)

    with open(JSON_FILE, 'w') as f:
        json.dump(conteudo, f, indent=4)


def criar_tabela():
    conn = sqlite3.connect(BANCO)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            data_nascimento TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def salvar_no_banco(nome, data_nascimento, email, senha):
    conn = sqlite3.connect(BANCO)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO usuarios (nome, data_nascimento, email, senha) VALUES (?, ?, ?, ?)',
                   (nome, data_nascimento, email, senha))
    conn.commit()
    conn.close()

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    dados = request.get_json()
    campos_obrigatorios = ['nome', 'data_nascimento', 'email', 'senha']

    if not all(campo in dados and dados[campo] for campo in campos_obrigatorios):
        return jsonify({'erro': 'Todos os campos são obrigatórios.'}), 400

    try:
        salvar_em_json(dados)
        salvar_no_banco(dados['nome'], dados['data_nascimento'], dados['email'], dados['senha'])
        return jsonify({'mensagem': 'Usuário cadastrado com sucesso!'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'erro': 'Este email já está cadastrado.'}), 409
    except Exception as e:
        return jsonify({'erro': f'Erro ao cadastrar: {str(e)}'}), 500


@app.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    email = dados.get('email')
    senha = dados.get('senha')

    if not email or not senha:
        return jsonify({'erro': 'Email e senha são obrigatórios.'}), 400

    conn = sqlite3.connect(BANCO)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE email = ? AND senha = ?', (email, senha))
    usuario = cursor.fetchone()
    conn.close()

    if usuario:
        return jsonify({'mensagem': 'Login bem-sucedido!'}), 200
    return jsonify({'erro': 'Email ou senha inválidos.'}), 401

if __name__ == '__main__':
    criar_tabela()
    app.run(debug=True)