Set WshShell = CreateObject("WScript.Shell")
' Executa o arquivo batch ocultando completamente a janela (0) e rodando em background (False)
WshShell.Run "cmd /c run_server.bat", 0, False

' Aguarda 3 segundos para o servidor Streamlit iniciar
WScript.Sleep 3000

' Abre o navegador padrao na porta do sistema
WshShell.Run "http://localhost:8501"
