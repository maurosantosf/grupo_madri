import pytest
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.exporter import export_relatorio

def test_export_relatorio(tmp_path):
    df_reconciled_vendas = pd.DataFrame({
        'Status Conciliação Sistema': ['Conciliado', 'Divergência de Valor', 'Apenas no Sistema', 'Apenas no PagBank']
    })
    
    df_reconciled_receb = pd.DataFrame({
        'Status Recebimento': ['Recebido', 'Pendente', 'Divergência de Recebimento']
    })
    
    df_mdr = pd.DataFrame({
        'Status MDR': ['Taxa Correta', 'Cobrado a Maior', 'Taxa Não Configurada']
    })
    
    filepath = tmp_path / "relatorio.xlsx"
    
    success = export_relatorio(str(filepath), df_reconciled_vendas, df_reconciled_receb, df_mdr)
    
    assert success is True
    assert os.path.exists(filepath)
    
    # Try reading back the Excel to ensure the 7 tabs are there
    excel = pd.ExcelFile(str(filepath))
    assert 'Resumo' in excel.sheet_names
    assert 'Vendas Conciliadas' in excel.sheet_names
    assert 'Divergências Valor' in excel.sheet_names
    assert 'Apenas no Sistema' in excel.sheet_names
    assert 'Apenas no PagBank' in excel.sheet_names
    assert 'Verificação Taxas (MDR)' in excel.sheet_names
    assert 'Recebimentos PagBank' in excel.sheet_names
    assert len(excel.sheet_names) == 7
