import pandas as pd

def export_relatorio(filepath, df_reconciled_vendas, df_reconciled_receb, df_mdr):
    """
    Gera um relatório Excel com múltiplas abas formatadas.
    """
    writer = pd.ExcelWriter(filepath, engine='xlsxwriter')
    
    # 1. Resumo
    resumo_data = []
    
    # Conciliação Vendas
    status_vendas = df_reconciled_vendas['Status Conciliação Sistema'].value_counts().to_dict()
    for status, count in status_vendas.items():
        resumo_data.append({'Categoria': 'Vendas - ' + status, 'Quantidade': count})
        
    # Conciliação Recebimentos
    status_receb = df_reconciled_receb['Status Recebimento'].value_counts().to_dict()
    for status, count in status_receb.items():
        resumo_data.append({'Categoria': 'Recebimentos - ' + status, 'Quantidade': count})
        
    # MDR
    status_mdr = df_mdr['Status MDR'].value_counts().to_dict()
    for status, count in status_mdr.items():
        resumo_data.append({'Categoria': 'MDR - ' + status, 'Quantidade': count})
        
    df_resumo = pd.DataFrame(resumo_data)
    df_resumo.to_excel(writer, sheet_name='Resumo', index=False)
    
    # 2. Vendas Conciliadas
    df_conciliado = df_reconciled_vendas[df_reconciled_vendas['Status Conciliação Sistema'] == 'Conciliado']
    df_conciliado.to_excel(writer, sheet_name='Vendas Conciliadas', index=False)
    
    # 3. Divergências Vendas
    df_div = df_reconciled_vendas[df_reconciled_vendas['Status Conciliação Sistema'] == 'Divergência de Valor']
    df_div.to_excel(writer, sheet_name='Divergências Valor', index=False)
    
    # 4. Apenas no Sistema
    df_sys_only = df_reconciled_vendas[df_reconciled_vendas['Status Conciliação Sistema'] == 'Apenas no Sistema']
    df_sys_only.to_excel(writer, sheet_name='Apenas no Sistema', index=False)
    
    # 5. Apenas no PagBank
    df_pb_only = df_reconciled_vendas[df_reconciled_vendas['Status Conciliação Sistema'] == 'Apenas no PagBank']
    df_pb_only.to_excel(writer, sheet_name='Apenas no PagBank', index=False)
    
    # 6. Relatório MDR
    df_mdr.to_excel(writer, sheet_name='Verificação Taxas (MDR)', index=False)
    
    # 7. Relatório Recebimentos
    df_reconciled_receb.to_excel(writer, sheet_name='Recebimentos PagBank', index=False)
    
    # Formatação XlsxWriter (Opcional)
    workbook = writer.book
    format_header = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1})
    
    for sheet_name, worksheet in writer.sheets.items():
        worksheet.set_row(0, None, format_header)
        # Ajusta largura de cada coluna ao conteúdo
        df_sheet = {
            'Resumo': df_resumo,
            'Vendas Conciliadas': df_conciliado,
            'Divergências Valor': df_div,
            'Apenas no Sistema': df_sys_only,
            'Apenas no PagBank': df_pb_only,
            'Verificação Taxas (MDR)': df_mdr,
            'Recebimentos PagBank': df_reconciled_receb,
        }.get(sheet_name)
        if df_sheet is not None:
            for i, col in enumerate(df_sheet.columns):
                max_len = max(len(str(col)), df_sheet[col].astype(str).map(len).max() if len(df_sheet) > 0 else 0)
                worksheet.set_column(i, i, min(max_len + 2, 50))

    writer.close()
    return True
