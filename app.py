import streamlit as st
from ui.config_tab import render_config_tab
from ui.conciliacao_tab import render_conciliacao_tab
from ui.mdr_tab import render_mdr_tab
from ui.recebimentos_tab import render_recebimentos_tab
from ui.relatorio_tab import render_relatorio_tab

st.set_page_config(page_title="Conciliador de Cartão de Crédito", layout="wide")

def main():
    st.title("Conciliador de Cartão de Crédito - EPS v1.0.0")
    
    # Initialize session state for our dataframes if not exist
    if 'df_sistema' not in st.session_state:
        st.session_state['df_sistema'] = None
    if 'df_vendas' not in st.session_state:
        st.session_state['df_vendas'] = None
    if 'df_receb' not in st.session_state:
        st.session_state['df_receb'] = None
        
    if 'df_reconciled_vendas' not in st.session_state:
        st.session_state['df_reconciled_vendas'] = None
    if 'df_reconciled_receb' not in st.session_state:
        st.session_state['df_reconciled_receb'] = None
    if 'df_mdr' not in st.session_state:
        st.session_state['df_mdr'] = None

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Configurações & Upload", 
        "Conciliação de Vendas", 
        "Taxas MDR", 
        "Recebimentos", 
        "Relatório Excel"
    ])
    
    with tab1:
        render_config_tab()
    
    with tab2:
        render_conciliacao_tab()
        
    with tab3:
        render_mdr_tab()
        
    with tab4:
        render_recebimentos_tab()
        
    with tab5:
        render_relatorio_tab()

if __name__ == "__main__":
    main()
