import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

#url_base = 'https://pt.wikipedia.org/wiki/Cidade_inteligente'
url_base = 'https://valedosinconfidentes.com.br/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    pagina = requests.get(url_base, headers=headers)
    pagina.raise_for_status()

    dados_pagina = BeautifulSoup(pagina.text, 'html.parser')

    html_formatado = dados_pagina.prettify()

    with open('teste.txt', 'w', encoding='utf-8') as f:
        f.write(html_formatado)
    
    tags_com_link = set(dados_pagina.find_all('a', href=True))
    links = set()

    for tag in tags_com_link:
        link = tag['href']
        if link and link.startswith(('http://', 'https://')):
            links.add(link)

    for link in links:
        print(link)

except requests.exceptions.RequestException as e:
    print(f"Ocorreu um erro: {e}")