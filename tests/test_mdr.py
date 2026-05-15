import pytest
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.mdr import calculate_effective_rate, verify_rates

def test_calculate_effective_rate():
    df_vendas = pd.DataFrame({
        'Valor Bruto': [100.0, 50.0, 0.0],
        'Valor Taxa': [2.5, 0.5, 0.0]
    })
    
    res = calculate_effective_rate(df_vendas)
    
    assert res.loc[0, 'Taxa Efetiva (%)'] == 2.50
    assert res.loc[1, 'Taxa Efetiva (%)'] == 1.00
    assert res.loc[2, 'Taxa Efetiva (%)'] == 0.00

def test_verify_rates():
    df_vendas = pd.DataFrame({
        'Bandeira': ['Visa', 'Mastercard', 'Elo'],
        'Forma de Pagamento': ['Crédito', 'Débito', 'Crédito'],
        'Parcela': ['À Vista', 'À Vista', '2 a 6'],
        'Valor Bruto': [100.0, 50.0, 200.0],
        'Taxa Efetiva (%)': [2.50, 1.00, 3.50]
    })
    
    df_contratadas = pd.DataFrame({
        'Bandeira': ['Visa', 'Mastercard'],
        'Forma de Pagamento': ['Crédito', 'Débito'],
        'Parcela': ['À Vista', 'À Vista'],
        'Taxa Contratada (%)': [2.49, 1.00]
    })
    
    res = verify_rates(df_vendas, df_contratadas)
    
    # Visa - Crédito - À Vista: 2.50 vs 2.49 -> Diff: +0.01 -> <= 0.01 tolerance -> Taxa Correta
    assert res.loc[0, 'Status MDR'] == 'Taxa Correta'
    
    # Let's change the tolerance test. If diff is 0.02, it should be Cobrado a Maior
    df_vendas.loc[0, 'Taxa Efetiva (%)'] = 2.52
    res = verify_rates(df_vendas, df_contratadas)
    assert res.loc[0, 'Status MDR'] == 'Cobrado a Maior'
    assert res.loc[0, 'Impacto Financeiro (R$)'] == 0.03 # (0.03/100) * 100 = 0.03
    
    # Mastercard - Débito - À Vista: 1.00 vs 1.00 -> Taxa Correta
    assert res.loc[1, 'Status MDR'] == 'Taxa Correta'
    
    # Elo - Crédito - 2 a 6: Missing config
    assert res.loc[2, 'Status MDR'] == 'Taxa Não Configurada'
