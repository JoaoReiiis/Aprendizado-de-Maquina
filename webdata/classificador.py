import ollama

texto_para_classificar = """
Uma Cidade inteligente (CI) é uma cidade que usa tipos diferentes de sensores eletrônicos para coletar dados e usá-los para gerenciar recursos e ativos eficientemente. Incluindo dados coletados de cidadãos, dispositivos que são processados e analisados para monitorar e gerenciar sistemas de tráfego e transporte,[1][2] usinas de energia, redes de abastecimento de água, gerenciamento de saneamento básico, detecção de crimes, sistemas de informação, escolas, livrarias, hospitais e diversos outros serviços para a comunidade.[3][4]

O conceito de cidade inteligente integra a tecnologia da informação e comunicação (TIC), vários dispositivos físicos conectados à rede IoT para otimizar a eficiência das operações e serviços da cidade e conectar-se aos cidadãos.[5][6] A tecnologia da cidade inteligente permite que as autoridades da cidade interajam diretamente com tanto a infraestrutura da comunidade e da cidade como monitorem o que está acontecendo na cidade e como a cidade está evoluindo. As Tecnologias de informação e comunicação são usadas para melhorar a qualidade, desempenho e interatividade dos serviços urbanos, reduzir custos e consumo de recursos e aumentar o contato entre cidadãos e governo.[7][8] As cidades inteligentes podem ajudar tanto o poder público a reconhecer problemas em tempo real, quanto o cidadão a produzir informações, auxiliando a mapear, discutir e enfrentar essas dificuldades. Uma CI pode, portanto, estar mais preparada para responder a desafios do que uma com um simples relacionamento "passivo" com seus cidadãos.[9] No entanto, o próprio termo permanece pouco claro para suas especificidades e, portanto, aberto a muitas interpretações, vulnerável à mudanças.[10]

As principais mudanças tecnológicas, econômicas e ambientais geraram interesse em cidades inteligentes, incluindo mudança climática, reestruturação econômica, mudança para consumo por varejo e entretenimento on-line, populações envelhecidas, crescimento da população urbana e pressões nas finanças públicas.[11] A União Europeia (UE) dedicou esforços constantes à elaboração de uma estratégia para alcançar um crescimento urbano 'inteligente' para as cidades e regiões metropolitanas.[12][13] A UE desenvolveu uma série de programas no âmbito da "Agenda Digital da Europa".[14] Em 2010, destacou o seu foco no fortalecimento da inovação e do investimento em serviços de TIC, com o objetivo de melhorar os serviços públicos e a qualidade de vida. Estimativas da Arup é de que o mercado global de serviços urbanos inteligentes será de US$ 400 bilhões por ano até 2020.[11] Exemplos de tecnologias e programas de cidades inteligentes foram implementados em Singapura,[15] cidades inteligentes na: Índia,[16][17]Dubai,[18] Milton Keynes,[19] Southampton,[20] Amsterdã,[21] Barcelona,[22][23] Madri, Estocolmo,[24] Copenhague, China[25] e Nova York.[26]
"""

prompt_otimizado = f"""
Você é um classificador de texto especialista. Sua única tarefa é determinar se o texto a seguir é sobre "mobilidade inteligente".
A mobilidade inteligente refere-se à utilização de tecnologias e dados para otimizar o transporte urbano, tornando-o mais eficiente, sustentável e seguro.

Com base nesta definição, classifique o texto abaixo.
Sua resposta DEVE SER uma única palavra: RELACIONADO ou NAO. Não escreva mais nada.

Texto para classificar:
---
{texto_para_classificar}
---

Classificação (apenas uma palavra):"""


try:
    print("Enviando prompt para o modelo...")
    response = ollama.generate(
        model='deepseek-r1:8b',
        prompt=prompt_otimizado
    )

    classificacao_limpa = response['response'].strip().upper()

    print("\n--- Resposta Bruta do Modelo ---")
    print(response['response'])
    
    print("\n--- Classificação Final ---")
    print(classificacao_limpa)

    if "RELACIONADO" in classificacao_limpa:
        print("\nO texto foi classificado como RELACIONADO.")
    else:
        print("\nO texto foi classificado como NAORELACIONADO.")

except Exception as e:
    print(f"Ocorreu um erro ao contatar o Ollama: {e}")
    print("Verifique se o Ollama está em execução e o modelo 'deepseek-r1:1.5b' foi baixado com 'ollama run deepseek-r1:1.5b'.")