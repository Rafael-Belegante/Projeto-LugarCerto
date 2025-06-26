from . import db
from flask_login import UserMixin
from datetime import datetime

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    aprovado = db.Column(db.Boolean, default=False)

    reivindicacoes = db.relationship(
        'Reivindicacao',
        backref='usuario',
        cascade='all, delete-orphan',
        lazy=True
    )

class Objeto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    local_encontrado = db.Column(db.String(255), nullable=False)
    data_encontrado = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20), default='Disponível')  # Disponível / Pendente / Encontrado
    imagem = db.Column(db.String(255), nullable=True)

    reivindicacoes = db.relationship(
        'Reivindicacao',
        backref='objeto',
        cascade='all, delete-orphan',
        lazy=True
    )

class Reivindicacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    objeto_id = db.Column(
        db.Integer,
        db.ForeignKey('objeto.id', ondelete='CASCADE'),
        nullable=False
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey('usuario.id', ondelete='CASCADE'),
        nullable=False
    )

    status = db.Column(db.String(20), default='Pendente')  # Pendente / Aprovada / Rejeitada
    data = db.Column(db.DateTime, default=datetime.now)
    data_resposta = db.Column(db.String(20), default='Aguardando')
