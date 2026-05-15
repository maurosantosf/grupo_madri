# Conciliador de Cartão de Crédito - Grupo Madri

Sistema automatizado para conciliação de vendas de cartão de crédito entre o Sistema Interno e o PagBank.

## Estrutura do Projeto

- `core/`: Lógica de processamento, leitura e conciliação.
- `ui/`: Interface do usuário (Streamlit).
- `tests/`: Bateria de testes automatizados.
- `docs/`: Documentação técnica e histórico do projeto.

## Como Usar

### Versão Portátil (Recomendado)
Para rodar o sistema sem instalar nada:
1. Extraia o pacote completo.
2. Execute o arquivo `Abrir_Sistema.vbs`.
3. O sistema abrirá automaticamente no seu navegador.

### Desenvolvimento
Se desejar rodar em ambiente de desenvolvimento:
1. Instale as dependências: `pip install -r requirements.txt`
2. Execute: `streamlit run app.py`

## Funcionalidades
- Conciliação Sistema vs PagBank (NSU/Autorização).
- Auditoria de Taxas MDR.
- Gráficos de Recebimentos e Fluxo de Caixa.
- Exportação de relatório completo em Excel.

## Requisitos de Sistema
- Windows 10 ou superior.
- Visual C++ Redistributable (Geralmente já presente no Windows).
