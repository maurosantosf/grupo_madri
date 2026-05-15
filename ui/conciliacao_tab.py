import streamlit as st
import pandas as pd

def render_conciliacao_tab():
    st.header("Conciliação: Sistema ↔ PagBank Vendas")
    
    df = st.session_state.get('df_reconciled_vendas')
    if df is None:
        st.info("Aguardando execução da conciliação na aba de Configurações.")
        return
        
    # Metrics
    status_counts = df['Status Conciliação Sistema'].value_counts()
    total = len(df)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Transações", total)
    with col2:
        st.metric("✅ Conciliado", status_counts.get('Conciliado', 0))
    with col3:
        st.metric("⚠️ Divergência de Valor", status_counts.get('Divergência de Valor', 0))
    with col4:
        st.metric("❌ Apenas Sistema", status_counts.get('Apenas no Sistema', 0))
    with col5:
        st.metric("❌ Apenas PagBank", status_counts.get('Apenas no PagBank', 0))
        
    st.markdown("---")
    
    # Filter
    status_filter = st.multiselect(
        "Filtrar por Status",
        options=df['Status Conciliação Sistema'].unique(),
        default=df['Status Conciliação Sistema'].unique()
    )
    
    df_filtered = df[df['Status Conciliação Sistema'].isin(status_filter)]
    
    st.dataframe(
        df_filtered,
        use_container_width=True,
        hide_index=True
    )
