import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from collections import deque
import time
import random
import re
import os

# --- MÓDULO DE EXTRAÇÃO E SALVAMENTO ---

def sanitize_filename(title):
    """
    Limpa uma string para que ela possa ser usada como um nome de arquivo válido.
    Remove caracteres inválidos e limita o comprimento.
    """
    if not title:
        return "sem_titulo"
    # Remove caracteres inválidos em nomes de arquivo do Windows/Linux/Mac
    sanitized = re.sub(r'[\\/*?:"<>|]', "", title)
    sanitized = sanitized.strip().replace(' ', '_')
    # Limita o nome do arquivo para evitar problemas de sistema de arquivos
    return sanitized[:100]

def extract_and_save_content(soup, output_dir="scraped_pages"):
    """
    Extrai texto das tags mais comuns (p, h's, li, table) de um objeto Soup
    e salva em um arquivo .txt nomeado com o título da página.
    """
    # 1. Obter e limpar o título para usar como nome de arquivo
    page_title = soup.title.string if soup.title else 'pagina_sem_titulo'
    filename = sanitize_filename(page_title) + ".txt"

    # Cria o diretório de saída se ele não existir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    filepath = os.path.join(output_dir, filename)

    # 2. Definir as tags de interesse para extração de texto
    # Usando expressão regular para todos os 'h' (h1 a h6)
    tags_de_texto = ['p', 'li', 'td', 'th', re.compile('^h[1-6]$')]
    
    # 3. Encontrar todos os elementos e extrair o texto
    elementos = soup.find_all(tags_de_texto)
    
    if not elementos:
        print(f"  -> Nenhuma tag de texto encontrada em '{page_title}'. Arquivo não será criado.")
        return

    # Usamos strip=True para remover espaços extras e \n\n como separador
    conteudo_texto = '\n\n'.join([elem.get_text(strip=True) for elem in elementos])
    
    # 4. Salvar o conteúdo no arquivo .txt
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(conteudo_texto)
        print(f"  -> Conteúdo salvo em: {filepath}")
    except OSError as e:
        print(f"  -> Erro ao salvar o arquivo {filepath}: {e}")


# --- CLASSE DO CRAWLER MODIFICADA ---

class SimpleCrawler:
    def __init__(self, seed_url, max_pages=50):
        self.seed = seed_url
        self.domain = urlparse(seed_url).netloc
        self.max_pages = max_pages
        self.visited = set()
        self.queue = deque([seed_url])
        # ESSENCIAL: Adicionar um User-Agent para parecer um navegador
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.output_dir = "scraped_" + self.domain.replace('.', '_')


    def crawl(self):
        """
        Método principal que navega pelas páginas.
        """
        while self.queue and len(self.visited) < self.max_pages:
            url = self.queue.popleft()
            if url in self.visited:
                continue

            print(f"[*] Visitando [{len(self.visited)+1}/{self.max_pages}]: {url}")
            
            try:
                # Usando o header definido no __init__
                resp = requests.get(url, headers=self.headers, timeout=10)
                resp.raise_for_status()
                # Garante que o conteúdo seja decodificado corretamente
                resp.encoding = resp.apparent_encoding
            except requests.RequestException as e:
                print(f"  -> Falha ao buscar {url}: {e}")
                continue

            self.visited.add(url)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # --- INTEGRAÇÃO: ACIONA O MÓDULO DE EXTRAÇÃO ---
            extract_and_save_content(soup, self.output_dir)
            
            self.find_and_queue_links(soup, url)

            # Pausa para não sobrecarregar o servidor
            time.sleep(random.uniform(1.0, 3.0))

    def find_and_queue_links(self, soup, current_url):
        """
        Encontra novos links na página e os adiciona à fila.
        """
        for link_tag in soup.find_all('a', href=True):
            link = urljoin(current_url, link_tag['href'])
            parsed = urlparse(link)
            
            # Manter apenas links http/https, do mesmo domínio e sem fragmentos (#)
            if parsed.scheme in ('http', 'https') and parsed.netloc == self.domain:
                clean_link = parsed._replace(fragment='').geturl()
                if clean_link not in self.visited and clean_link not in self.queue:
                    self.queue.append(clean_link)


if __name__ == '__main__':
    # URL inicial para o crawler
    start_url = 'https://valedosinconfidentes.com.br/'
    
    # Cria uma instância do crawler com um limite de 20 páginas
    crawler = SimpleCrawler(start_url, max_pages=20)
    
    # Inicia o processo
    crawler.crawl()
    
    print("\n[+] Crawling finalizado!")