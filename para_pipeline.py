import requests
from bs4 import BeautifulSoup
import pandas as pd
import nltk
from nltk import pos_tag, word_tokenize
from nltk.corpus import stopwords


# Lista de URLs para scrapear
urls = [
    #ejemplo de urls
'https://viapais.com.ar/entretenimiento/gustavo-cerati-fue-elegido-entre-los-mejores-cantantes-de-rock-de-la-historia/',
'https://viapais.com.ar/estilo/bella-hadid-revoluciono-las-redes-al-posar-calva-y-sin-ropa-para-una-campana/',
'https://viapais.com.ar/por-las-redes/fortnite-devuelve-dinero-a-sus-jugadores-como-reclamarlo-y-que-requisitos-debes-cumplir/',
'https://viapais.com.ar/entretenimiento/asi-sera-la-exclusiva-cena-show-de-luis-miguel-en-buenos-aires-entradas-a-1-millon-de-pesos/',
'https://viapais.com.ar/estilo/al-estilo-de-lady-di-kate-middleton-impone-la-moda-del-sastrero-monocromatico/',
'https://viapais.com.ar/entretenimiento/asi-esta-hoy-fernando-colunga-el-protagonista-de-maria-la-del-barrio/',
'https://viapais.com.ar/entretenimiento/tiene-82-anos-y-la-eligio-el-publico-asi-fue-el-debut-de-nelly-camjalli-en-el-bailando-2023/',
'https://viapais.com.ar/entretenimiento/el-emotivo-ultimo-posteo-de-silvina-luna-en-instagram-antes-de-ser-internada-a-no-bajar-los-brazos/',
'https://viapais.com.ar/entretenimiento/sergio-massa-lotocki-mato-a-silvina-luna/',
'https://viapais.com.ar/entretenimiento/luego-de-celebrarse-el-dia-de-shakira-la-artista-dejo-un-emotivo-mensaje-no-me-lo-merezco/',
'https://viapais.com.ar/cordoba/fin-del-misterio-un-joven-mostro-cual-es-el-pasaporte-para-viajar-a-cordoba-y-se-volvio-viral/',
'https://viapais.com.ar/entretenimiento/quien-es-roberto-storino-landi-el-novio-de-charlotte-caniggia-que-aparecio-en-el-bailando-2023/',
'https://viapais.com.ar/entretenimiento/marcela-tinayre-revelo-al-aire-una-intimidad-y-no-se-la-dejaron-pasar/',
'https://viapais.com.ar/entretenimiento/javier-milei-y-fatima-florez-seran-los-primeros-invitados-a-la-mesa-de-mirtha-legrand-donde-nos-conocimos/',
'https://viapais.com.ar/urbano/emilia-mernes-revelo-un-insolito-detalle-de-duki-que-le-molesta-cuando-duermen-juntos/',
'https://viapais.com.ar/cordoba/got-talent-argentina-la-cordobesa-de-17-anos-que-gano-el-boton-dorado-con-su-increible-voz/',
'https://viapais.com.ar/rumbos/mia-khalifa-se-sumo-a-una-tendencia-que-ya-lucieron-oriana-sabatini-y-dua-lipa/',
'https://viapais.com.ar/entretenimiento/pamela-sosa-expareja-de-anibal-lotocki-fue-a-increparlo-a-su-casa-asesino-da-la-cara/',
'https://viapais.com.ar/entretenimiento/como-son-y-cuanto-salen-los-vinos-que-le-regalo-la-mama-de-cami-homs-a-marcelo-tinelli/',

]

# Palabras clave a buscar en las URLs
#este es un ejemplo de palabras clave de acuerdo a la pagina:
keywords = ['article','noticias','news','nota','/','-']


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
with open('extraccion_urls.txt', 'w') as file:
    for url in unique_urls:
        file.write("'"+url + "',"+'\n')
print("txt listo")

