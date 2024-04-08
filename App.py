from flask import (Flask, render_template, request,
                   redirect, url_for, flash, session)

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import generate_password_hash, check_password_hash #lidar com a criptografia de senhas

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/financeiro'
app.config['SECRET_KEY'] = 'ASDFGHJKL'
db = SQLAlchemy(app) # Inicializa com o banco de dados


#usuario, receita e despesas é um modelo de dados e possui os recursos e funcionalidades fornecidos pelo SQLAlchemy.
# Classes que representam tabelas no banco de dados.
class Usuario(db.Model):
    # colunas do banco de dados
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True) #integer significa q e um numero interio,
    # primary_key significa que a chave primaria da tabela, autoincrement=True indica que o valor desta coluna será gerado automaticamente pelo banco de dados
    nome = db.Column(db.String(50))
    email = db.Column(db.String(100))
    senha = db.Column(db.String(254))

class Receitas(db.Model):
    id_receitas = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(254))
    valor = db.Column(db.Numeric)
    data = db.Column(db.Date)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))

class Despesas(db.Model):
    id_despesas = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(254))
    valor = db.Column(db.Numeric)
    data = db.Column(db.Date)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))


# Rota principal que renderiza a página inicial, exibindo o saldo total de receitas e despesas,
# bem como listas de receitas e despesas.
@app.route('/')
def index():
    receitas = Receitas.query.all() #consulta ao banco de dados para obter tudo que esta armazenado
    despesas = Despesas.query.all()

    # esta percorrendo e extraindo o valor, logo em seguida somando tudo
    total_receitas = sum(receita.valor for receita in receitas)
    total_despesas = sum(despesa.valor for despesa in despesas)

    # passa algumas variaveis para usar no template, rece e despe sao as listas contendo tudo
    return render_template('home.html', total_receitas=total_receitas, total_despesas=total_despesas, rece=receitas, despe=despesas)


# Rota para adicionar novas receitas e despesas. Se o usuário estiver logado, exibe um formulário para
# adicionar uma nova receita ou despesa. Caso contrário, redireciona para a página de login.
@app.route('/novoReceitas')
def novoRece():
    receitas = Receitas.query.all()
    if 'id' in session:
        return render_template('novoReceitas.html', titulo='Nova Receita', rece=receitas)
    else:
        return redirect(url_for('login_form'))

@app.route('/novoDespesas')
def novoDespe():
    despesas = Despesas.query.all()
    if 'id' in session:
        return render_template('novoDespesas.html', titulo='Nova Despesa', despe=despesas)
    else:
        return redirect(url_for('login_form'))


# Rota para lidar com a criação de uma nova receita e despesas. Os dados são recebidos por meio de uma
# solicitação POST e adicionados ao banco de dados.
@app.route('/criarReceita', methods=['POST'])
def criarRece():
    #  obtendo o valor do campo 'nome' que foi enviado através do input do formulário HTML
    nome = request.form['nome']
    valor= request.form['valor']
    data = request.form['data']

    #passando os dados para a classe
    nova_receita = Receitas(nome=nome, valor=valor, data=data)

    # insere a nova receita no banco de dados
    db.session.add(nova_receita)
    db.session.commit()
    return redirect(url_for('novoRece'))


@app.route('/criarDespesa', methods=['POST'])
def criarDespe():
    nome = request.form['nome']
    valor= request.form['valor']
    data = request.form['data']

    nova_despesa = Despesas(nome=nome, valor=valor, data=data)

    db.session.add(nova_despesa)
    db.session.commit()
    return redirect(url_for('novoDespe'))


# Rota para excluir receita e uma despesas específica com base no seu ID.
@app.route('/deletarRece/<int:id>')
def deletarRece(id):
    Receitas.query.filter_by(id_receitas=id).delete()
    db.session.commit()
    return redirect(url_for('novoRece'))


@app.route('/deletarDespe/<int:id>')
def deletarDespe(id):
    Despesas.query.filter_by(id_despesas=id).delete()
    db.session.commit()
    return redirect(url_for('novoDespe'))

# =========================LOGIN===============================================

# Rota para exibir o formulário de login.
@app.route('/login')
def login_form():
    return render_template('login.html')

# Verifica as credenciais fornecidas pelo usuário, se forem válidas, redireciona para a
# página inicial.
@app.route('/login', methods=['POST'])
def login_post():
    #obtendo o valor de email e senha que foi enviado atraves do input
    email = request.form.get('email')
    senha = request.form.get('senha')

    #consultando o banco para achar um usuario com o email e a senha fornecido
    user = Usuario.query.filter_by(email=email).first()
    senha = check_password_hash(user.senha, senha)

    #verifica se o usuario e a senha sao validos
    if user and senha:
        # o ID do usuário é armazenado na sessão para identificar o usuário logado
        # em seguida direciona ele a proxima rota que le etentava acessar
        session['id'] = user.id_usuario
        if 'next' in session:
            next_route = session.pop('next')
            return redirect(url_for(next_route))
        return redirect(url_for('index'))
    else:
        flash('Email ou senha incorretos', 'error')
        return redirect(url_for('login_form'))


# Rota para exibir o formulário de registro de novo usuário.
@app.route('/novo_user')
def novo_user():
	return render_template('novo_usuario.html', titulo='Novo Usuário')


# Rota para criar um novo usuário com base nas informações fornecidas no formulário de registro.
@app.route('/criar_user', methods=['POST'])
def criar_user():
    email = request.form['email']
    senha = request.form['senha']

    #verifica se tem um email ja existente
    user = Usuario.query.filter_by(email=email).first()
    if user:
        flash('Usuário já existe', 'error')
        return redirect(url_for('novo_user'))
    else:
        #senha fornecida é criptografada
        senha_hash = generate_password_hash(senha).decode('utf-8')
        #passando os dados para a classe
        novo_usuario = Usuario(email=email, senha=senha_hash)
        #adiciona o novo usuario ao banco
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Usuário cadastrado com sucesso', 'success')
        return redirect(url_for('novo_user'))

# Rota para realizar o logout do usuário.
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)