import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.reconciler import reconcile_vendas_sistema, reconcile_vendas_receb

def test_reconcile_vendas_sistema():
    df_sistema = pd.DataFrame({
        'NSU': ['123', '456', '111', '789'],
        'Autorização do TEF': ['ABC', 'DEF', '111', 'GHI'],
        'Valor': [10.0, 20.0, 30.0, 40.0]
    })
    
    df_vendas = pd.DataFrame({
        'Código da Venda': ['123', '000456', '999'],
        'Código de Autorização': ['ABC', 'DEF', 'ZZZ'],
        'Valor Bruto': [10.0, 20.05, 50.0]
    })
    
    merged = reconcile_vendas_sistema(df_sistema, df_vendas)
    
    # 123_ABC is in both and values match -> Conciliado
    # 456_DEF is in both, but values are 20.0 and 20.05 (difference <= 0.05) -> Conciliado
    # 111_111 is only in sys -> Apenas no Sistema
    # 789_GHI is only in sys -> Apenas no Sistema
    # 999_ZZZ is only in pb -> Apenas no PagBank
    
    # Check 123_ABC
    row_123 = merged[merged['Chave_Composta'] == '123_ABC'].iloc[0]
    assert row_123['Status Conciliação Sistema'] == 'Conciliado'
    
    # Check 456_DEF
    row_456 = merged[merged['Chave_Composta'] == '456_DEF'].iloc[0]
    assert row_456['Status Conciliação Sistema'] == 'Conciliado'
    
    # Check 111_111
    row_111 = merged[merged['Chave_Composta'] == '111_111'].iloc[0]
    assert row_111['Status Conciliação Sistema'] == 'Apenas no Sistema'
    
    # Check 999_ZZZ
    row_999 = merged[merged['Chave_Composta'] == '999_ZZZ'].iloc[0]
    assert row_999['Status Conciliação Sistema'] == 'Apenas no PagBank'

def test_reconcile_vendas_receb():
    df_vendas = pd.DataFrame({
        'Código da Transação': ['UUID1', 'UUID2', 'UUID3'],
        'Valor Líquido': [100.0, 200.0, 300.0]
    })
    
    df_receb = pd.DataFrame({
        'Código da transação': ['UUID1', 'UUID2', 'UUID2'],
        'Valor Líquido': [100.0, 150.0, 50.0],
        'Data do pagamento': [pd.to_datetime('2026-03-01'), pd.to_datetime('2026-03-02'), pd.to_datetime('2026-03-03')]
    })
    
    merged = reconcile_vendas_receb(df_vendas, df_receb)
    
    # UUID1 -> 100.0 == 100.0 -> Recebido
    row_1 = merged[merged['Chave_UUID'] == 'UUID1'].iloc[0]
    assert row_1['Status Recebimento'] == 'Recebido'
    
    # UUID2 -> 200.0 == (150.0 + 50.0) -> Recebido
    row_2 = merged[merged['Chave_UUID'] == 'UUID2'].iloc[0]
    assert row_2['Status Recebimento'] == 'Recebido'
    assert row_2['Data_Recebimento'] == pd.to_datetime('2026-03-03')
    
    # UUID3 -> Not in recebimentos -> Pendente
    row_3 = merged[merged['Chave_UUID'] == 'UUID3'].iloc[0]
    assert row_3['Status Recebimento'] == 'Pendente'
