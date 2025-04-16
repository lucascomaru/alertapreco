# Buscador de Preços Google Shopping (Python)

Um script simples em Python que busca produtos no Google Shopping com base em um termo de pesquisa e um preço máximo definido pelo usuário.

## Funcionalidades

*   Busca por nome de produto no Google Shopping.
*   Permite definir um preço máximo para filtrar os resultados.
*   Exibe os produtos encontrados (título, preço, loja) que atendem ao critério de preço no console.
*   Ordena os resultados pelo menor preço.

## Tecnologias Utilizadas

*   Python 3
*   Requests 
*   Beautiful Soup 4 

## Instalação e Configuração

1.  **Clonar o repositório:**
    ```bash
    https://github.com/lucascomaru/alertapreco.git
    cd alertapreco\precos-google
    ```

2.  **Criar e ativar um ambiente virtual:**
    ```bash
    python -m venv venv
    # No Windows: venv\Scripts\activate
    # No Linux/macOS: source venv/bin/activate
    ```

3.  **Instalar as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

## Como Usar

1.  Certifique-se de que o ambiente virtual está ativo.
2.  Execute o script:  python buscador_precos.py 
3.  Siga as instruções no console para digitar o nome do produto e o preço máximo desejado.
4.  Aparecerá um link do Google Shopping com o produto desejado

## Limitações

*   Depende da estrutura HTML atual do Google Shopping.
*   Pode ser bloqueado pelo Google se usado excessivamente.
*   A extração de dados (especialmente o link real do produto) pode não ser 100% precisa.
*   Não possui interface gráfica nem notificações automáticas (nesta versão).
