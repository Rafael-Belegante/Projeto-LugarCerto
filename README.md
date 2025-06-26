# 📦 LugarCerto - Sistema de Achados e Perdidos

**LugarCerto** é um sistema web desenvolvido com **Python (Flask)** para auxiliar instituições (como escolas ou empresas) a registrarem, organizarem e localizarem itens perdidos. O projeto foi criado para o ambiente do **SENAI**, mas é totalmente adaptável a outras instituições.

---

## 🚀 Funcionalidades

### 👨‍👩‍👧‍👦 Para Usuários
- Visualização pública dos objetos perdidos.
- Registro de novos usuários.
- Login de usuários.
- Reivindicação de objetos.
- Acompanhamento do status das reivindicações.

### 🛠️ Para Administradores
- Cadastro de novos usuários e administradores.
- Gerenciamento de objetos perdidos (adicionar, editar, excluir).
- Aprovação ou rejeição de reivindicações feitas por usuários.
- Visualização de todos os objetos e usuários.

---

## 📷 Interface

- Interface moderna, responsiva e adaptada para desktop e dispositivos móveis (com foco para Desktops).
- Cards organizados com informações e imagem dos objetos.

---

## 🔑 Requisitos

- Python > 8.
- Dependências listadas dentro do requirements.txt.

---

## ⚙️ Instalação

### 🪟 Windows

Execute:

```bash
setup_env.bat
```

Em seguida:

```bash
start_site.bat
```

### 🐧 Linux / macOS

Execute:

```bash
chmod +x setup_env.sh
./setup_env.sh
```

Em seguida:

```bash
chmod +x setup_env.sh
./start_site.sh
```

---

## 🧪 Como Testar o Projeto

1) Acesse no navegador:

```
http://127.0.0.1:5000/
```

2) Use o usuário **admin pré-configurado** para acessar o painel administrativo:

```
Email: admin@lugarcerto.com
Senha: admin123
```

---

## 🔐 Segurança

- Para produção:
  - Ative HTTPS com proxy reverso (como Nginx).
  - Use variáveis de ambiente para configs sensíveis.
  - Faça backups regulares do banco (`objetos.db`) ou outro utilizado.
  - Logging simples para ações de auditoria.

---

## 📬 Contato

Desenvolvido por Rafael Belegante

GitHub: https://github.com/Rafael-Belegante

---
