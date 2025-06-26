from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from datetime import datetime
from app import db
from app.models import Usuario, Objeto, Reivindicacao
from app.routes.utils import admin_required
from app.routes.utils import enviar_email
from PIL import Image
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def redimensionar_imagem(caminho_imagem):
    try:
        img = Image.open(caminho_imagem)
        img = img.convert("RGB")  # Remove transparência

        largura, altura = img.size

        # Só redimensiona se algum lado for maior que 512
        if largura > 512 or altura > 512:
            # Calcula fator de redução proporcional
            if largura >= altura:
                fator = 512 / float(largura)
            else:
                fator = 512 / float(altura)

            nova_largura = int(largura * fator)
            nova_altura = int(altura * fator)

            img = img.resize((nova_largura, nova_altura), Image.BILINEAR)

        # Salva como JPEG
        nova_path = os.path.splitext(caminho_imagem)[0] + ".jpg"
        img.save(nova_path, "JPEG", optimize=True, quality=85)

        # Remove o original se o nome mudou
        if nova_path != caminho_imagem and os.path.exists(caminho_imagem):
            os.remove(caminho_imagem)

        return os.path.basename(nova_path)

    except Exception as e:
        current_app.logger.error(
            f"Erro ao redimensionar imagem: {e}")
        return None

# ----------------------
# APROVAÇÃO / REJEIÇÃO
# ----------------------

@admin_bp.route('/aprovar/<int:reivindicacao_id>', methods=['POST'])
@login_required
@admin_required
def aprovar(reivindicacao_id):
    reivind = Reivindicacao.query.get_or_404(reivindicacao_id)
    objeto = reivind.objeto

    reivind.status = 'Aprovada'
    reivind.data_resposta = datetime.now().strftime('%d/%m/%Y %H:%M')
    objeto.status = 'Encontrado'

    db.session.commit()
    current_app.logger.info(
        f"Reivindicação aprovada: {objeto.nome} | Autor: {current_user.email} ({current_user.nome})")
    return redirect(url_for('objeto.index'))

@admin_bp.route('/rejeitar/<int:reivindicacao_id>', methods=['POST'])
@login_required
@admin_required
def rejeitar(reivindicacao_id):
    reivind = Reivindicacao.query.get_or_404(reivindicacao_id)
    objeto = reivind.objeto

    reivind.status = 'Rejeitada'
    reivind.data_resposta = datetime.now().strftime('%d/%m/%Y %H:%M')
    objeto.status = 'Disponível'

    db.session.commit()
    current_app.logger.info(
        f"Reivindicação negada: {objeto.nome} | Autor: {current_user.email} ({current_user.nome})")
    return redirect(url_for('objeto.index'))

# ----------------------
# GERENCIAR USUÁRIOS
# ----------------------

@admin_bp.route('/usuarios')
@login_required
@admin_required
def listar_usuarios():
    usuarios = Usuario.query.all()
    return render_template('admin/usuarios.html', usuarios=usuarios)

@admin_bp.route('/usuarios/novo', methods=['POST'])
@login_required
@admin_required
def criar_usuario():
    nome = request.form['nome']
    email = request.form['email'].lower()
    senha = generate_password_hash(request.form['senha'])
    is_admin = request.form.get('is_admin') == 'on'

    if Usuario.query.filter_by(email=email).first():
        flash("Email já cadastrado.")
        current_app.logger.info(
            f"Tentativa de criação de usuário já existente: {nome} ({email}) | Autor: {current_user.email} ({current_user.nome})")
        return redirect(url_for('admin.listar_usuarios'))

    novo = Usuario(nome=nome, email=email, senha=senha, is_admin=is_admin)
    db.session.add(novo)
    db.session.commit()
    current_app.logger.info(
        f"Usuário criado: {nome} ({email}) | Autor: {current_user.email} ({current_user.nome})")
    return redirect(url_for('admin.listar_usuarios'))

@admin_bp.route('/usuarios/editar/<int:usuario_id>', methods=['POST'])
@login_required
@admin_required
def editar_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    usuario.nome = request.form['nome']
    usuario.email = request.form['email'].lower()
    senha_nova = request.form.get('senha')
    if senha_nova:
        usuario.senha = generate_password_hash(senha_nova)
    usuario.is_admin = request.form.get('is_admin') == 'on'
    db.session.commit()
    current_app.logger.info(
        f"Usuário editado: {usuario.nome} ({usuario.email} - Admin:{usuario.is_admin}) | Autor: {current_user.email} ({current_user.nome})")
    return redirect(url_for('admin.listar_usuarios'))

@admin_bp.route('/usuarios/excluir/<int:usuario_id>', methods=['POST'])
@login_required
@admin_required
def excluir_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    # Verificação pelo nome ou outro campo exclusivo, como email ou ID
    if usuario.nome == "Admin LugarCerto":
        flash('Não é possível excluir a conta do sistema "Admin LugarCerto".', 'danger')
        current_app.logger.info(
            f"Tentativa de exclusão de conta do sistema | Autor: {current_user.email} ({current_user.nome})")
        return redirect(url_for('admin.listar_usuarios'))
    db.session.delete(usuario)
    db.session.commit()
    current_app.logger.info(
        f"Usuário apagado: {usuario.nome} ({usuario.email}) | Autor: {current_user.email} ({current_user.nome})")
    return redirect(url_for('admin.listar_usuarios'))

