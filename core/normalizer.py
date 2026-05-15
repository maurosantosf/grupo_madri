import pandas as pd
import re

def normalize_uuid(uuid_str):
    """Remove traços e transforma em maiúsculo."""
    if pd.isna(uuid_str):
        return uuid_str
    return str(uuid_str).replace("-", "").upper().strip()

def normalize_currency(val):
    """Converte string com R$ para float.

    Detecta automaticamente o formato:
    - Formato BR (1.234,56): vírgula como decimal → remove pontos, troca vírgula por ponto
    - Formato US/XLSX (1234.56): ponto como decimal → usa diretamente
    """
    if pd.isna(val):
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)

    val_str = str(val).upper().replace("R$", "").replace("\xa0", "").strip()

    if "," in val_str:
        # Formato brasileiro: ponto é separador de milhar, vírgula é decimal
        val_str = val_str.replace(".", "")
        val_str = val_str.replace(",", ".")
    # Senão, já está no formato decimal com ponto (ex: "11.85" vindo do XLSX)

    try:
        return float(val_str)
    except ValueError:
        return 0.0

def normalize_date(date_str, format="%d/%m/%Y"):
    """Padroniza data para datetime."""
    if pd.isna(date_str):
        return pd.NaT
    
    # Tenta converter usando o formato especificado.
    # Se falhar, o errors='coerce' retorna NaT.
    return pd.to_datetime(date_str, format=format, errors='coerce')
