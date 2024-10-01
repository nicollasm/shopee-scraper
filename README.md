# Shopee Scraper Otimizado

Um web scraper em Python para extrair vendas, preço, estoque disponível e mais de um vendedor dado no Brasil.

## Requisitos

O projeto foi criado em Python 3 e requer as seguintes bibliotecas:

- requests
- tkinter
- re
- datetime
- threading

Você pode instalar facilmente essas bibliotecas usando o seguinte comando:

```bash
$ pip install -r requirements.txt
```

## Como Funciona

Este script roda com base na API pública da Shopee. A Shopee gera uma página dinâmica que mostra produtos e suas informações chamando um arquivo JSON. Já que é uma API e é pública, é mais fácil apenas chamar o arquivo JSON e extrair os dados.

## Como Usar

1. Você tem duas opções para iniciar o scraping: 
    - Encontrar o ID do vendedor, que está presente no link do produto.
    - Usar o próprio link do produto.

    Exemplo: \`https://shopee.com.br/Camisetas-Bandas-Rock-RHCP-Red-Hot-Chili-Peppers-100-Algodao!!-i.409068735.3983196792\`
  
    - 409068735 é o ID do vendedor.
    - 3983196792 é o ID do produto.

2. Execute o script em Python:

```bash
$ python main_final_version.py
```

3. Insira o ID do vendedor ou o link do produto na interface gráfica.

4. Clique em "Buscar Dados" para carregar a quantidade de produtos.

5. Clique em "Iniciar Scraping" para começar o scraping.

## Créditos

Este projeto é uma otimização do [Shopee Scraper original](https://github.com/paulodarosa/shopee-scraper) criado por Paulo da Rosa.
