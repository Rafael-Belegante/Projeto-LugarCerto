@echo off
REM setup_env.bat
REM Script para copiar o .env.example para .env, se ainda não existir.
chcp 65001 >nul

set ENV_FILE=.env
set EXAMPLE_FILE=.env.example

echo 🔧 Iniciando configuração de ambiente...

if exist %ENV_FILE% (
    echo ⚠️  O arquivo %ENV_FILE% já existe. Nenhuma ação foi realizada.
) else (
    if exist %EXAMPLE_FILE% (
        copy %EXAMPLE_FILE% %ENV_FILE%
        echo ✅ Arquivo .env criado a partir de .env.example.
        echo 📝 Edite o arquivo .env com suas configurações reais.
    ) else (
        echo ❌ Arquivo .env.example não encontrado. Abortando.
    )
)

REM Cria o ambiente python e instala os requisitos
python -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt

echo Ambiente configurado com sucesso!

REM Pausa para o usuário ver o resultado
pause