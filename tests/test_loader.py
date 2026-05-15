import pytest
import pandas as pd
import os

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.loader import load_pagbank_vendas, load_pagbank_receb, load_sistema

def test_load_pagbank_vendas(tmp_path):
    # Setup mock CSV
    content = """Documento;Estabelecimento;Nome Cliente;E-mail Cliente;Código da Transação;Data da Transação;Data prevista de liberação;Data do cancelamento;Bandeira;Forma de Pagamento;Parcela;Valor Bruto;Valor Taxa;Valor Repasse;Valor Líquido;Status;Número do Cartão;Código NSU;Código de Autorização;Identificação da Maquininha;Código da Venda;Código Referência;Nome Comprador;E-mail Comprador;Código TX ID (PIX);ID Split
;;MADRI;madri@gmail.com;00007AC1-3531-44B5-80E2-2998ED7EA355;21/03/2026 06:53;;;Alelo;Voucher;;R$ 36,85;R$ 0,00;;R$ 36,85;Aprovada;509809******4721;-;901535;7200091904079655;500057;;;;;
"""
    file_path = tmp_path / "vendas_mock.csv"
    with open(file_path, "w", encoding="utf-8-sig") as f:
        f.write(content)
        
    df = load_pagbank_vendas(str(file_path))
    
    assert len(df) == 1
    assert df.loc[0, 'Código da Transação'] == "00007AC1353144B580E22998ED7EA355"
    assert df.loc[0, 'Valor Bruto'] == 36.85
    assert df.loc[0, 'Valor Líquido'] == 36.85
    assert df.loc[0, 'Valor Taxa'] == 0.0

def test_load_pagbank_receb(tmp_path):
    content = """Cabecalho 1
Cabecalho 2
Cabecalho 3
CNPJ;Razão Social;Código da transação;Código do pagamento (Cashout);Código de recebimento;Data do pagamento;Bandeira;Produto;Valor Líquido;Banco;Agência;Conta;
16879613000180;MADRI;748A12C8A940422BA9CC583736978171;9628056153AB45CDA4C806F6163F6366;7AE1FFE7AC3145329D03B58CAEA4C129;31/03/2026;Mastercard Débito;DÉBITO;R$ 4,53;PagBank;0001;385700463
"""
    file_path = tmp_path / "receb_mock.csv"
    with open(file_path, "w", encoding="utf-8-sig") as f:
        f.write(content)
        
    df = load_pagbank_receb(str(file_path))
    
    assert len(df) == 1
    assert df.loc[0, 'Código da transação'] == "748A12C8A940422BA9CC583736978171"
    assert df.loc[0, 'Valor Líquido'] == 4.53
    assert df.loc[0, 'Data do pagamento'] == "31/03/2026"

def test_load_sistema(tmp_path):
    # Setup mock XLSX
    file_path = tmp_path / "sistema_mock.xlsx"
    df_mock = pd.DataFrame({
        "Col1": ["Should be skipped", "CÓDIGO", "1234-ABCD"],
        "Col2": ["Skip 2", "VALOR", "R$ 10,50"],
        "Col3": ["Skip 3", "DATA", "15/03/2026"]
    })
    df_mock.to_excel(file_path, index=False, header=False)
    
    df = load_sistema(str(file_path))
    assert len(df) == 1
    assert df.loc[0, 'CÓDIGO'] == "1234ABCD"
    assert df.loc[0, 'VALOR'] == 10.5
    assert df.loc[0, 'DATA'] == "15/03/2026"
