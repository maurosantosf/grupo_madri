import streamlit as st
import pandas as pd
import tempfile
import os

from core.loader import load_pagbank_vendas, load_pagbank_receb, load_sistema
from core.reconciler import reconcile_vendas_sistema, reconcile_vendas_receb
from core.mdr import calculate_effective_rate, verify_rates

def _save_uploaded_file(uploaded_file):
    if uploaded_file is None:
        return None
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
        tmp.write(uploaded_file.getvalue())
        return tmp.name

def render_config_tab():
    st.header("Configurações e Upload de Arquivos")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("1. Vendas PagBank")
        file_vendas = st.file_uploader("Upload CSV Vendas", type=['csv'], key='vendas_upload')
        
    with col2:
        st.subheader("2. Recebimentos PagBank")
        file_receb = st.file_uploader("Upload CSV Recebimentos", type=['csv'], key='receb_upload')
        
    with col3:
        st.subheader("3. Relatório do Sistema")
        file_sistema = st.file_uploader("Upload XLSX Sistema", type=['xlsx'], key='sistema_upload')
        
    st.markdown("---")
    st.subheader("Tabela de Taxas Contratadas (MDR)")
    
    # Default rates
    if 'df_taxas_contratadas' not in st.session_state:
        st.session_state['df_taxas_contratadas'] = pd.DataFrame({
            'Bandeira': ['MASTERCARD', 'VISA', 'ELO', 'MASTERCARD', 'VISA', 'ELO', 'ALELO', 'PIX'],
            'Forma de Pagamento': ['CRÉDITO', 'CRÉDITO', 'CRÉDITO', 'DÉBITO', 'DÉBITO', 'DÉBITO', 'VOUCHER', 'PIX'],
            'Parcela': ['À VISTA', 'À VISTA', 'À VISTA', 'À VISTA', 'À VISTA', 'À VISTA', 'À VISTA', 'À VISTA'],
            'Taxa Contratada (%)': [2.49, 2.49, 3.50, 1.00, 1.00, 1.50, 0.00, 0.00]
        })
        
    edited_rates = st.data_editor(st.session_state['df_taxas_contratadas'], num_rows="dynamic", use_container_width=True)
    st.session_state['df_taxas_contratadas'] = edited_rates
    
    if st.button("Executar Conciliação", type="primary", use_container_width=True):
        if not file_vendas or not file_receb or not file_sistema:
            st.warning("Por favor, faça o upload dos três arquivos antes de executar a conciliação.")
            return
            
        with st.spinner("Processando arquivos..."):
            try:
                path_vendas = _save_uploaded_file(file_vendas)
                path_receb = _save_uploaded_file(file_receb)
                path_sys = _save_uploaded_file(file_sistema)
                
                # Load
                df_vendas = load_pagbank_vendas(path_vendas)
                df_receb = load_pagbank_receb(path_receb)
                df_sys = load_sistema(path_sys)
                
                # Reconcile
                df_reconciled_vendas = reconcile_vendas_sistema(df_sys, df_vendas)
                df_reconciled_receb = reconcile_vendas_receb(df_vendas, df_receb)
                
                # MDR
                df_vendas_mdr = calculate_effective_rate(df_vendas)
                df_mdr = verify_rates(df_vendas_mdr, st.session_state['df_taxas_contratadas'])
                
                # Store in session state
                st.session_state['df_sistema'] = df_sys
                st.session_state['df_vendas'] = df_vendas
                st.session_state['df_receb'] = df_receb
                st.session_state['df_reconciled_vendas'] = df_reconciled_vendas
                st.session_state['df_reconciled_receb'] = df_reconciled_receb
                st.session_state['df_mdr'] = df_mdr
                
                st.success("Conciliação executada com sucesso! Navegue pelas abas acima para visualizar os resultados.")
            except Exception as e:
                st.error(f"Erro ao processar a conciliação: {e}")
