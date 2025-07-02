# spiders/foco_mobilidade_spider.py

import scrapy
from scrapy.loader import ItemLoader
from ..items import MobilidadeItem
from urllib.parse import urlparse

class FocoMobilidadeSpider(scrapy.Spider):
    """
    Esta spider representa a melhor abordagem para um crawler focado:
    - Extrai conteúdo de forma semântica e robusta.
    - Propaga-se de forma inteligente e temática, seguindo links externos relevantes.
    - Opera dentro de limites controlados para garantir eficiência e foco.
    """
    name = "foco_mobilidade"
    
    # URLs iniciais: Pontos de partida de alta qualidade e confiança.
    start_urls = [
        "https://mobilidade.estadao.com.br/",
        "https://www.mobilize.org.br/noticias/",
        "https://thecityfixbrasil.com/",
        "https://viatrolebus.com.br/category/mobilidade-urbana/"
    ]
    
    # Domínios base para ajudar a identificar links "internos".
    allowed_domains = [urlparse(url).netloc for url in start_urls]

    # PALAVRAS-CHAVE TEMÁTICAS: O cérebro do nosso filtro de relevância.
    # Usadas para decidir se um link externo vale a pena ser seguido.
    KEYWORDS = [
        'mobilidade', 'urbana', 'cidade', 'inteligente', 'smart-city', 'transporte',
        'publico', 'veiculo', 'eletrico', 'ev', 'vlt', 'metro', 'brt', 'bicicleta',
        'ciclovia', 'urbanismo', 'sustentabilidade', 'logistica', 'pedestre'
    ]

    def __init__(self, *args, **kwargs):
        super(FocoMobilidadeSpider, self).__init__(*args, **kwargs)
        # Limite de profundidade para o crawler não se perder.
        self.max_depth = 5 
        # Conjunto para armazenar URLs já visitadas e evitar trabalho duplicado.
        self.visited_urls = set()

    def parse(self, response):
        """
        Método principal que é chamado para cada página visitada.
        """
        current_url = response.url
        if current_url in self.visited_urls:
            return
        self.visited_urls.add(current_url)

        # --- PILAR 1: EXTRAÇÃO DE CONTEÚDO SEMÂNTICO ---
        self.extrair_dados_da_pagina(response)

        # --- PILAR 2: PROPAGAÇÃO TEMÁTICA INTELIGENTE ---
        current_depth = response.meta.get('depth', 0)
        if current_depth >= self.max_depth:
            self.logger.info(f"Profundidade máxima ({self.max_depth}) atingida em: {current_url}")
            return

        # Itera sobre todos os elementos de link '<a>' da página.
        for link_element in response.css('a'):
            link_href = link_element.attrib.get('href')
            anchor_text = link_element.css('::text').get('').lower()
            
            if not link_href:
                continue

            absolute_link = response.urljoin(link_href)

            # Verifica se o link é relevante antes de segui-lo.
            if self.deve_seguir_o_link(absolute_link, anchor_text):
                yield scrapy.Request(
                    absolute_link,
                    callback=self.parse,
                    meta={'depth': current_depth + 1}
                )

    def extrair_dados_da_pagina(self, response):
        """
        Extrai informações da página usando a abordagem de "bloco de conteúdo".
        """
        loader = ItemLoader(item=MobilidadeItem(), response=response)
        
        loader.add_value('url_fonte', response.url)
        loader.add_value('site_de_origem', urlparse(response.url).netloc)
        loader.add_value('profundidade_crawl', response.meta.get('depth', 0))

        # Lista de seletores para encontrar o contêiner principal do artigo.
        content_selectors = ['article', 'main', '.post-content', '.entry-content', '.article-body', '[role="main"]']
        content_block = None
        for selector in content_selectors:
            if response.css(selector):
                content_block = response.css(selector)
                break
        
        if content_block:
            # Se encontrou um bloco, extrai dados de dentro dele.
            loader.add_value('titulo', content_block.css('h1::text').get())
            loader.add_value('conteudo_texto', content_block.css('h2, h3, h4, p, li, blockquote').getall())
            loader.add_value('autor', content_block.css('.author::text, [rel="author"]::text').get())
            loader.add_value('data_publicacao', content_block.css('time::attr(datetime)').get())
            loader.add_value('tags_ou_categorias', content_block.css('[rel="category tag"]::text, .tags a::text').getall())
        else:
            # Fallback se nenhum bloco for encontrado.
            self.logger.warning(f"Nenhum bloco de conteúdo principal encontrado em {response.url}. Usando fallback.")
            loader.add_css('titulo', 'h1::text')
            loader.add_css('conteudo_texto', 'p::text')

        yield loader.load_item()

    def deve_seguir_o_link(self, url: str, anchor_text: str) -> bool:
        """
        Lógica de decisão para seguir um link. Retorna True se o link for relevante.
        """
        if not url.startswith(('http', 'https')) or '#' in url:
            return False

        # Critério 1: Seguir se for um link interno (do mesmo domínio inicial).
        if urlparse(url).netloc in self.allowed_domains:
            return True

        # Critério 2: Para links externos, verificar se a URL ou o texto do link contém palavras-chave.
        # Isso aumenta drasticamente a chance de o link ser temático.
        text_to_check = (url + ' ' + anchor_text).lower()
        if any(keyword in text_to_check for keyword in self.KEYWORDS):
            self.logger.info(f"Link externo temático encontrado: {url} (texto: '{anchor_text[:50]}...')")
            return True
        
        return False