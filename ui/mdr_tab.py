import streamlit as st
import pandas as pd

def render_mdr_tab():
    st.header("Verificação de Taxas (MDR)")
    
    df = st.session_state.get('df_mdr')
    if df is None:
        st.info("Aguardando execução da conciliação na aba de Configurações.")
        return
        
    status_counts = df['Status MDR'].value_counts()
    impacto_total = df['Impacto Financeiro (R$)'].sum()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("✅ Taxa Correta", status_counts.get('Taxa Correta', 0))
    with col2:
        st.metric("⚠️ Cobrado a Maior", status_counts.get('Cobrado a Maior', 0))
    with col3:
        st.metric("⚠️ Cobrado a Menor", status_counts.get('Cobrado a Menor', 0))
    with col4:
        st.metric("❌ Não Configurada", status_counts.get('Taxa Não Configurada', 0))
    with col5:
        st.metric("Impacto Total (R$)", f"R$ {impacto_total:.2f}")
        
    st.markdown("---")
    
    # Agrupamento resumo
    st.subheader("Resumo por Agrupamento")
    
    agrupado = df.groupby(['Bandeira', 'Forma de Pagamento', 'Parcela']).agg(
        Qtd_Transacoes=('Valor Bruto', 'count'),
        Valor_Bruto_Total=('Valor Bruto', 'sum'),
        Impacto_Total=('Impacto Financeiro (R$)', 'sum')
    ).reset_index()
    
    st.dataframe(agrupado, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.subheader("Transações Detalhadas")
    
    status_filter = st.multiselect(
        "Filtrar por Status MDR",
        options=df['Status MDR'].unique(),
        default=df['Status MDR'].unique()
    )
    
    df_filtered = df[df['Status MDR'].isin(status_filter)]
    st.dataframe(df_filtered, use_container_width=True, hide_index=True)
