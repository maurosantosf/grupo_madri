# Plano de Implementação — Conciliador de Cartão de Crédito
**Empresa:** MADRI SILVA PAIVA COMERCIO LTDA  
**CNPJ:** 16.879.613/0001-80  
**Operadora foco:** PagBank (PagSeguro)  
**Data do plano:** 12/05/2026  

---

## 1. Contexto e Objetivos

### Problema
A empresa possui dois fluxos de informação sobre as vendas com cartão que nunca são cruzados:

| Fonte | O que registra |
|---|---|
| **Sistema interno** | Cada venda lançada no PDV (NSU + autorização + valor bruto) |
| **PagBank VENDAS** | Cada transação aprovada/cancelada pela operadora (com taxa real cobrada) |
| **PagBank RECEB** | Cada liquidação financeira creditada na conta bancária |

Sem a conciliação desses três fluxos, a empresa não sabe:
1. Se todas as vendas lançadas no sistema foram de fato processadas e aprovadas pelo PagBank
2. Se as taxas MDR cobradas estão de acordo com o contrato firmado
3. Se há vendas aprovadas pelo PagBank que ainda não foram pagas / creditadas na conta

### Objetivos do sistema
- **Conciliação Sistema ↔ PagBank VENDAS:** garantir que tudo que foi vendido no cartão existe na operadora
- **Verificação de MDR:** comparar a taxa contratada com a taxa efetivamente cobrada em cada transação
- **Vendas vs Recebimentos:** verificar se todas as vendas aprovadas geraram o crédito na conta

---

## 2. Análise dos Arquivos-Fonte

### 2.1 Volume de dados (amostral)

| Mês | PagBank VENDAS | PagBank RECEB | Sistema |
|---|---|---|---|
| Mar/2026 | 29.473 registros | 28.271 registros | 24.394 registros |
| Abr/2026 | 26.241 registros | 24.828 registros | 23.272 registros |

### 2.2 PagBank VENDAS (`PAGBANK_VENDAS_MM-AAAA.csv`)

- **Formato:** CSV, separador `;`, encoding `UTF-8-BOM`
- **Linha 1:** Cabeçalho com nomes de colunas
- **Formas de pagamento:** Débito, Crédito, Pix, Voucher
- **Status possíveis:** `Aprovada`, `Cancelada`

**Colunas relevantes:**

| Coluna | Descrição | Uso na conciliação |
|---|---|---|
| `Código da Transação` | UUID da transação (ex: `00009E5D-CB2F-496F-B2C2-4A5BC95B109A`) | Chave p/ RECEB |
| `Data da Transação` | Data e hora da venda | Filtros e relatórios |
| `Bandeira` | Mastercard, Visa, Elo, Amex, Alelo, Ticket | Verificação MDR |
| `Forma de Pagamento` | Débito, Crédito, Pix, Voucher | Verificação MDR |
| `Parcela` | "à Vista", "pré pago", ou número | Verificação MDR |
| `Valor Bruto` | Valor cobrado do cliente (R$) | Conciliação de valor |
| `Valor Taxa` | Taxa MDR cobrada pelo PagBank (R$) | Verificação MDR |
| `Valor Líquido` | Valor a receber após taxa (R$) | Conciliação financeira |
| `Status` | Aprovada / Cancelada | Filtro |
| `Código NSU` | NSU completo da operadora (12 dígitos) | Referência |
| `Código de Autorização` | Código de autorização do cartão | **Chave p/ Sistema** |
| `Identificação da Maquininha` | ID do terminal POS | Controle por terminal |
| `Código da Venda` | Número sequencial do PDV (6 dígitos) | **Chave p/ Sistema** |

**Taxas MDR observadas (médias em Mar/2026):**

| Modalidade | Bandeira | Taxa média | Mín | Máx |
|---|---|---|---|---|
| Débito | Mastercard | 0,819% | 0,000% | 2,369% |
| Débito | Visa | 0,820% | 0,000% | 2,363% |
| Débito | Elo | 0,818% | 0,645% | 1,000% |
| Crédito à Vista | Mastercard | 2,650% | 2,451% | 2,913% |
| Crédito à Vista | Visa | 2,650% | 2,439% | 2,857% |
| Crédito à Vista | Elo | 2,649% | 2,482% | 2,750% |
| Crédito à Vista | Amex | 3,997% | 3,924% | 4,059% |
| Crédito pré-pago | Mastercard | 2,630% | 2,000% | 2,750% |

