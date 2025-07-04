import scrapy
from itemloaders.processors import TakeFirst, MapCompose, Join, Compose
from w3lib.html import remove_tags
import re
import dateparser
import unicodedata

def safe_remove_tags(value):
    """Remove tags HTML de forma segura."""
    if value is None: return ""
    return remove_tags(str(value))

def clean_text(text):
    """Limpa e normaliza o texto."""
    if text is None: return ""
    text = unicodedata.normalize('NFC', text)
    return text.strip()

def parse_date(date_str: str):
    """
    Converte uma string de data para o formato YYYY-MM-DD.
    Retorna uma string vazia ("") se a conversão falhar.
    """
    if not date_str:
        return ""  # Retorna string vazia se a entrada for vazia
    try:
        parsed_date = dateparser.parse(date_str, languages=['pt'])
        # Retorna string vazia se o dateparser não conseguir converter
        return parsed_date.strftime('%Y-%m-%d') if parsed_date else ""
    except (TypeError, ValueError):
        # Retorna string vazia em caso de outros erros
        return ""

def process_content(text_block):
    
    if not text_block: return ""

    lines = text_block.splitlines()
    
    cleaned_lines = []
    for line in lines:
        normalized_line = re.sub(r'\s+', ' ', line).strip()
        if normalized_line:
            cleaned_lines.append(normalized_line)
            
    final_text = "\n".join(cleaned_lines)
    final_text = re.sub(r'(\n\s*){3,}', '\n\n', final_text)

    return final_text

class MobilidadeItem(scrapy.Item):
    url_fonte = scrapy.Field(
        output_processor=TakeFirst()
    )

    site_de_origem = scrapy.Field(
        output_processor=TakeFirst()
    )

    titulo = scrapy.Field(
        input_processor=MapCompose(safe_remove_tags, clean_text),
        output_processor=TakeFirst()
    )

    conteudo_texto = scrapy.Field(
        input_processor=MapCompose(safe_remove_tags, clean_text),
        output_processor=Compose(Join('\n'), process_content)
    )

    data_publicacao = scrapy.Field(
        input_processor=MapCompose(clean_text, parse_date),
        output_processor=TakeFirst()
    )
