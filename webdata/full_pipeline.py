import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import ollama
import os
import re

def sanitizar_nome_arquivo(nome):
    nome = re.sub(r'[\\/*?:"<>|]', "", nome)
    nome = nome.replace(' ', '_')
    return nome[:150]

def extrair_texto_relevante(soup):
    tags_de_texto = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'td', 'article', 'span', 'pre']
    
    textos_encontrados = []
    
    for tag in soup.find_all(tags_de_texto):
        texto = tag.get_text(strip=True)
        if texto:
            textos_encontrados.append(texto)
            
    return '\n\n'.join(textos_encontrados)

def rastrear_sites(urls_iniciais, profundidade_maxima):
    diretorio_saida = 'sites_baixados'
    if not os.path.exists(diretorio_saida):
        os.makedirs(diretorio_saida)
        print(f"Diretório '{diretorio_saida}' criado.")

    urls_visitadas = set()
    urls_para_visitar_nesta_profundidade = list(urls_iniciais)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for profundidade_atual in range(profundidade_maxima + 1):
        if not urls_para_visitar_nesta_profundidade:
            print("Não há mais URLs únicas para visitar. Finalizando.")
            break

        print(f"\n--- PROFUNDIDADE: {profundidade_atual} ---")
        print(f"URLs a serem processadas nesta profundidade: {len(urls_para_visitar_nesta_profundidade)}")

        urls_para_proxima_profundidade = set()
    
        for url in urls_para_visitar_nesta_profundidade:
            if url in urls_visitadas:
                continue

            print(f"Acessando: {url}")
            urls_visitadas.add(url)

            try:
                pagina = requests.get(url, headers=headers, timeout=10)
                pagina.raise_for_status()
                
                if 'text/html' not in pagina.headers.get('Content-Type', ''):
                    print("  -> Ignorado: Conteúdo não é HTML.")
                    continue

                dados_pagina = BeautifulSoup(pagina.text, 'html.parser')
                texto_extraido = extrair_texto_relevante(dados_pagina)
                
                if not texto_extraido:
                    print("  -> Ignorado: Nenhum texto relevante encontrado.")
                    continue

                relacao = ''

                titulo_pagina = dados_pagina.title.string if dados_pagina.title else ''
                if titulo_pagina:
                    nome_base_arquivo = sanitizar_nome_arquivo(titulo_pagina)
                else:
                    caminho_url = urlparse(url).path
                    nome_base_arquivo = sanitizar_nome_arquivo(os.path.basename(caminho_url) or url.replace('https://', '').replace('http://', ''))
                
                if not nome_base_arquivo:
                    nome_base_arquivo = f"pagina_{len(urls_visitadas)}"

                caminho_arquivo = os.path.join(diretorio_saida, f"{nome_base_arquivo}.txt")
                with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                    f.write(texto_extraido)
                print(f"  -> Texto extraído salvo em: {caminho_arquivo}")

                if profundidade_atual < profundidade_maxima:
                    tags_de_link = dados_pagina.find_all('a', href=True)
                    for tag in tags_de_link:
                        link = tag['href']
                        link_absoluto = urljoin(url, link)
                        
                        parsed_link = urlparse(link_absoluto)
                        if parsed_link.scheme in ['http', 'https']:
                            urls_para_proxima_profundidade.add(link_absoluto)

            except requests.exceptions.RequestException as e:
                print(f"  -> ERRO: Não foi possível baixar a página. {e}")
            except Exception as e:
                print(f"  -> ERRO: Ocorreu um erro inesperado ao processar a página. {e}")
        
        urls_para_visitar_nesta_profundidade = list(urls_para_proxima_profundidade)

    print("\n--- Rastreamento Concluído ---")
    print(f"Total de páginas únicas visitadas: {len(urls_visitadas)}")


if __name__ == "__main__":
    urls_iniciais = [
        'https://valedosinconfidentes.com.br/',
        'https://pt.wikipedia.org/wiki/Cidade_inteligente',
        'https://www.gov.br/cidades/pt-br'
    ]

    profundidade_rastreio = 1

    rastrear_sites(urls_iniciais, profundidade_rastreio)
