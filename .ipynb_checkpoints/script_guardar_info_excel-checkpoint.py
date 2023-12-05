import requests
from bs4 import BeautifulSoup
import pandas as pd

# Lista de URLs de páginas web 
urls = [
#se escriben las urls de las noticias

       ]


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