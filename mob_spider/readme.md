Crawler Focado em Mobilidade Inteligente

Este projeto é um web crawler desenvolvido em Python com o framework Scrapy. Seu objetivo é coletar, de forma autônoma, artigos e notícias sobre mobilidade urbana, cidades inteligentes, transporte sustentável e tecnologias relacionadas.
Principais Funcionalidades

    Coleta Direcionada: Navega pela web seguindo apenas links que contenham palavras-chave relevantes para o tema de mobilidade, garantindo o foco dos dados.

    Extração Inteligente de Conteúdo: Utiliza a biblioteca trafilatura para identificar e extrair o conteúdo principal das páginas, descartando menus, anúncios e rodapés.

    Limpeza e Estruturação de Dados: Processa os dados brutos para remover tags HTML, normalizar textos e padronizar datas (usando dateparser) em um formato consistente.

    Controle de Rastreamento: Permite configurar a profundidade máxima da busca para otimizar o tempo de execução e o escopo da coleta.

    Exportação Simples: Os dados coletados podem ser facilmente exportados para formatos como JSON, CSV ou XML.

Tecnologias Utilizadas

    Python 3

    Scrapy Framework

    Trafilatura (para extração de conteúdo)

    Dateparser (para análise de datas)

Como Começar
Pré-requisitos

    Python 3.8 ou superior

    Pip (gerenciador de pacotes do Python)

Instalação

    Clone este repositório (ou baixe os arquivos para uma pasta local).

    Crie um ambiente virtual (recomendado para isolar as dependências do projeto):

    python -m venv venv

    Ative o ambiente virtual:

        No Windows:

        .\venv\Scripts\activate

        No macOS/Linux:

        source venv/bin/activate

    Instale as bibliotecas necessárias:

    pip install Scrapy trafilatura dateparser

Executando o Crawler

Para iniciar a coleta de dados, navegue até a pasta raiz do projeto no seu terminal (onde o arquivo scrapy.cfg está localizado) e execute o seguinte comando:

python -m scrapy crawl mob -o dados_coletados.json

    mob é o nome do spider que fará o rastreamento.

    O argumento -o (output) salva os resultados em um arquivo. Você pode alterar dados_coletados.json para o nome que preferir, usando extensões como .csv ou .xml se desejar outro formato.


