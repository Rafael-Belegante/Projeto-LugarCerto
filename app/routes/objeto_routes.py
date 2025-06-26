from flask import Blueprint, redirect, url_for, render_template, flash, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Objeto, Usuario, Reivindicacao

objeto_bp = Blueprint('objeto', __name__)

@objeto_bp.route('/')
def index():
    objetos = (
        Objeto.query
        .outerjoin(Reivindicacao)
        .filter(
            ~Objeto.reivindicacoes.any(Reivindicacao.status == 'Aprovada')
        )
        .all()
    )
    return render_template('index.html', objetos=objetos, usuario=current_user)

@objeto_bp.route('/reivindicar/<int:objeto_id>', methods=['POST'])
@login_required
def reivindicar(objeto_id):
    objeto = Objeto.query.get_or_404(objeto_id)

    if objeto.status != 'Disponível':
        flash('Objeto indisponível.', 'warning')
        return redirect(url_for('objeto.index'))

    # Verifica se o usuário já tem uma reivindicação pendente pra esse objeto
    existente = Reivindicacao.query.filter_by(objeto_id=objeto.id, usuario_id=current_user.id, status='Pendente').first()
    if existente:
        flash('Você já fez uma solicitação para esse objeto.', 'info')
        return redirect(url_for('objeto.index'))

    # Cria nova reivindicação
    nova_reivindicacao = Reivindicacao(objeto_id=objeto.id, usuario_id=current_user.id)
    objeto.status = 'Pendente'

    db.session.add(nova_reivindicacao)
    db.session.commit()
    current_app.logger.info(f"Nova reivindicação do objeto {objeto.nome} | Autor: {current_user.nome}")
    return redirect(url_for('objeto.index'))

@objeto_bp.route('/reivindicacoes')
@login_required
def reivindicacoes():
    minhas_reivindicacoes = Reivindicacao.query.filter_by(usuario_id=current_user.id).all()
    return render_template('reivindicacoes.html', reivindicacoes=minhas_reivindicacoes)
