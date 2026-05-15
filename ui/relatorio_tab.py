import streamlit as st
import io
from core.exporter import export_relatorio

def render_relatorio_tab():
    st.header("Relatório Final")
    
    df_vendas = st.session_state.get('df_reconciled_vendas')
    df_receb = st.session_state.get('df_reconciled_receb')
    df_mdr = st.session_state.get('df_mdr')
    
    if df_vendas is None or df_receb is None or df_mdr is None:
        st.info("Aguardando execução da conciliação na aba de Configurações.")
        return
        
    st.markdown("""
    ### Baixar Relatório Completo
    O relatório conterá 7 abas organizadas:
    1. **Resumo**: Quantitativo geral da conciliação.
    2. **Vendas Conciliadas**: Transações encontradas em ambos os sistemas com valor correto.
    3. **Divergências Valor**: Transações encontradas, mas com divergência financeira.
    4. **Apenas no Sistema**: Transações ausentes na base PagBank Vendas.
    5. **Apenas no PagBank**: Transações PagBank não lançadas no Sistema.
    6. **Verificação Taxas (MDR)**: Cálculo efetivo e divergências de MDR.
    7. **Recebimentos PagBank**: Status de pagamento (Recebido vs Pendente).
    """)
    
    # We create a BytesIO buffer to hold the Excel data
    buffer = io.BytesIO()
    try:
        # Pasa o buffer diretamente para o export_relatorio
        export_relatorio(buffer, df_vendas, df_receb, df_mdr)
        
        st.download_button(
            label="📥 Download Relatório Excel",
            data=buffer.getvalue(),
            file_name="Relatorio_Conciliacao_Cartoes.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )
        
    except Exception as e:
        st.error(f"Erro ao gerar o relatório: {str(e)}")
