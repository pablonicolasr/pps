import requests
from bs4 import BeautifulSoup

# Lista de URLs para scrapear
urls = [
    #ejemplo de urls
'https://www.bbc.com/mundo/topics/cpzd498zkxgt?page=11',
'https://www.bbc.com/mundo/topics/cpzd498zkxgt?page=12',
'https://www.bbc.com/mundo/topics/cpzd498zkxgt?page=13',
'https://www.bbc.com/mundo/topics/cpzd498zkxgt?page=14',
'https://www.bbc.com/mundo/topics/cpzd498zkxgt?page=15',



]


# Palabras clave a buscar en las URLs
#este es un ejemplo de palabras clave de acuerdo a la pagina:
keywords = ['article','noticias']


# Crea un conjunto para almacenar URLs únicas que cumplen con las condiciones
unique_urls = set()

# Itera a través de las URLs en la lista
for url in urls:
    # Realiza una solicitud HTTP para obtener el contenido de la página
    response = requests.get(url)

    # Verifica si la solicitud fue exitosa
    if response.status_code == 200:
        # Analiza el contenido HTML de la página con BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Encuentra todos los enlaces (hipervínculos) dentro de elementos <a> con un atributo href
        links = soup.find_all('a', href=True)

        # Itera a través de los enlaces y agrega sus URLs al conjunto si son únicas y contienen las palabras clave
        for link in links:
            url = link['href']
            for keyword in keywords:
                if keyword in url:
                    unique_urls.add(url)
    else:
        print("No se pudo acceder a la página:", url)

# Guarda los resultados en un archivo de texto 
with open('resultados.txt', 'w') as file:
    for url in unique_urls:
        file.write("'"+url + "',"+'\n')
print("txt listo")
