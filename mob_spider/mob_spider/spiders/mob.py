import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from ..items import MobilidadeItem

class MobSpider(CrawlSpider):
    name = "mob"

    allowed_domains = ["mobilidade.estadao.com.br", "summitmobilidade.estadao.com.br"]

    start_urls = [
        "https://mobilidade.estadao.com.br/",
        "https://summitmobilidade.estadao.com.br/"
    ]

    rules = (
        # Regra 1: Seguir links de notícias e artigos.
        # A expressão regular em 'allow' busca por URLs que parecem ser artigos.
        # 'callback' especifica a função que processará a página encontrada.
        # 'follow=True' permite que ele continue procurando por mais links dentro da página do artigo.
        Rule(
            LinkExtractor(
                allow=r'/noticias/|/reportagens/', # Padrão para URLs de artigos
                deny=r'/tags/|/autor/' # Evita seguir para páginas de tags ou autores
            ),
            callback='parse_item',
            follow=True
        ),
         Rule(
            LinkExtractor(
                allow=r'/[a-z,-]+/$', # Padrão para categorias
                deny=r'/noticias/|/reportagens/' # Evita re-processar o que a Regra 1 já pega
            ),
            follow=True
        ),
    )

    def parse_item(self, response):
        """
        Esta função é chamada para cada página de artigo encontrada.
        Ela utiliza o ItemLoader para extrair e carregar os dados.
        """
        # Nome do site de origem para referência
        site_origem = "Estadão Mobilidade"
        if "summitmobilidade" in response.url:
            site_origem = "Summit Mobilidade Estadão"

        # O ItemLoader facilita a extração e o processamento dos dados.
        loader = ItemLoader(item=MobilidadeItem(), response=response)

        # Adiciona a URL da fonte e o site de origem
        loader.add_value('url_fonte', response.url)
        loader.add_value('site_de_origem', site_origem)

        # Extraindo dados usando seletores CSS (ou XPath)
        # OBS: Estes seletores são exemplos e podem precisar de ajuste se o site mudar.
        # Use o "Inspecionar Elemento" do seu navegador para encontrar os seletores corretos.

        # Título do artigo
        loader.add_css('titulo', 'h1.n--noticia__title::text')

        # Autor do artigo
        loader.add_css('autor', 'div.n--noticia__state-author p.author::text')

        # Data de publicação
        # O seletor busca o tempo e extrai o atributo 'datetime'
        loader.add_css('data_publicacao', 'div.n--noticia__state-date time::attr(datetime)')

        # Conteúdo do artigo
        # Pega todos os parágrafos dentro da área de conteúdo do artigo.
        # O '::text' extrai o texto de cada parágrafo. O loader junta tudo.
        loader.add_css('conteudo_texto', 'div.n--noticia__content p::text')

        # Tags ou categorias associadas ao artigo
        loader.add_css('tags_ou_categorias', 'div.n--noticia__tags a::text')

        yield loader.load_item()