import pandas as pd
import numpy as np

def calculate_effective_rate(df_vendas):
    """
    Calcula a taxa efetiva (MDR) praticada em cada transação de Vendas.
    Taxa Efetiva = (Valor Taxa / Valor Bruto) * 100
    """
    df = df_vendas.copy()
    
    # Prevenir divisão por zero
    df['Taxa Efetiva (%)'] = np.where(
        df['Valor Bruto'] > 0,
        (df['Valor Taxa'] / df['Valor Bruto']) * 100,
        0.0
    )
    
    # Arredondar para 2 casas decimais
    df['Taxa Efetiva (%)'] = df['Taxa Efetiva (%)'].round(2)
    return df

def verify_rates(df_vendas_with_rates, df_taxas_contratadas):
    """
    Compara a taxa efetiva calculada com a taxa contratada.
    df_taxas_contratadas deve ter as colunas:
      - Bandeira
      - Forma de Pagamento
      - Parcela
      - Taxa Contratada (%)
    Chama calculate_effective_rate internamente se a coluna ainda não existir.
    """
    if 'Taxa Efetiva (%)' not in df_vendas_with_rates.columns:
        df_vendas_with_rates = calculate_effective_rate(df_vendas_with_rates)
    df = df_vendas_with_rates.copy()
    
    # Normalizar as chaves de junção para evitar erros de case/espaços
    # Parcela vazia (NaN/NA) = "à Vista" — débito e pix nunca têm parcela explícita
    _NA_VALS = {'NAN', '<NA>', 'NONE', 'NAT', ''}
    for col in ['Bandeira', 'Forma de Pagamento', 'Parcela']:
        if col in df.columns:
            key = df[col].fillna('à Vista').astype(str).str.strip().str.upper()
            if col == 'Parcela':
                key = key.apply(lambda v: 'À VISTA' if v in _NA_VALS else v)
            df[col + '_key'] = key
        if col in df_taxas_contratadas.columns:
            key = df_taxas_contratadas[col].fillna('à Vista').astype(str).str.strip().str.upper()
            if col == 'Parcela':
                key = key.apply(lambda v: 'À VISTA' if v in _NA_VALS else v)
            df_taxas_contratadas[col + '_key'] = key

    merged = pd.merge(
        df,
        df_taxas_contratadas,
        on=['Bandeira_key', 'Forma de Pagamento_key', 'Parcela_key'],
        how='left'
    )
    
    # Tolerância de 0.01%
    merged['Diferença Taxa (%)'] = merged['Taxa Efetiva (%)'] - merged['Taxa Contratada (%)']
    
    def get_status(row):
        if pd.isna(row['Taxa Contratada (%)']):
            return 'Taxa Não Configurada'
        if row['Diferença Taxa (%)'] > 0.01:
            return 'Cobrado a Maior'
        elif row['Diferença Taxa (%)'] < -0.01:
            return 'Cobrado a Menor'
        return 'Taxa Correta'
        
    merged['Status MDR'] = merged.apply(get_status, axis=1)
    
    # Calcula impacto financeiro: (Diferença Taxa / 100) * Valor Bruto
    merged['Impacto Financeiro (R$)'] = (merged['Diferença Taxa (%)'] / 100) * merged['Valor Bruto']
    merged['Impacto Financeiro (R$)'] = merged['Impacto Financeiro (R$)'].fillna(0.0).round(2)
    
    # Limpeza
    # Limpeza das colunas duplicadas e temporárias
    cols_to_drop = [c for c in merged.columns if c.endswith('_key') or c.endswith('_y')]
    merged = merged.drop(columns=cols_to_drop)
    
    # Renomear de volta os _x
    rename_dict = {
        'Bandeira_x': 'Bandeira',
        'Forma de Pagamento_x': 'Forma de Pagamento',
        'Parcela_x': 'Parcela'
    }
    merged = merged.rename(columns=rename_dict)
    
    return merged
