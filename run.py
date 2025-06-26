from dotenv import load_dotenv

# Carrega o .env (caso exista)
load_dotenv()

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=app.config['DEBUG'])
