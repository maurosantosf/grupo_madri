import pandas as pd
import os
from .normalizer import normalize_uuid, normalize_currency, normalize_date

def load_pagbank_vendas(filepath):
    """Carrega o arquivo CSV de Vendas PagBank."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")
    
    # O arquivo tem delimitador ';' e encoding utf-8 com BOM
    df = pd.read_csv(filepath, sep=';', encoding='utf-8-sig', dtype=str)
    
    # Aplica as normalizações nas colunas se existirem
    if 'Código da Transação' in df.columns:
        df['Código da Transação'] = df['Código da Transação'].apply(normalize_uuid)
    
    # Convertendo valores que usam vírgula (R$ ...)
    cols_to_normalize = ['Valor Bruto', 'Valor Taxa', 'Valor Repasse', 'Valor Líquido']
    for col in cols_to_normalize:
        if col in df.columns:
            df[col] = df[col].apply(normalize_currency)
            
    # Datas
    date_cols = ['Data da Transação', 'Data prevista de liberação', 'Data do cancelamento']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format="%d/%m/%Y %H:%M", errors='coerce').dt.strftime('%d/%m/%Y')
            
    return df

def load_pagbank_receb(filepath):
    """Carrega o arquivo CSV de Recebimentos PagBank, ignorando as 3 primeiras linhas."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")
    
    df = pd.read_csv(filepath, sep=';', encoding='utf-8-sig', skiprows=3, dtype=str)
    
    # Remove a coluna Unnamed que é gerada se a linha tiver um ; sobrando no final
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # Normalizações
    if 'Código da transação' in df.columns:
        df['Código da transação'] = df['Código da transação'].apply(normalize_uuid)
    
    if 'Código do pagamento (Cashout)' in df.columns:
        df['Código do pagamento (Cashout)'] = df['Código do pagamento (Cashout)'].apply(normalize_uuid)
        
    if 'Valor Líquido' in df.columns:
        df['Valor Líquido'] = df['Valor Líquido'].apply(normalize_currency)
        
    if 'Data do pagamento' in df.columns:
        # Aqui a data geralmente é só data, sem hora
        df['Data do pagamento'] = pd.to_datetime(df['Data do pagamento'], format="%d/%m/%Y", errors='coerce').dt.strftime('%d/%m/%Y')
        
    return df

def load_sistema(filepath):
    """Carrega o arquivo XLSX do Sistema, ignorando a 1ª linha."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")
    
    df = pd.read_excel(filepath, skiprows=1, dtype=str)
    
    # Normalizações
    if 'CÓDIGO' in df.columns:
        df['CÓDIGO'] = df['CÓDIGO'].apply(normalize_uuid)
        
    # Verificar colunas de valor
    for col in df.columns:
        if 'VALOR' in col.upper():
            df[col] = df[col].apply(normalize_currency)
            
        if 'DATA' in col.upper() or 'EMISS' in col.upper() or 'VENCIMENTO' in col.upper():
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce').dt.strftime('%d/%m/%Y')
            
    return df