#Palabras clave para cada categoría
palabras_clave = {

    'salud': ['salud', 'medicina', 'enfermedad', 'medico', 'bienestar'],
    'deportes': ['deportes', 'futbol', 'baloncesto', 'tenis', 'competicion'],
    'medioambiente': ['medioambiente', 'ecologia', 'naturaleza', 'sostenibilidad', 'cambio climatico'],
    'economia': ['economia', 'finanzas', 'negocios', 'mercado', 'inversion'],
    'politica': ['politica', 'gobierno', 'elecciones', 'legislación', 'parlamento'],
    'entretenimiento': ['entretenimiento', 'cine', 'musica', 'celebridades', 'espectaculos'],
    'horoscopo': ['horoscopo', 'astrologia', 'signos zodiacales', 'predicciones', 'astrologia diaria'],
    'cultura': ['cultura', 'arte', 'literatura', 'tradiciones', 'patrimonio'],
    'ciencia_tecnologia': ['ciencia', 'tecnologia', 'innovacion', 'descubrimientos', 'avances cientificos'],
    'educacion': ['educacion', 'escuela', 'aprendizaje', 'docentes', 'formacion']
}

# Creacion de listas para almacenar datos
fechas = []
textos = []
titulos = []  # Agregar una lista para almacenar los títulos
categorias = []
longitudes = []

# Función para determinar la categoría de la noticia
def determinar_categoria(tipo_noticia):
    for categoria, palabras in palabras_clave.items():
        for palabra in palabras:
            if tipo_noticia is None:
                return 'Otra'
            if palabra in tipo_noticia:
                return categoria
    return 'Otra'  # Si no se encuentra ninguna categoría

# Función para obtener los datos de una URL
def scrape_noticia(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Se intenta extraer el título de la noticia
    titulo_noticia = soup.find('h1').text.strip() if soup.find('h1') else "no especificado"  # Modificar esta línea

    # Se intenta extraer el título de la noticia (tipo de noticia)
    tipo_noticia = soup.title.string.strip() if soup.title else None

    # Determinar la categoría de la noticia
    categoria = determinar_categoria(tipo_noticia)

    # Se intenta extraer la fecha de la noticia de varias formas
    fecha_noticia = None

    # Buscar elementos con atributo 'datetime' que a menudo contiene la fecha
    date_elements = soup.find_all(['time', 'span', 'p', 'publication-date', 'fecha'], {'datetime': True})
    for date_element in date_elements:
        fecha_noticia = date_element['datetime'].strip()
        if fecha_noticia:
            break  # Salir del bucle si se encuentra una fecha

    if fecha_noticia is None:
        # Intentar buscar elementos con clases de fecha comunes
        common_date_classes = ['date', 'published', 'fecha', 'publication-date']
        date_elements = soup.find_all(['time', 'span', 'p'], class_=common_date_classes)
        for date_element in date_elements:
            fecha_noticia = date_element.text.strip()
            if fecha_noticia:
                break  # Salir del bucle si se encuentra una fecha

    if fecha_noticia is None:
        fecha_noticia = "Fecha no encontrada"  # Valor predeterminado si no se encuentra la fecha

    # Intentamos extraer el texto de la noticia
    texto_noticia = ''
    paragraphs = soup.find_all('p')
    for p in paragraphs:
        texto_noticia += p.text.strip() + ' '

    fechas.append(fecha_noticia)
    textos.append(texto_noticia)
    titulos.append(titulo_noticia)  # Agregar el título a la lista
    categorias.append(categoria)


# Iterar a través de las URLs y extraer los datos
for url in urls:
    scrape_noticia(url)

# Crear un DataFrame con los datos recopilados
data = {
    'fecha_noticia': fechas,
    'titulo_noticia': titulos,  # Agregar la columna de títulos
    'texto_noticia': textos,
    'categoria': categorias
}

df = pd.DataFrame(data)

# Calcular la longitud de la noticia
df['longitud_noticia'] = df['texto_noticia'].apply(len)

# Reorganizar las columnas en el orden deseado
df = df[['fecha_noticia', 'titulo_noticia', 'texto_noticia', 'longitud_noticia', 'categoria']]  # Agregar 'titulo_noticia'

# Ordenar el DataFrame por 'texto_noticia'
df = df.sort_values(by='texto_noticia')

# Guardar el DataFrame en un archivo Excel (.xlsx) con el motor xlsxwriter
output_file = 'Data.xlsx'
df.to_excel(output_file, index=False, engine='xlsxwriter')

# Imprimir el DataFrame
print(df)

# Imprimir mensaje de confirmación
print(f"Los datos se han guardado en '{output_file}'.")
