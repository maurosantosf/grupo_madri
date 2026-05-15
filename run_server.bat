@echo off
:: Procura se o Streamlit ja esta rodando na porta 8501 e encerra o processo antigo
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8501" ^| find "LISTENING"') do taskkill /f /pid %%a >nul 2>&1

:: Verifica se existe o Python embutido (Versao Portatil)
if exist "python_embutido\python.exe" (
    :: Inicia o streamlit na porta fixa usando o Python embutido
    python_embutido\python.exe -m streamlit run app.py --server.port 8501
) else (
    :: Fallback para ambiente virtual padrao (Versao de Desenvolvimento)
    call venv\Scripts\activate.bat
    streamlit run app.py --server.port 8501
)
