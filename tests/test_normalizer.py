import pytest
import pandas as pd
import numpy as np

# Adjust the path to import core
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.normalizer import normalize_uuid, normalize_currency, normalize_date

def test_normalize_uuid():
    assert normalize_uuid("00009E5D-CB2F-496F-B2C2-4A5BC95B109A") == "00009E5DCB2F496FB2C24A5BC95B109A"
    assert normalize_uuid(" 1234-abcd-EFGH ") == "1234ABCDEFGH"
    assert normalize_uuid(np.nan) is np.nan
    assert pd.isna(normalize_uuid(pd.NA))

def test_normalize_currency():
    # Formato brasileiro (vírgula decimal)
    assert normalize_currency("R$ 4,53") == 4.53
    assert normalize_currency(" R$  1.234,56 ") == 1234.56
    assert normalize_currency("10,00") == 10.00
    assert normalize_currency("-5,50") == -5.50
    # Formato XLSX (ponto decimal, sem vírgula — vindo de células numéricas do Excel)
    assert normalize_currency("11.85") == 11.85
    assert normalize_currency("100.22") == 100.22
    assert normalize_currency("7.82") == 7.82
    # Tipos nativos Python
    assert normalize_currency(100.5) == 100.5
    assert normalize_currency(np.nan) == 0.0

def test_normalize_date():
    # Test DD/MM/YYYY
    d1 = normalize_date("31/03/2026")
    assert d1.year == 2026 and d1.month == 3 and d1.day == 31
    
    # Test DD/MM/YYYY HH:MM
    d2 = normalize_date("15/03/2026 12:32", format="%d/%m/%Y %H:%M")
    assert d2.year == 2026 and d2.month == 3 and d2.day == 15 and d2.hour == 12 and d2.minute == 32
    
    # Test NaT
    assert pd.isna(normalize_date(np.nan))
