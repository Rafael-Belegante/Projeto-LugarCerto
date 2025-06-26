#!/bin/bash

# setup_env.sh
# Este script copia o arquivo .env.example para .env, se ainda não existir.

ENV_FILE=".env"
EXAMPLE_FILE=".env.example"

echo "🔧 Iniciando configuração de ambiente..."

if [ -f "$ENV_FILE" ]; then
    echo "⚠️  O arquivo $ENV_FILE já existe. Nenhuma ação foi realizada."
else
    if [ -f "$EXAMPLE_FILE" ]; then
        cp "$EXAMPLE_FILE" "$ENV_FILE"
        echo "✅ Arquivo .env criado a partir de .env.example."
        echo "📝 Edite o arquivo .env com suas configurações reais."
    else
        echo "❌ Arquivo .env.example não encontrado. Abortando."
    fi
fi

# Cria o ambiente python e instala os requisitos
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

echo "Ambiente configurado com sucesso!"

# Pausa para o usuário ler as mensagens
read -p "Pressione ENTER para sair..."