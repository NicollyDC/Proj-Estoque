# Controle de Estoque

Sistema desktop para controle de estoque desenvolvido em Python, com interface gráfica Tkinter e banco de dados SQLite.

O sistema possui módulos independentes para diferentes estabelecimentos, permitindo que cada um mantenha seus próprios produtos, notas, movimentações e banco de dados.

## 🏢 Estabelecimentos

Atualmente o sistema possui:

* **Hotel**
* **Restaurante**

Cada estabelecimento possui seu próprio banco de dados SQLite, mantendo os dados completamente separados.

## 🛠️ Tecnologias

* Python
* Tkinter / ttk
* SQLite
* XML
* Git / GitHub
* PyInstaller

## 📁 Estrutura do projeto

```text
Proj-Estoque/
│
├── main.py
│
├── dados/
│   ├── hotel/
│   │   └── database.py
│   │
│   └── restaurante/
│       └── database.py
│
├── estoque_hotel/
│   ├── main.py
│   ├── app_state.py
│   ├── utils.py
│   ├── xml_import.py
│   ├── consulta_nfe.py
│   └── ui/
│       ├── components.py
│       ├── notas.py
│       ├── notas_detalhes.py
│       ├── produtos.py
│       ├── saidas.py
│       ├── saida_detalhes.py
│       └── relatorios.py
│
├── estoque_restaurante/
│   ├── main.py
│   ├── app_state.py
│   ├── utils.py
│   ├── xml_import.py
│   └── ui/
│       ├── components.py
│       ├── notas.py
│       ├── notas_detalhes.py
│       ├── produtos.py
│       ├── saidas.py
│       ├── saida_detalhes.py
│       └── relatorios.py
│
├── .gitignore
└── ControleEstoque.spec
```

## 📦 Funcionalidades

### Produtos

* Cadastro de produtos
* Código interno
* Nome
* Unidade
* Estoque mínimo
* Finalidade
* Ativação/inativação de produtos

### Notas fiscais

* Cadastro e importação de notas fiscais
* Importação de itens através de XML
* Armazenamento da chave de acesso da NF-e
* Vinculação de produtos do fornecedor aos produtos internos
* Controle de fator de conversão

O XML da NF-e é utilizado durante a importação, mas não é armazenado permanentemente no banco de dados.

### Controle de estoque

O estoque é calculado a partir das entradas e saídas registradas no sistema.

As movimentações consideram:

* Quantidade recebida
* Fator de conversão
* Quantidade em estoque
* Valor total
* Valor unitário
* Saídas realizadas

### Custo médio

O sistema utiliza custo médio ponderado para determinar o valor unitário das saídas.

O custo utilizado em uma saída é registrado junto à movimentação, preservando o histórico mesmo quando o custo médio do estoque muda posteriormente.

### Saídas

Permite registrar movimentações de:

* Perda
* Uso e consumo
* Venda

O sistema impede a realização de uma saída superior ao estoque disponível.

### Relatórios

Possui relatórios de movimentação e estoque com filtros por:

* Semana
* Mês
* Ano
* Tipo de movimentação
* Produto

## 🧾 NF-e

A importação de NF-e utiliza a chave de acesso de 44 dígitos para consultar os dados da nota.

Cada estabelecimento possui validação própria do destinatário, evitando que notas destinadas a outro estabelecimento sejam importadas para o banco incorreto.

### CNPJs dos estabelecimentos

**Hotel**

```text
00.810.115/0001-41
```

**Restaurante**

```text
62.719.684/0001-33
```

Os dados dos dois estabelecimentos são mantidos separados.

## 🖥️ Executável

O projeto pode ser empacotado como aplicativo Windows utilizando PyInstaller.

Os arquivos gerados pelo PyInstaller, como `build/` e `dist/`, não são versionados no Git.

Para gerar o executável:

```powershell
python -m PyInstaller --noconfirm --clean --windowed --name ControleEstoque --add-data "dados;dados" main.py
```

O executável será gerado em:

```text
dist/ControleEstoque/
```

## 🚧 Próximos passos

O projeto está sendo desenvolvido de forma incremental.

Entre os próximos recursos planejados estão:

* Sistema de login e controle de acesso
* Registro de operações
* Sessões de usuário
* Sincronização com banco de dados em nuvem
* Controle de alterações
* Integração mais completa com serviços fiscais
* Melhorias na distribuição do aplicativo

## 👩‍💻 Desenvolvimento

Projeto desenvolvido por **Nicolly Dias Cruz**.

GitHub:

**NicollyDC/Proj-Estoque**
