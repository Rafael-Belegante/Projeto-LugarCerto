@echo off
REM Ativa o ambiente virtual (ajuste o caminho se estiver em outra pasta)
call venv\Scripts\activate.bat

REM Executa o sistema
python run.py

pause