> ⚠️ Observado: algumas transações de débito com taxa 0,000% e picos de ~2,37% — anomalias a investigar.

---

### 2.3 PagBank RECEB (`PAGBANK_RECEB_MM-AAAA.csv`)

- **Formato:** CSV, separador `;`, encoding `UTF-8-BOM`
- **Linhas 1–3:** Cabeçalho institucional (empresa, CNPJ, período) — devem ser ignoradas
- **Linha 4:** Cabeçalho das colunas
- **Linha 5+:** Dados

**Colunas relevantes:**

| Coluna | Descrição | Uso na conciliação |
|---|---|---|
| `Código da transação` | UUID sem traços (32 hex) | **Chave p/ VENDAS** |
| `Código do pagamento (Cashout)` | ID do lote de pagamento | Rastreio financeiro |
| `Código de recebimento` | ID do recebimento individual | Rastreio financeiro |
| `Data do pagamento` | Data em que o crédito entrou na conta | Fluxo de caixa |
| `Bandeira` | Ex: "Mastercard Débito", "PIX" | Categorização |
| `Produto` | "DÉBITO", "CRÉDITO", "PIX" | Categorização |
| `Valor Líquido` | Valor creditado na conta (R$) | Conciliação financeira |

**Chave de ligação com VENDAS:**  
`RECEB."Código da transação"` (sem traços) == `VENDAS."Código da Transação"` (sem traços, `.replace('-','').upper()`)

> Validado: **28.268 de 28.271** registros RECEB cruzam com VENDAS (99,99% de match).

---

### 2.4 Sistema (`CAR_MM-AAAA.xlsx`)

- **Formato:** Excel `.xlsx`, aba `Contas_a_Receber1`
- **Linha 1:** Título "Contas a Receber" — ignorar
- **Linha 2:** Cabeçalho das colunas
- **Linha 3+:** Dados

**Colunas relevantes:**

| Coluna | Descrição | Uso na conciliação |
|---|---|---|
| `Documento` | Código interno (`NSU-TerminalID`) | Referência |
| `Tipo` | "Cartão débito", "Cartão crédito", "Crediario", etc. | Filtro |
| `Emissão` | Data da venda | Filtros e cruzamento |
| `NSU` | Número sequencial do PDV | **Chave p/ VENDAS** |
| `Autorização do TEF` | Código de autorização do terminal | **Chave p/ VENDAS** |
| `Valor` | Valor bruto da venda (R$) | Conciliação de valor |
| `Nome da bandeira do TEF` | MAESTRO, VISA, ELO DEBITO, etc. | Categorização |
| `Status` | "Aberto", "Quitado", "Substituído" | Filtro |
| `Vencimento` | Data prevista de recebimento | Fluxo de caixa |
| `Valor pago/recebido` | Valor já liquidado no sistema (R$) | Reconciliação interna |

**Tipos de registro por volume:**

| Tipo | Mar/2026 | Abr/2026 |
|---|---|---|
| Cartão débito | 14.247 | 13.492 |
| Cartão crédito | 9.175 | 8.783 |
| Crediário | 928 | 929 |
| Outros (boleto, dinheiro, etc.) | ~44 | ~66 |

**Chave de ligação com VENDAS:**  
`Sistema."NSU"` == `VENDAS."Código da Venda"` **E** `Sistema."Autorização do TEF"` == `VENDAS."Código de Autorização"`

---

### 2.5 Mapa de Relacionamento entre Arquivos