# --------------------------
# APROVAR/REJEITAR USUÁRIOS
# --------------------------

@admin_bp.route('/usuarios/aprovar/<int:usuario_id>', methods=['POST'])
@login_required
@admin_required
def aprovar_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    usuario.aprovado = True
    db.session.commit()

    corpo = f"""
Olá, {usuario.nome}!

Seu cadastro no sistema Lugar Certo foi aprovado por um administrador.
Você já pode acessar o sistema normalmente pelo link: {url_for('auth.login', _external=True)}

Equipe Lugar Certo
    """
    enviar_email(usuario.email, "Cadastro aprovado - Lugar Certo", corpo)

    flash(f"Usuário {usuario.nome} foi aprovado com sucesso!", "success")
    current_app.logger.info(
        f"Registro de Usuário aprovado: {usuario.nome} ({usuario.email}) | Autor: {current_user.email} ({current_user.nome})")
    return redirect(url_for('admin.listar_usuarios'))

@admin_bp.route('/usuarios/rejeitar/<int:usuario_id>', methods=['POST'])
@login_required
@admin_required
def rejeitar_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)

    corpo = f"""
Olá, {usuario.nome}.

Infelizmente, seu cadastro no sistema Lugar Certo foi recusado por um administrador.

Caso acredite que foi um erro, entre em contato com a equipe responsável.

Equipe Lugar Certo
    """
    enviar_email(usuario.email, "Cadastro recusado - Lugar Certo", corpo)

    db.session.delete(usuario)
    db.session.commit()

    current_app.logger.info(
        f"Registro de Usuário negado: {usuario.nome} ({usuario.email}) | Autor: {current_user.email} ({current_user.nome})")

    flash(f"O cadastro de {usuario.nome} foi rejeitado e removido.", "warning")
    return redirect(url_for('admin.listar_usuarios'))

# ----------------------
# GERENCIAR OBJETOS
# ----------------------

@admin_bp.route('/objetos')
@login_required
@admin_required
def listar_objetos():
    objetos = Objeto.query.all()
    return render_template('admin/objetos.html', objetos=objetos)

@admin_bp.route('/objetos/novo', methods=['POST'])
@login_required
@admin_required
def criar_objeto():
    nome = request.form['nome']
    descricao = request.form['descricao']
    local = request.form['local_encontrado']
    imagem_file = request.files.get('imagem')
    imagem_nome = None

    if imagem_file and imagem_file.filename != '':
        imagem_nome = secure_filename(imagem_file.filename)
        imagem_path = os.path.join(current_app.config['UPLOAD_FOLDER'], imagem_nome)
        imagem_file.save(imagem_path)
        imagem_nome = redimensionar_imagem(imagem_path)

    obj = Objeto(nome=nome, descricao=descricao, local_encontrado=local, imagem=imagem_nome)
    db.session.add(obj)
    db.session.commit()
    current_app.logger.info(
        f"Objeto criado: {obj.nome} ({obj.descricao}) | Autor: {current_user.email} ({current_user.nome})")
    return redirect(url_for('admin.listar_objetos'))

@admin_bp.route('/objetos/editar/<int:objeto_id>', methods=['POST'])
@login_required
@admin_required
def editar_objeto(objeto_id):
    obj = Objeto.query.get_or_404(objeto_id)
    obj.nome = request.form['nome']
    obj.descricao = request.form['descricao']
    obj.local_encontrado = request.form['local_encontrado']

    imagem_file = request.files.get('imagem')
    if imagem_file and imagem_file.filename != '':
        imagem_nome = secure_filename(imagem_file.filename)
        imagem_path = os.path.join(current_app.config['UPLOAD_FOLDER'], imagem_nome)
        imagem_file.save(imagem_path)
        imagem_nome = redimensionar_imagem(imagem_path)
        obj.imagem = imagem_nome

    db.session.commit()
    current_app.logger.info(
        f"Objeto editado: {obj.nome} ({obj.descricao}) | Autor: {current_user.email} ({current_user.nome})")
    return redirect(url_for('admin.listar_objetos'))

@admin_bp.route('/objetos/excluir/<int:objeto_id>', methods=['POST'])
@login_required
@admin_required
def excluir_objeto(objeto_id):
    obj = Objeto.query.get_or_404(objeto_id)
    try:
        os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], obj.imagem))
    except:
        current_app.logger.error(f"Erro ao tentar excluir Imagem do objeto: {obj.nome} ({obj.descricao}) | Autor: {current_user.email} ({current_user.nome})")
    db.session.delete(obj)
    db.session.commit()
    current_app.logger.info(
        f"Objeto excluído: {obj.nome} ({obj.descricao}) | Autor: {current_user.email} ({current_user.nome})")
    return redirect(url_for('admin.listar_objetos'))

@admin_bp.route('/historico')
@login_required
@admin_required
def historico_objetos():
    # Filtrar apenas objetos que possuem uma reivindicação aprovada
    objetos = (
        Objeto.query
        .join(Reivindicacao)
        .filter(Reivindicacao.status == 'Aprovada')
        .all()
    )
    return render_template('admin/historico.html', objetos=objetos)
