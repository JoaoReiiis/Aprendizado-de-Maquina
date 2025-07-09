import scrapy
from itemloaders.processors import TakeFirst, MapCompose, Join, Compose
from w3lib.html import remove_tags
import re
import dateparser
import unicodedata

def safe_remove_tags(value):
    if value is None: return ""
    return remove_tags(str(value))

def clean_text(text):
    if text is None: return ""
    text = unicodedata.normalize('NFC', text)
    return text.strip()

def parse_date(date_str: str):
    if not date_str:
        return ""
    try:
        parsed_date = dateparser.parse(date_str, languages=['pt'])
        return parsed_date.strftime('%Y-%m-%d') if parsed_date else ""
    except (TypeError, ValueError):
        return ""

def process_content(text_block):
    
    if not text_block: return ""

    footer_triggers = [
        "leia também:", "leia mais:", "veja também", "receba a newsletter", 
        "para saber mais", "fontes", "referências", "créditos"
    ]

    lines = text_block.splitlines()
    
    cutoff_index = len(lines)
    for i, line in enumerate(lines):
        line_lower = line.lower()
        for trigger in footer_triggers:
            if trigger in line_lower:
                cutoff_index = i
                break
        if cutoff_index != len(lines):
            break
    
    main_content_lines = lines[:cutoff_index]

    cleaned_lines = []
    for line in main_content_lines:
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