```
┌─────────────────────────────────────────────────────────────────┐
│                        SISTEMA (xlsx)                           │
│  NSU ──────────────────────────────────────► Código da Venda   │
│  Autorização do TEF ───────────────────────► Código Autorização │
│                              │                    │             │
│                              │         PAGBANK_VENDAS (csv)     │
│                              │              │                   │
│                              │    Código da Transação (UUID)    │
│                              │              │                   │
│                              │    ──────────▼──────────         │
│                              │    PAGBANK_RECEB (csv)           │
│                              │    Código da transação (UUID)    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Stack Tecnológica

### 3.1 Linguagem e Runtime

| Componente | Tecnologia | Versão mínima | Justificativa |
|---|---|---|---|
| Linguagem | Python | 3.9+ | Já instalado no ambiente; ecossistema maduro para dados |
| Interface Web | Streamlit | 1.32+ | Roda localmente no browser sem servidor; drag-and-drop nativo |
| Processamento de dados | pandas | 2.0+ | Leitura de CSV/XLSX, merge, groupby, filtros |
| Leitura de Excel | openpyxl | 3.1+ | Engine do pandas para `.xlsx` |
| Exportação Excel | XlsxWriter | 3.1+ | Geração de relatórios formatados com abas múltiplas |
| Gráficos | Plotly | 5.0+ | Gráficos interativos nativos no Streamlit |

### 3.2 Dependências completas (`requirements.txt`)

```
streamlit>=1.32.0
pandas>=2.0.0
openpyxl>=3.1.0
xlsxwriter>=3.1.0
plotly>=5.0.0
```

### 3.3 Estrutura de Arquivos do Sistema

```
conciliador/
├── app.py                  # Entrada principal — Streamlit
├── requirements.txt        # Dependências Python
├── iniciar.bat             # Launcher Windows (instala + executa)
│
├── core/
│   ├── __init__.py
│   ├── loader.py           # Leitura e normalização dos arquivos-fonte
│   ├── reconciler.py       # Motor de conciliação (cruzamentos)
│   ├── mdr.py              # Cálculo e verificação de taxas MDR
│   └── exporter.py         # Geração do relatório Excel
│
└── ui/
    ├── __init__.py
    ├── config_tab.py       # Aba: Upload de arquivos + taxas contratadas
    ├── conciliacao_tab.py  # Aba: Sistema ↔ PagBank
    ├── mdr_tab.py          # Aba: Verificação MDR
    ├── recebimentos_tab.py # Aba: Vendas vs Recebimentos
    └── relatorio_tab.py    # Aba: Exportar relatório
