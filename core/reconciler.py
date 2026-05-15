import pandas as pd
import numpy as np

def _clean_key(series):
    """Remove espaços e zeros à esquerda para tornar a chave mais robusta."""
    s = series.astype(str).str.strip().str.lstrip('0')
    return s.replace(['nan', 'None', '', 'NaN', 'NaT'], np.nan)

def reconcile_vendas_sistema(df_sistema, df_vendas):
    """
    Concilia o relatório do Sistema (Excel) com as Vendas do PagBank (CSV).
    Chaves de conciliação: NSU e Autorização.
    """
    sys_df = df_sistema.copy()
    pb_df = df_vendas.copy()
    
    # Padronizar nomes das colunas de chaves
    sys_df['Chave_NSU'] = _clean_key(sys_df.get('NSU', pd.Series(dtype=str)))
    sys_df['Chave_Aut'] = _clean_key(sys_df.get('Autorização do TEF', pd.Series(dtype=str)))
    
    pb_df['Chave_NSU'] = _clean_key(pb_df.get('Código da Venda', pd.Series(dtype=str)))
    pb_df['Chave_Aut'] = _clean_key(pb_df.get('Código de Autorização', pd.Series(dtype=str)))
    
    # Criar chave composta, tratando NaNs
    sys_df['Chave_Composta'] = sys_df['Chave_NSU'].fillna('VAZIO') + "_" + sys_df['Chave_Aut'].fillna('VAZIO')
    pb_df['Chave_Composta'] = pb_df['Chave_NSU'].fillna('VAZIO') + "_" + pb_df['Chave_Aut'].fillna('VAZIO')
    
    # Precisamos tratar os casos onde a chave é 'VAZIO_VAZIO' (não há NSU nem Aut)
    # Para evitar Produto Cartesiano no join, vamos dar uma chave única para eles
    # assim eles cairão como 'Apenas no Sistema' ou 'Apenas no PagBank'
    mask_sys_vazio = sys_df['Chave_Composta'] == 'VAZIO_VAZIO'
    if mask_sys_vazio.any():
        sys_df.loc[mask_sys_vazio, 'Chave_Composta'] = [f'SYS_UNMATCHED_{i}' for i in range(mask_sys_vazio.sum())]

    mask_pb_vazio = pb_df['Chave_Composta'] == 'VAZIO_VAZIO'
    if mask_pb_vazio.any():
        pb_df.loc[mask_pb_vazio, 'Chave_Composta'] = [f'PB_UNMATCHED_{i}' for i in range(mask_pb_vazio.sum())]
    
    # Realizar Outer Join
    merged = pd.merge(
        sys_df, 
        pb_df, 
        on='Chave_Composta', 
        how='outer', 
        suffixes=('_sys', '_pb'),
        indicator=True
    )
    
    # Classificar o status da conciliação
    def get_status(row):
        if row['_merge'] == 'left_only':
            return 'Apenas no Sistema'
        elif row['_merge'] == 'right_only':
            return 'Apenas no PagBank'
        elif row['_merge'] == 'both':
            # Checar divergência de valor
            val_sys = row.get('Valor', 0.0)
            val_pb = row.get('Valor Bruto', 0.0)
            
            # Se a diferença for maior que 0.05 centavos, considera divergência
            if pd.isna(val_sys) or pd.isna(val_pb):
                return 'Divergência de Valor'
            if round(abs(val_sys - val_pb), 2) > 0.05:
                return 'Divergência de Valor'
            return 'Conciliado'
        return 'Erro'

    merged['Status Conciliação Sistema'] = merged.apply(get_status, axis=1)
    
    # Cleanup _merge
    merged = merged.drop(columns=['_merge'])
    return merged

def reconcile_vendas_receb(df_vendas, df_receb):
    """
    Cruza as Vendas PagBank com os Recebimentos PagBank.
    Chave: Código da Transação (UUID).
    """
    v_df = df_vendas.copy()
    r_df = df_receb.copy()
    
    # Chaves (já foram normalizadas no loader, mas garantimos que não haja nan problems)
    v_df['Chave_UUID'] = v_df.get('Código da Transação', pd.Series(dtype=str)).astype(str).str.strip()
    r_df['Chave_UUID'] = r_df.get('Código da transação', pd.Series(dtype=str)).astype(str).str.strip()
    
    # Agrupar recebimentos por UUID, somando o valor líquido (caso haja pagamentos parciais)
    # Pegamos também a data máxima de recebimento para a transação
    r_agg = r_df.groupby('Chave_UUID').agg(
        Recebido_Liquido=('Valor Líquido', 'sum'),
        Data_Recebimento=('Data do pagamento', 'max')
    ).reset_index()
    
    # Left join Vendas com Recebimentos agrupados
    merged = pd.merge(
        v_df,
        r_agg,
        on='Chave_UUID',
        how='left'
    )
    
    def get_status(row):
        if pd.isna(row['Recebido_Liquido']):
            return 'Pendente'
        
        val_venda = row.get('Valor Líquido', 0.0)
        val_receb = row['Recebido_Liquido']
        
        # Considerar divergência se a diferença for maior que 0.02
        if round(abs(val_venda - val_receb), 2) > 0.02:
            return 'Divergência de Recebimento'
        
        return 'Recebido'

    merged['Status Recebimento'] = merged.apply(get_status, axis=1)
    return merged
