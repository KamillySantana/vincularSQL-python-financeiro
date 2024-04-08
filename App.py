from flask import (Flask, render_template, request,
                   redirect, url_for, flash, send_from_directory, session)

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/financeiro'
app.config['SECRET_KEY'] = 'ASDFGHJKL'
db = SQLAlchemy(app)

class Usuario(db.Model):
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
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


@app.route('/')
def index():
    receitas = Receitas.query.all()
    despesas = Despesas.query.all()
    return render_template('home.html', rece=receitas, despe=despesas)

@app.route('/receitas')
def receitas():
    receitas = Receitas.query.all()
    return render_template('cadastroRece.html', rece=receitas)

@app.route('/despesas')
def despesas():
    despesas = Despesas.query.all()
    return render_template('cadastroDespe.html', despe=despesas)


@app.route('/novoReceitas')
def novoRece():
    if 'id' in session:
        return render_template('novoReceitas.html', titulo='Nova Receita')
    else:
        return redirect(url_for('login_form'))

@app.route('/novoDespesas')
def novoDespe():
    if 'id' in session:
        return render_template('novoDespesas.html', titulo='Nova Despesa')
    else:
        return redirect(url_for('login_form'))

@app.route('/criarReceita', methods=['POST'])
def criarRece():
    nome = request.form['nome']
    valor= request.form['valor']
    data = request.form['data']

    nova_receita = Receitas(nome=nome, valor=valor, data=data)

    db.session.add(nova_receita)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/criarDespesa', methods=['POST'])
def criarDespe():
    nome = request.form['nome']
    valor= request.form['valor']
    data = request.form['data']

    nova_despesa = Receitas(nome=nome, valor=valor, data=data)

    db.session.add(nova_despesa)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/deletarRece/<int:id>')
def deletarRece(id):
    Receitas.query.filter_by(id_receitas=id).delete()
    db.session.commit()
    flash('Receita excluido com sucesso.')
    return redirect(url_for('index'))


@app.route('/deletarDespe/<int:id>')
def deletarDespe(id):
    Despesas.query.filter_by(id_despesas=id).delete()
    db.session.commit()
    flash('Livro excluido com sucesso.')
    return redirect(url_for('index'))



@app.route('/login')
def login_form():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    senha = request.form.get('senha')

    user = Usuario.query.filter_by(email=email).first()
    senha = check_password_hash(user.senha, senha)
    if user and senha:
        session['id'] = user.id_usuario
        if 'next' in session:
            next_route = session.pop('next')
            return redirect(url_for(next_route))
        return redirect(url_for('index'))
    else:
        flash('Email ou senha incorretos', 'error')
        return redirect(url_for('login_form'))


@app.route('/novo_user')
def novo_user():
	return render_template('novo_usuario.html', titulo='Novo Usuário')


@app.route('/criar_user', methods=['POST'])
def criar_user():
    email = request.form['email']
    senha = request.form['senha']

    user = Usuario.query.filter_by(email=email).first()
    if user:
        flash('Usuário já existe', 'error')
        return redirect(url_for('novo_user'))
    else:
        senha_hash = generate_password_hash(senha).decode('utf-8')
        novo_usuario = Usuario(email=email, senha=senha_hash)
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Usuário cadastrado com sucesso', 'success')
        return redirect(url_for('novo_user'))


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)