```

### 3.4 Launcher Windows (`iniciar.bat`)

```bat
@echo off
echo Verificando dependencias...
pip install -r requirements.txt --quiet
echo Iniciando Conciliador de Cartao...
streamlit run app.py --server.headless false
pause
```

---

## 4. Especificação Funcional por Módulo

### Módulo 1 — Configuração e Upload

**Entradas:**
- Upload de arquivos PagBank VENDAS (CSV, múltiplos meses)
- Upload de arquivos PagBank RECEB (CSV, múltiplos meses)
- Upload de arquivos Sistema (XLSX, múltiplos meses)
- Tabela de taxas MDR contratadas editável pelo usuário

**Tabela de taxas contratadas (valores padrão pré-carregados):**

| Bandeira | Modalidade | Parcelas | Taxa Contratada (%) |
|---|---|---|---|
| Mastercard | Débito | — | 0,82 |
| Visa | Débito | — | 0,82 |
| Elo | Débito | — | 0,82 |
| Mastercard | Crédito | à Vista | 2,65 |
| Visa | Crédito | à Vista | 2,65 |
| Elo | Crédito | à Vista | 2,65 |
| Amex | Crédito | à Vista | 4,00 |
| Mastercard | Crédito | 2–6x | — |
| Visa | Crédito | 2–6x | — |

**Saídas:**
- DataFrames normalizados em memória para os demais módulos
- Indicador visual de arquivos carregados com sucesso / com erro

---

### Módulo 2 — Conciliação Sistema ↔ PagBank VENDAS

**Lógica:**
1. Filtrar Sistema: apenas `Tipo` = "Cartão débito" ou "Cartão crédito"
2. Filtrar VENDAS: apenas `Forma de Pagamento` = "Débito" ou "Crédito" e `Status` = "Aprovada"
3. Fazer merge duplo:
   - `Sistema.NSU` == `VENDAS.Código da Venda`
   - `Sistema.Autorização do TEF` == `VENDAS.Código de Autorização`
4. Classificar cada registro:

| Resultado | Condição | Ação recomendada |
|---|---|---|
| ✅ Conciliado | Encontrado em ambos com valor igual | Nenhuma |
| ⚠️ Divergência de valor | Encontrado em ambos com valores diferentes | Investigar |
| 🔴 Só no Sistema | NSU/Auth não encontrado no PagBank | Verificar se foi processado |
| 🟡 Só no PagBank | Transação não registrada no sistema | Verificar lançamento |

**Métricas exibidas:**
- Total de registros por lado (Sistema / PagBank)
- % conciliado com sucesso
- Total em R$ de divergências de valor
- Total em R$ de registros só no Sistema (risco não-recebimento)
- Tabelas filtráveis por resultado com exportação

---

### Módulo 3 — Verificação de MDR

**Lógica:**
1. Para cada transação em VENDAS (Débito + Crédito):
   - Calcular `taxa_efetiva = Valor Taxa / Valor Bruto × 100`
   - Buscar `taxa_contratada` na tabela configurada pelo usuário (Bandeira + Forma + Parcela)
   - Calcular `diferença = taxa_efetiva − taxa_contratada`
   - Calcular `impacto_R$ = Valor Taxa − (Valor Bruto × taxa_contratada / 100)`
2. Marcar como `cobrado a mais` se `diferença > 0,01%` (tolerância)
3. Marcar como `cobrado a menos` se `diferença < -0,01%`

**Relatório MDR por agrupamento:**

| Bandeira | Modalidade | Parcela | N° transações | Taxa contratada | Taxa média efetiva | Diferença | Impacto R$ |
|---|---|---|---|---|---|---|---|
| Mastercard | Débito | — | 7.600 | 0,82% | 0,819% | -0,001% | -R$ 0,76 |
| Visa | Crédito | à Vista | 3.180 | 2,65% | 2,650% | 0,000% | R$ 0,00 |
| ... | | | | | | | |

**Alertas:**
- Transações individuais com taxa acima do contrato (lista detalhada)
- Total cobrado a mais no período (R$)
- Transações com taxa zerada (possível isenção ou erro)

---

### Módulo 4 — Vendas vs Recebimentos PagBank

**Lógica:**
1. Fazer merge: `VENDAS.Código da Transação` (UUID normalizado) → `RECEB.Código da transação`
2. Classificar:

| Resultado | Condição |
|---|---|
| ✅ Recebido | Aprovada no VENDAS e presente no RECEB |
| ⏳ Aguardando | Aprovada no VENDAS, ainda não em RECEB (crédito futuro) |
| ❌ Cancelada | Status "Cancelada" no VENDAS |
| ⚠️ Só no RECEB | Presente em RECEB sem venda correspondente |

**Métricas exibidas:**
- Total aprovado (R$) vs Total recebido (R$)
- Total pendente de crédito por data prevista de liberação
- Gráfico de barras: recebimentos por dia
- Gráfico de pizza: distribuição por bandeira

---

### Módulo 5 — Exportar Relatório

**Formato:** Excel `.xlsx` com múltiplas abas:

| Aba | Conteúdo |
|---|---|
| `Resumo` | Dashboard executivo: totais, alertas, % conciliado |
| `Conciliação` | Listagem completa com coluna de resultado (✅ ⚠️ 🔴 🟡) |
| `Divergências` | Apenas registros com problemas |
| `MDR_Resumo` | MDR agrupado por modalidade |
| `MDR_Detalhado` | MDR por transação (com desvios) |
| `Recebimentos` | Status de cada venda vs crédito na conta |
| `Pendentes` | Transações aprovadas ainda não creditadas |

---

## 5. Plano de Testes

### 5.1 Testes de Leitura e Normalização (`core/loader.py`)

| # | Teste | Critério de aprovação |
|---|---|---|
| T01 | Leitura de VENDAS CSV com encoding UTF-8-BOM | Sem erros de caracteres especiais; acentos corretos |
| T02 | Leitura de RECEB CSV ignorando as 3 primeiras linhas de cabeçalho | Primeira linha de dados correta na linha 4 do arquivo |
| T03 | Leitura de Sistema XLSX ignorando linha 1 (título) e usando linha 2 como cabeçalho | Colunas mapeadas corretamente |
| T04 | Normalização de UUID: remoção de traços e uppercase | `"00009E5D-CB2F..."` → `"00009E5DCB2F..."` |
| T05 | Conversão de valores monetários com vírgula decimal | `"85,22"` → `85.22` (float) |
| T06 | Upload de dois meses simultaneamente (mar + abr) | DataFrames concatenados sem duplicação de cabeçalho |
| T07 | Arquivo corrompido ou formato inválido | Mensagem de erro amigável; app não trava |
| T08 | Arquivo de mês fora do padrão de nome | Tratamento gracioso; data extraída do conteúdo |

---

### 5.2 Testes de Conciliação Sistema ↔ PagBank (`core/reconciler.py`)

| # | Teste | Critério de aprovação |
|---|---|---|
| T09 | Registro presente em ambos com valor igual | Classificado como ✅ Conciliado |
| T10 | Registro presente em ambos com valores diferentes em R$ 0,01 | Classificado como ⚠️ Divergência |
| T11 | Registro no Sistema sem correspondente no PagBank | Classificado como 🔴 Só no Sistema |
| T12 | Registro no PagBank sem correspondente no Sistema | Classificado como 🟡 Só no PagBank |
| T13 | NSU duplicado no Sistema (mesmo NSU, meses diferentes) | Cruzamento correto sem duplicação falsa |
| T14 | Transação cancelada no PagBank com registro no Sistema | Sinalizada como cancelada; não computada como pendente |
| T15 | 100% de match com arquivo de dados sintético controlado | Zero registros não conciliados no dataset de teste |
| T16 | Cruzamento de dois meses simultâneos | Sem mistura entre períodos; totais corretos por mês |
| T17 | Registro com Código de Autorização alfanumérico (ex: "1Q49S5") | Match correto (case-insensitive) |

---

### 5.3 Testes de Verificação MDR (`core/mdr.py`)

| # | Teste | Critério de aprovação |
|---|---|---|
| T18 | Transação com taxa exatamente igual ao contrato | `diferença = 0,000%`; sem alerta |
| T19 | Transação com taxa 0,01% acima do contrato | Sinalizada como "cobrado a mais"; impacto R$ calculado |
| T20 | Transação com taxa 0,01% abaixo do contrato | Sinalizada como "cobrado a menos" |
| T21 | Transação com taxa zerada (Valor Taxa = 0,00) | Sinalizada como anomalia; não gera divisão por zero |
| T22 | Modalidade não cadastrada na tabela de contratos | Exibida com taxa contratada = "—"; não trava o cálculo |
| T23 | Voucher e Pix excluídos do cálculo MDR | Não aparecem na verificação MDR |
| T24 | Soma de impactos R$ confere com somatório individual | Erro máximo de R$ 0,01 por arredondamento |
| T25 | Taxas padrão pré-configuradas correspondem às médias observadas | Valores padrão dentro de ±0,01% das médias de mar/2026 |

---

### 5.4 Testes de Vendas vs Recebimentos (`core/reconciler.py`)

| # | Teste | Critério de aprovação |
|---|---|---|
| T26 | UUID com traços (VENDAS) faz match com UUID sem traços (RECEB) | Match correto após normalização |
| T27 | Transação aprovada presente no RECEB | Classificada como ✅ Recebido |
| T28 | Transação aprovada ausente no RECEB | Classificada como ⏳ Aguardando |
| T29 | Transação cancelada | Classificada como ❌ Cancelada; não aparece em pendentes |
| T30 | RECEB sem VENDAS correspondente (3 casos conhecidos de mar/2026) | Classificada como ⚠️ Só no RECEB; não trava |
| T31 | Total recebido (RECEB) + pendente (sem RECEB) == total aprovado (VENDAS) | Equação financeira fechando com R$ 0,00 de diferença |
| T32 | Crédito parcelado: N parcelas em RECEB para 1 venda em VENDAS | Agrupamento correto; valor total de parcelas = valor bruto venda |

---

### 5.5 Testes de Interface e Exportação

| # | Teste | Critério de aprovação |
|---|---|---|
| T33 | App inicia sem arquivos carregados | Tela de boas-vindas com instruções; sem erros no console |
| T34 | Drag-and-drop de arquivo inválido (ex: `.jpg`) | Mensagem de erro clara; outros arquivos não afetados |
| T35 | Filtros de data na tabela de conciliação | Tabela atualiza corretamente; totais recalculados |
| T36 | Exportação do relatório Excel com todos os módulos | Arquivo `.xlsx` abre sem erros; 7 abas presentes |
| T37 | Relatório Excel com dados de dois meses | Cada mês identificável; sem mistura entre períodos |
| T38 | App rodando em Windows 10/11 sem privilégios de administrador | Instalação via `pip` e execução sem erros de permissão |
| T39 | Tabela MDR editável: alterar taxa e recalcular | Cálculos de diferença e impacto R$ atualizados em tempo real |
| T40 | Performance: carregar mar+abr (~53K linhas) e conciliar | Resultado exibido em menos de 30 segundos |

---

### 5.6 Dataset de Teste Sintético

Para garantir os testes T09–T17 e T26–T32 de forma determinística, será criado um arquivo de fixtures com:

```
tests/
├── fixtures/
│   ├── vendas_test.csv        # 20 transações controladas
│   ├── receb_test.csv         # 18 correspondentes (2 pendentes)
│   ├── sistema_test.xlsx      # 20 lançamentos (2 divergentes de valor)
│   └── expected_results.json  # Resultado esperado por transação
└── test_reconciler.py         # Testes automatizados (pytest)
```

---

## 6. Cronograma de Implementação

| Fase | Entregável | Estimativa |
|---|---|---|
| 1 | Estrutura de projeto + `loader.py` + testes T01–T08 | 1 dia |
| 2 | `reconciler.py` (conciliação principal) + testes T09–T17 | 1 dia |
| 3 | `mdr.py` (verificação MDR) + testes T18–T25 | 1 dia |
| 4 | Vendas vs Recebimentos + testes T26–T32 | 0,5 dia |
| 5 | Interface Streamlit completa (5 abas) + testes T33–T39 | 1,5 dia |
| 6 | `exporter.py` (relatório Excel) + teste T36–T37 | 0,5 dia |
| 7 | Teste de performance (T40) + ajustes finais + launcher `.bat` | 0,5 dia |
| **Total** | | **~6 dias úteis** |

---

## 7. Requisitos de Instalação no Computador do Cliente

```
Sistema Operacional : Windows 10 ou Windows 11
Python              : 3.9 ou superior (download: python.org)
Espaço em disco     : ~200 MB (Python + dependências)
RAM                 : 4 GB mínimo (8 GB recomendado para múltiplos meses)
Acesso à internet   : Necessário apenas na primeira execução (para baixar dependências)
```

**Passos de instalação:**
1. Instalar Python (marcar "Add Python to PATH" no instalador)
2. Copiar a pasta `conciliador/` para o computador
3. Dar duplo clique em `iniciar.bat`
4. Aguardar download automático das dependências (~1 min na primeira vez)
5. O browser abre automaticamente com o sistema

---

## 8. Decisões de Arquitetura

| Decisão | Alternativas consideradas | Justificativa |
|---|---|---|
| Streamlit para UI | Flask, Dash, planilha Excel VBA | Mais simples de instalar e usar; UI moderna sem HTML/JS |
| Processamento local | API/servidor na nuvem | Dados financeiros sensíveis; sem dependência de internet |
| pandas para dados | polars, dask | Mais familiar; suporte amplo; integração nativa com Streamlit |
| XlsxWriter para export | openpyxl write, csv | Melhor suporte a formatação, cores e múltiplas abas |
| Chave dupla de conciliação (NSU + Auth) | Apenas NSU, apenas Auth | Reduz falsos positivos; ambos os campos são únicos por transação |
| Tolerância MDR de ±0,01% | Zero tolerância | Evita alertas por arredondamentos de centavos |

---

*Documento gerado em 12/05/2026 | Revisão: v1.0*
