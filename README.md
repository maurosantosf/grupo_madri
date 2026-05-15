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

## Histórico de Versões e Backups
Este projeto utiliza o sistema de versionamento **Git**. Cada versão estável é marcada com uma "Tag", permitindo retornar a qualquer estado anterior do sistema se necessário.

- **v1.0.0** (15/05/2026): **Versão Inicial Estável**.
  - Implementação completa da lógica de conciliação NSU/Autorização.
  - Módulo de auditoria de taxas MDR.
  - Exportação de relatórios multifolhas em Excel.
  - Interface Streamlit com 5 abas operacionais.
