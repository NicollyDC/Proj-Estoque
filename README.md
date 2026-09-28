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

```
estoque/
├── main.py            # ponto de entrada da aplicação
├── app_state.py       # estado da aplicação
├── database.py        # acesso ao banco de dados
├── utils.py           # funções auxiliares
├── xml_import.py      # leitura e importação do XML da nota fiscal
└── ui/
    ├── components.py      # componentes reutilizáveis da interface
    ├── notas.py           # tela de notas
    ├── notas_detalhes.py  # detalhes de uma nota
    ├── produtos.py        # tela de produtos
    ├── saidas.py          # tela de saídas
    └── relatorios.py      # tela de relatórios
```

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
