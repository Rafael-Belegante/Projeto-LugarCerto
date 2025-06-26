from flask import abort, current_app
from flask_login import current_user
from functools import wraps
import smtplib
from email.mime.text import MIMEText

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)  # Acesso negado
        return f(*args, **kwargs)
    return decorated_function


def enviar_email(destinatario, assunto, corpo):
    remetente = current_app.config['MAIL_USERNAME']
    senha = current_app.config['MAIL_PASSWORD']
    servidor = current_app.config['MAIL_SERVER']
    porta = current_app.config['MAIL_PORT']
    usar_ssl = current_app.config['MAIL_USE_SSL']
    usar_tls = current_app.config['MAIL_USE_TLS']

    msg = MIMEText(corpo)
    msg['Subject'] = assunto
    msg['From'] = remetente
    msg['To'] = destinatario

    try:
        if usar_ssl:
            with smtplib.SMTP_SSL(servidor, porta) as server:
                server.login(remetente, senha)
                server.send_message(msg)
        else:
            with smtplib.SMTP(servidor, porta) as server:
                if usar_tls:
                    server.starttls()
                server.login(remetente, senha)
                server.send_message(msg)

    except Exception as e:
        current_app.logger.error(f"Erro ao enviar e-mail: {e}")
