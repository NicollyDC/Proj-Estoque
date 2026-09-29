# Proj-Estoque

Sistema de controle de estoque para desktop, feito em Python. Os itens entram no estoque a partir da nota fiscal (XML) e as saídas ficam registradas com responsável, data e horário.

## Funcionalidades

- **Entrada por nota fiscal:** importação dos itens lendo direto o XML da nota, com busca pelo número da nota.
- **Vínculo de produtos:** o item da nota pode ser ligado a um cadastro já existente, já que nome e código do fornecedor nem sempre batem com os do sistema.
- **Edição de quantidades:** permite ajustar a quantidade quando a unidade de medida do sistema é diferente da do fornecedor.
- **Registro de saídas:** guarda quem fez a saída, a data e o horário.
- **Classificação das saídas:** perda, uso e consumo ou venda. Cada produto também pode ser marcado como de venda ou de uso e consumo.
- **Estoque mínimo:** alerta quando o item chega ao mínimo, com valor editável.
- **Faturamento:** registra quando a nota de entrada foi faturada.
- **Edição e exclusão:** produtos e itens existentes podem ser alterados ou removidos.
- **Relatórios:** perdas e gastos por semana, mês e ano, com exportação para Excel e texto/PDF.

## Estrutura do projeto

`Estruraa das pastas: 

Proj-Estoque/
│
├── estoque.db                 # Banco SQLite
├── requirements.txt
│
├── estoque/
│   ├── main.py                # Inicializa o sistema
│   ├── database.py            # Conexão + SQL
│   ├── utils.py               # Funções auxiliares
│   ├── app_state.py           # Estado da aplicação
│   ├── xml_import.py          # Leitura da NF-e
│   │
│   └── ui/
│       ├── components.py      # TreeView, Form, Botões
│       ├── notas.py           # Tela de notas
│       ├── notas_detalhes.py  # Itens da nota
│       ├── produtos.py        # Cadastro de produtos
│       ├── saidas.py          # Baixas de estoque
│       └── relatorios.py      # Relatórios
│
└── xml/                       # XMLs importados (opcional)



## Responsabilidade de cada arquivo

**main.py**

* Ponto de entrada da aplicação. Cria a janela principal, Notebook (abas), estilo e controla o fechamento do sistema.

**database.py**

* Único arquivo que conversa diretamente com o SQLite. Guarda q() para consultas e run() para INSERT/UPDATE/DELETE.

**utils.py**

* Regras reutilizáveis: datas, conversão numérica, formatação, cálculo de estoque e mapa de produtos.

**xml_import.py**

* Apenas interpreta o XML da NF-e. Ele não grava no banco; devolve nota e itens para a interface decidir o que fazer.

**components.py**

* Biblioteca de componentes da interface. Evita repetir código de formulários, tabelas e seleção.

## Como executar

1. Instale o [Python](https://www.python.org/downloads/).
2. Clone o repositório:
   ```bash
   git clone https://github.com/NicollyDC/Proj-Estoque.git
   cd Proj-Estoque
   ```
3. Instale as dependências do projeto:
   ```bash
   pip install -r requirements.txt
   ```
4. Inicie a aplicação:
   ```bash
   python estoque/main.py
   ```

## Banco de dados

O arquivo do banco (`estoque.db`) **não é versionado**, porque está no `.gitignore` e pode conter dados reais do estoque. Ao rodar o projeto pela primeira vez, o banco precisa ser criado pela própria aplicação.

## Autora

Desenvolvido por [NicollyDC](https://github.com/NicollyDC).
