import scrapy
from scrapy.loader import ItemLoader
from ..items import MobilidadeItem
from urllib.parse import urlparse

class MobPropagadorSpider(scrapy.Spider):
    name = "mob_propagador"
    
    # URLs iniciais de alta qualidade sobre o tema
    start_urls = [
        "https://mobilidade.estadao.com.br/",
        "https://www.mobilize.org.br/noticias/",
        "https://thecityfixbrasil.com/"
    ]
    
    # Domínios originais para referência
    allowed_domains = [urlparse(url).netloc for url in start_urls]

    KEYWORDS = [
    "mobilidade", "mobilidade-urbana", "cidade-inteligente", "smart-city",
    "transporte", "transporte-publico", "veiculo-eletrico", "ev", "vlt",
    "metro", "brt", "bicicleta", "ciclovia", "urbanismo", "sustentabilidade"

    # Tecnologias Habilitadoras  
    "iot", "big-data", "ia", "inteligencia-artificial", "5g", "blockchain",  
    "geolocalizacao", "sensoristica", "rfid", "telemetria", "conectividade",  
    "cloud-computing", "edge-computing", "digital-twin", "anpr", "visao-computacional",  
    "modelagem-preditiva", "api-integracao", "dados-abertos", "realidade-aumentada",  
      
    # Modalidades de Transporte Inovadoras  
    "veiculos-autonomos", "veiculos-conectados", "veiculo-eletrico", "ev",  
    "vlt", "metro", "brt", "bicicleta-compartilhada", "patinete-eletrico",  
    "microtransito", "carsharing", "motosharing", "ride-hailing", "mobility-as-a-service",  
    "maas", "transporte-aereo-urbano", "drones-entrega", "hyperloop", "eVTOL",  
    "onibus-autonomo", "cargo-bike", "roboshuttles", "trem-regional", "monotrilho",  
    "balsa-eletrica", "starship-technologies",  
      
    # Infraestrutura Inteligente  
    "semaforos-inteligentes", "estacao-de-recarga", "recarga-rapida", "v2g",  
    "zona-de-baixas-emissoes", "calcada-inteligente", "parquimetro-digital",  
    "corredores-onibus", "hubs-multimodais", "pavimento-inteligente",  
    "iluminacao-adaptativa", "estacionamento-inteligente", "faixa-dedicada",  
    "priorizacao-semafórica", "ciclorrotas", "ciclovias-dinamicas",  
    "infraestrutura-v2x", "estacoes-multimodais", "recarga-inductiva",  
      
    # Modelos de Gestão e Serviços  
    "tarifacao-dinamica", "pagamento-por-aproximacao", "bilhetes-digitais",  
    "planejamento-de-viagens-integrado", "reserva-em-tempo-real", "gestao-dinamica-de-frotas",  
    "controle-operacional-remoto", "otimizacao-de-rotas", "roterizacao-inteligente",  
    "gestao-de-congestionamento", "pedagio-eletronico", "cobranca-de-congestionamento",  
    "fiscalizacao-automatizada", "centros-de-controle", "hipervisao",  
    "sistemas-de-transporte-inteligente", "sti", "monitoramento-de-vagas",  
    "pool-de-veiculos",  
      
    # Conceitos Estratégicos  
    "cidade-15-minutos", "mobilidade-compartilhada", "mobilidade-como-servico",  
    "zero-emissoes", "descarbonizacao", "logistica-urbana-sustentavel",  
    "last-mile", "acessibilidade-universal", "equidade-mobilidade",  
    "transporte-ativo", "mobilidade-inclusiva", "neutralidade-carbono",  
    "ods-11", "transicao-energetica", "economia-circular-transporte",  
    "reducao-congestionamento", "seguranca-viaria", "visao-zero",  
    "eficiencia-energetica", "pegada-carbono-transporte", "mobilidade-corporativa",  
    "fretamento-inteligente", "transporte-sob-demanda", "shared-mobility",  
    "logistica-urbana-colaborativa",  
      
    # Indicadores e Métricas  
    "tempo-real-transporte", "previsao-trafego", "simulacao-urbana",  
    "indicadores-desempenho-mobilidade", "taxa-ocupacao-veicular",  
    "reducao-emissoes-transporte", "avaliacao-impacto-mobilidade",  
    "participacao-cidada-mobilidade"   
    ]

    def __init__(self, *args, **kwargs):
        super(MobPropagadorSpider, self).__init__(*args, **kwargs)
        self.max_depth = 5 
        self.visited_urls = set()

    def parse(self, response):
        """
        Esta função principal faz duas coisas:
        1. Extrai informações da página atual.
        2. Encontra novos links, filtra-os por relevância e agenda novos requests.
        """

        current_url = response.url
        
        if current_url in self.visited_urls:
            return
        self.visited_urls.add(current_url)

        site_origem = urlparse(current_url).netloc
        
        loader = ItemLoader(item=MobilidadeItem(), response=response)
        loader.add_value('url_fonte', current_url)
        loader.add_value('site_de_origem', site_origem)
        loader.add_value('profundidade_crawl', response.meta.get('depth', 0))

        loader.add_css('titulo', 'h1::text')
        # Tenta extrair o conteúdo (parágrafos dentro de 'article' ou 'main')
        loader.add_css('conteudo_texto', 'article p::text, main p::text')
        # Outros campos podem ser adicionados aqui...
        
        yield loader.load_item()

        # 2. BUSCA, FILTRAGEM E PROPAGAÇÃO PARA NOVOS LINKS
        current_depth = response.meta.get('depth', 0)
        if current_depth >= self.max_depth:
            self.logger.info(f"Profundidade máxima atingida em: {current_url}")
            return

        # Encontra todos os links na página
        links = response.css('a::attr(href)').getall()

        for link in links:
            # Transforma links relativos (ex: /noticias/123) em absolutos
            absolute_link = response.urljoin(link)
            
            # Decide se o link deve ser seguido
            if self.deve_seguir_o_link(absolute_link):
                yield scrapy.Request(
                    absolute_link,
                    callback=self.parse,
                    meta={'depth': current_depth + 1}
                )

    def deve_seguir_o_link(self, url: str) -> bool:
        """
        A LÓGICA CENTRAL: decide se um link é relevante o suficiente para ser seguido.
        """
        # Ignora links que não são HTTP/HTTPS ou links para âncoras na mesma página
        if not url.startswith(('http', 'https')) or '#' in url:
            return False

        # 1. Sempre segue links que pertencem aos domínios iniciais (links internos)
        if urlparse(url).netloc in self.allowed_domains:
            return True
        
        # 2. Para links externos, verifica se alguma palavra-chave está na URL
        # Isso aumenta a chance de o link ser sobre nosso tema.
        url_lower = url.lower()
        for keyword in self.KEYWORDS:
            if keyword in url_lower:
                self.logger.info(f"Link externo relevante encontrado: {url}")
                return True
        
        return False
