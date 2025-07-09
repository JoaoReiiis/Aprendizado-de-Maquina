import scrapy
from scrapy.loader import ItemLoader
from ..items import MobilidadeItem
from urllib.parse import urlparse
import trafilatura
import spacy

class FocoMobilidadeSpider(scrapy.Spider):
    name = "mob"
    
    start_urls = [
        "https://mobilidade.estadao.com.br/",
        "https://www.mobilize.org.br/noticias/",
        "https://valedosinconfidentes.com.br/"
    ]
        
    KEYWORDS = [
        "mobilidade", "mobilidade-urbana", "cidade-inteligente", "smart-city",
        "transporte", "transporte-publico", "veiculo-eletrico", "ev", "vlt",
        "metro", "brt", "bicicleta", "ciclovia", "urbanismo", "sustentabilidade",
        "iot", "big-data", "ia", "inteligencia-artificial", "5g", "blockchain",
        "veiculos-autonomos", "veiculos-conectados", "maas", "eVTOL",
        "semaforos-inteligentes", "estacao-de-recarga", "v2g",
        "cidade-15-minutos", "mobilidade-compartilhada", "logistica-urbana", "last-mile",
        "sistemas-de-transporte-inteligente", "sti", "transporte-ativo",
    ]

    NEGATIVE_KEYWORDS = [
        'login', 'cadastro', 'assine', 'contato', 'sobre-nos', 
        'politica-de-privacidade', 'termos-de-uso'
    ]
    
    def __init__(self, *args, **kwargs):
        super(FocoMobilidadeSpider, self).__init__(*args, **kwargs)
        self.max_depth = 10
        self.nlp = None
        
        try:
            self.nlp = spacy.load("pt_core_news_lg", disable=["parser", "lemmatizer"])
        except OSError:
            raise scrapy.exceptions.CloseSpider("Modelo do spaCy não encontrado.")


    def parse(self, response):
        extracted_content = trafilatura.extract(response.body, include_comments=False, include_tables=True)
        
        if extracted_content and self.is_article_page(response, extracted_content):
            yield self.extrair_dados_da_pagina(response, extracted_content)

        current_depth = response.meta.get('depth', 0)
        if current_depth >= self.max_depth:
            self.logger.info(f"Profundidade máxima ({self.max_depth}) atingida em: {response.url}")
            return

        for link in response.css('a::attr(href)').getall():
            absolute_link = response.urljoin(link)
            
            if self.deve_seguir_o_link(absolute_link):
                yield scrapy.Request(
                    absolute_link,
                    callback=self.parse,
                    meta={'depth': current_depth + 1}
                )

    def is_article_page(self, response, content: str) -> bool:

        parsed_url = urlparse(response.url)
        if not parsed_url.path or parsed_url.path == '/':
            self.logger.debug(f"Página pulada (URL é uma página raiz): {response.url}")
            return False
        
        if len(content) < 512:
            self.logger.debug(f"Página pulada (conteúdo curto): {response.url}")
            return False
        
        if content.count('...') > 5:
             self.logger.debug(f"Página pulada (muitos resumos '...'): {response.url}")
             return False

        menu_like_lines = 0
        total_lines = 0

        for line in content.splitlines():
            stripped_line = line.strip()
            if not stripped_line:
                continue
            total_lines += 1
            words = stripped_line.split()
            if 1 <= len(words) <= 7 and stripped_line.isupper():
                menu_like_lines += 1

        if total_lines > 10 and (menu_like_lines / total_lines) > 0.2:
            self.logger.debug(f"Página pulada (parece ser um menu/índice): {response.url}")
            return False
        
        doc = self.nlp(content)
        
        relevant_entities = 0
        relevant_labels = {'ORG', 'LOC', 'GPE', 'PRODUCT'}

        for ent in doc.ents:
            if ent.label_ in relevant_labels:
                relevant_entities += 1

        if relevant_entities < 10:
            self.logger.debug(f"Página pulada (poucas entidades: {relevant_entities}): {response.url}")
            return False

        self.logger.info(f"Artigo válido encontrado (Entidades: {relevant_entities}): {response.url}")
        return True

    def is_relevant(self, text_content: str) -> bool:
        text_lower = text_content.lower()
        count = sum(1 for keyword in self.KEYWORDS if keyword in text_lower)
        return count >= 3

    def extrair_dados_da_pagina(self, response, extracted_content: str):
        loader = ItemLoader(item=MobilidadeItem(), response=response)
        
        metadata = trafilatura.extract_metadata(response.body)
        
        loader.add_value('url_fonte', response.url)
        loader.add_value('site_de_origem', urlparse(response.url).netloc)
        loader.add_value('titulo', metadata.title if metadata else '')
        loader.add_css('titulo', 'h1::text')
        loader.add_value('conteudo_texto', extracted_content)
        loader.add_value('data_publicacao', metadata.date if metadata else '')
        
        return loader.load_item()

    def deve_seguir_o_link(self, url: str) -> bool:
        if not url.startswith(('http', 'https')):
            return False
        
        url_lower = url.lower()
        
        if any(neg_keyword in url_lower for neg_keyword in self.NEGATIVE_KEYWORDS):
            return False
            
        if any(keyword in url_lower for keyword in self.KEYWORDS):
            return True
        
        return False
