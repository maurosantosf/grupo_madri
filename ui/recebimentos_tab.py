import streamlit as st
import pandas as pd
import plotly.express as px

def render_recebimentos_tab():
    st.header("Recebimentos: Vendas ↔ Recebimentos PagBank")
    
    df = st.session_state.get('df_reconciled_receb')
    if df is None:
        st.info("Aguardando execução da conciliação na aba de Configurações.")
        return
        
    status_counts = df['Status Recebimento'].value_counts()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Vendas", len(df))
    with col2:
        st.metric("✅ Recebido", status_counts.get('Recebido', 0))
    with col3:
        st.metric("⚠️ Divergência", status_counts.get('Divergência de Recebimento', 0))
    with col4:
        st.metric("⏳ Pendente", status_counts.get('Pendente', 0))
        
    st.markdown("---")
    
    # Gráficos
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Status de Recebimentos")
        fig1 = px.pie(
            names=status_counts.index, 
            values=status_counts.values,
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig1, use_container_width=True)
        
    with col_chart2:
        st.subheader("Valor Pendente vs Recebido")
        valor_pendente = df[df['Status Recebimento'] == 'Pendente']['Valor Líquido'].sum()
        valor_recebido = df[df['Status Recebimento'] == 'Recebido']['Valor Líquido'].sum()
        valor_div = df[df['Status Recebimento'] == 'Divergência de Recebimento']['Valor Líquido'].sum()
        
        fig2 = px.bar(
            x=['Recebido', 'Pendente', 'Divergência'],
            y=[valor_recebido, valor_pendente, valor_div],
            labels={'x': 'Status', 'y': 'Valor (R$)'},
            color=['Recebido', 'Pendente', 'Divergência'],
            color_discrete_map={'Recebido': 'green', 'Pendente': 'orange', 'Divergência': 'red'}
        )
        st.plotly_chart(fig2, use_container_width=True)
        
    st.markdown("---")
    st.subheader("Transações Detalhadas")
    
    status_filter = st.multiselect(
        "Filtrar por Status de Recebimento",
        options=df['Status Recebimento'].unique(),
        default=df['Status Recebimento'].unique()
    )
    
    df_filtered = df[df['Status Recebimento'].isin(status_filter)]
    st.dataframe(df_filtered, use_container_width=True, hide_index=True)
