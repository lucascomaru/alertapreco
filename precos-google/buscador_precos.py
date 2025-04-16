import requests
from bs4 import BeautifulSoup
import re
import json 
from urllib.parse import quote_plus 

CABECALHOS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7', 
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Upgrade-Insecure-Requests': '1',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin', 
    'Sec-Fetch-User': '?1',
}

def limpar_preco(texto_preco):

    if not texto_preco:
        return None
    try:

        string_numerica = re.sub(r'[^\d,.]', '', texto_preco)

        if '.' in string_numerica and ',' in string_numerica:
            if string_numerica.rfind('.') > string_numerica.rfind(','):
                string_numerica = string_numerica.replace(',', '') 
            else:
                 string_numerica = string_numerica.replace('.', '').replace(',', '.') 
        elif ',' in string_numerica:
             string_numerica = string_numerica.replace('.', '').replace(',', '.')
        elif '.' in string_numerica and string_numerica.count('.') == 1 and string_numerica.endswith('.'):
             string_numerica = string_numerica.replace('.', '') 
        elif '.' in string_numerica:
             if string_numerica.count('.') > 1:
                  string_numerica = string_numerica.replace('.', '')

        return float(string_numerica)

    except (ValueError, IndexError):
        return None 


def buscar_google_shopping(consulta):

    consulta_codificada = quote_plus(consulta)
    url = f"https://www.google.com/search?tbm=shop&q={consulta_codificada}&hl=pt-BR&gl=BR"

    print(f"Buscando em: {url}")

    try:
        resposta = requests.get(url, headers=CABECALHOS, timeout=20)
        resposta.raise_for_status() 

        sopa = BeautifulSoup(resposta.text, 'html.parser')

        produtos_encontrados = []

        containers_produtos = sopa.select('.sh-dgr__gr-auto.sh-dgr__grid-result') 

        if not containers_produtos:
             containers_produtos = sopa.select('.sh-pr__product-results-grid .sh-pr__product-result')

        if not containers_produtos:
            return []

        print(f"Encontrados {len(containers_produtos)} potenciais produtos.")

        for div_produto in containers_produtos:
            dados_produto = {}

            elemento_titulo = div_produto.select_one('h3.tAxDx')
            if not elemento_titulo:
                 elemento_titulo = div_produto.select_one('h4')

            dados_produto['titulo'] = elemento_titulo.get_text(strip=True) if elemento_titulo else "Título não encontrado"

            elemento_preco = div_produto.select_one('span.a8Pemb') 
            if elemento_preco:
                 texto_preco_extraido = elemento_preco.get_text(strip=True)
                 dados_produto['preco'] = limpar_preco(texto_preco_extraido)
                 dados_produto['preco_str'] = texto_preco_extraido
            else:
                 dados_produto['preco'] = None
                 dados_produto['preco_str'] = "Preço não encontrado"

            elemento_loja = div_produto.select_one('div.aULzUe')
            if not elemento_loja:
                 elemento_loja = div_produto.select_one('span.E5ocAb')

            dados_produto['loja'] = elemento_loja.get_text(strip=True) if elemento_loja else "Loja não encontrada"

            elemento_link = div_produto.select_one('a.sh-np__click-target')
            if not elemento_link:
                 elemento_link = div_produto.find('a', href=True)

            if elemento_link and 'href' in elemento_link.attrs:
                href_link = elemento_link['href']
                if href_link.startswith('/url?q='):
                    from urllib.parse import unquote, parse_qs, urlparse
                    link_decodificado = unquote(href_link)
                    query_string = urlparse(link_decodificado).query
                    parametros = parse_qs(query_string)
                    link_real = parametros.get('adurl', parametros.get('url', parametros.get('q', [None])))[0]
                elif href_link.startswith('http'):
                     dados_produto['link'] = href_link
                else:
                     dados_produto['link'] = f"https://www.google.com{href_link}"
            else:
                 dados_produto['link'] = "Link não encontrado"

            if dados_produto.get('titulo') != "Título não encontrado":
                 produtos_encontrados.append(dados_produto)


        return produtos_encontrados

    # Tratando possíveis erros

    except requests.exceptions.Timeout:
        print("Erro: A requisição demorou muito. Tente novamente.")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Erro de rede ao buscar: {e}")
        if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 429:
             print("AVISO: Você foi bloqueado temporariamente pelo Google. Espere um pouco antes de tentar novamente")
        return []
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a extração dos dados: {e}")
        return []

if __name__ == "__main__":
    termo_busca = input("Digite o nome do produto que você busca: ")

     # Loop para garantir que o usuário digite um preço válido
    while True:
        try:
            preco_maximo_str = input("Digite o preço máximo desejado (ex: 2000.00) ou deixe em branco para ver todos: ")
            if not preco_maximo_str:
                preco_maximo = float('inf') 
                break
            preco_maximo = float(preco_maximo_str)
            if preco_maximo >= 0:
                break
            else:
                print("Por favor, digite um preço válido (número positivo).")
        except ValueError:
            print("Entrada inválida. Por favor, digite um número para o preço.")

    print("\nIniciando busca...")
    resultados_brutos = buscar_google_shopping(termo_busca)

    if not resultados_brutos:
        print("\nNão foi possível obter resultados da busca.")
    else:
        print(f"\nEncontrados {len(resultados_brutos)} resultados brutos. Filtrando por preço <= R$ {preco_maximo:.2f}...\n")

        resultados_filtrados = []
        for produto in resultados_brutos:
            if produto.get('preco') is not None and produto['preco'] <= preco_maximo:
                resultados_filtrados.append(produto)
            elif produto.get('preco') is None and preco_maximo == float('inf'):
                 resultados_filtrados.append(produto)


        if not resultados_filtrados:
            if preco_maximo == float('inf'):
                 print("Nenhum resultado encontrado para sua busca.")
            else:
                 print(f"Nenhum resultado encontrado para '{termo_busca}' com preço até R$ {preco_maximo:.2f}.")
        else:
            print(f"--- Resultados para '{termo_busca}' (até R$ {preco_maximo:.2f}) ---")
            resultados_filtrados.sort(key=lambda x: x.get('preco') if x.get('preco') is not None else float('inf'))

            for indice, produto in enumerate(resultados_filtrados):
                preco_exibicao = f"R$ {produto['preco']:.2f}" if produto['preco'] is not None else produto['preco_str']
                print(f"{indice+1}. {produto['titulo']}")
                print(f"   Preço: {preco_exibicao}")
                print(f"   Loja:  {produto['loja']}")
                print("-" * 20)

            print(f"--- Fim dos {len(resultados_filtrados)} resultados filtrados ---")