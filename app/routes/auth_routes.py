from flask import Blueprint, request, redirect, url_for, render_template, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import Usuario
from app.routes.utils import admin_required
from app.routes.utils import enviar_email
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email'].lower()
        senha = generate_password_hash(request.form['senha'])

        if Usuario.query.filter_by(email=email).first():
            flash("Email já cadastrado.")
            return redirect(url_for('auth.registrar'))

        novo_usuario = Usuario(nome=nome, email=email, senha=senha, aprovado=False)
        db.session.add(novo_usuario)
        db.session.commit()

        # Envia email confirmando registro pendente
        corpo = f"""
Olá, {nome}!

Seu pedido de registro no sistema Lugar Certo foi recebido com sucesso.

Assim que um administrador aprovar seu cadastro, você poderá acessar o sistema normalmente.

Obrigado pela paciência!
Equipe Lugar Certo
        """
        enviar_email(email, "Cadastro pendente - Lugar Certo", corpo)

        flash("Registro enviado com sucesso! Verifique seu e-mail.")
        current_app.logger.info(f"Novo usuario padrão registrado: {nome} ({email}) | Autor: {current_user.email} ({current_user.nome})")
        return redirect(url_for('auth.login'))

    return render_template('registro.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].lower()
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.senha, senha):
            if usuario.aprovado:
                login_user(usuario)
                current_app.logger.info(f"Novo login: {usuario.nome} ({email}")
                return redirect(url_for('objeto.index'))
            else:
                flash("Sua conta ainda não foi aprovada por um administrador.", 'warning')
        else:
            flash("Credenciais inválidas.", 'danger')
            current_app.logger.info(f"ATENÇÃO: Tentativa de login inválida para o usuário: {usuario.nome} ({email})")

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/registrar_admin', methods=['GET', 'POST'])
@login_required
@admin_required
def registrar_admin():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = generate_password_hash(request.form['senha'])
        if Usuario.query.filter_by(email=email).first():
            flash("Email já cadastrado.")
            return redirect(url_for('objeto.index'))

        novo_admin = Usuario(nome=nome, email=email, senha=senha, is_admin=True)
        db.session.add(novo_admin)
        db.session.commit()
        current_app.logger.info(f"Novo admin registrado: {nome} ({email}) | Autor: {current_user.email} ({current_user.nome})")
        return redirect(url_for('objeto.index'))
    return render_template('registro_admin.html')

