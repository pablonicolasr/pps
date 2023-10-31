import requests
from bs4 import BeautifulSoup

# Vector de URLs que deseas scrapear
urls = [
'https://www.bbc.com/mundo/topics/cpzd498zkxgt?page=11',
'https://www.bbc.com/mundo/topics/cpzd498zkxgt?page=12',
'https://www.bbc.com/mundo/topics/cpzd498zkxgt?page=13',
'https://www.bbc.com/mundo/topics/cpzd498zkxgt?page=14',
'https://www.bbc.com/mundo/topics/cpzd498zkxgt?page=15',


    
]

# Crea un conjunto para almacenar URLs únicas
unique_urls = set()

# Itera a través de las URLs en el vector
for url in urls:
    # Realiza una solicitud HTTP para obtener el contenido de la página
    response = requests.get(url)

    # Verifica si la solicitud fue exitosa
    if response.status_code == 200:
        # Analiza el contenido HTML de la página con BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Encuentra todos los enlaces (hipervínculos) dentro de elementos <a> con un atributo href
        links = soup.find_all('a', href=True)
        
        # Itera a través de los enlaces e imprime sus URLs si son únicas
        for link in links:
            sub_url = link['href']
            if sub_url not in unique_urls:
                unique_urls.add(sub_url)
                print("'" + sub_url + "',")
    else:
        print(f"No se pudo acceder a la página: {url}")
