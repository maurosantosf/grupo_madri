import pytest
from streamlit.testing.v1 import AppTest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_app_loads_successfully():
    """
    Testa se o aplicativo Streamlit principal carrega sem erros de sintaxe ou execução.
    """
    app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app.py")
    
    # Executa a aplicação e verifica se não há exceções lançadas durante o parse inicial
    at = AppTest.from_file(app_path).run()
    
    assert not at.exception, f"App crashed with exception: {at.exception}"
    
    # Verifica se o título aparece corretamente
    assert "Conciliador de Cartão de Crédito - EPS" in at.title[0].value
    
    # Verifica se as abas foram criadas
    assert len(at.tabs) >= 5
    assert at.tabs[0].label == "Configurações & Upload"
