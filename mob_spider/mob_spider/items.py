# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy

class MobilidadeItem(scrapy.Item):
    url_fonte = scrapy.Field()
    site_de_origem = scrapy.Field()
    titulo = scrapy.Field()
    
    conteudo_texto = scrapy.Field()
    
    autor = scrapy.Field()
    data_publicacao = scrapy.Field()
    tags_ou_categorias = scrapy.Field()
    
    profundidade_crawl = scrapy.Field()

