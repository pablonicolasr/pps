import requests
from bs4 import BeautifulSoup
from datetime import datetime
from .models import Scraping, InformIngresada, Noticia
import re
from sklearn.svm import SVC 
import pandas as pd
import re
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report
from sklearn.decomposition import TruncatedSVD
from collections import Counter
import joblib
import json
import numpy  # Agrega esta línea para importar NumPy
import tensorflow as tf
import scipy.sparse as sp
import numpy as np
import scipy
import pickle,joblib
from sklearn.decomposition import TruncatedSVD
from dateutil import parser as date_parser
from tensorflow.keras.models import load_model



# Palabras clave para cada categoría
palabras_clave = {
    'salud': ['salud', 'medicina', 'enfermedad', 'medico', 'bienestar','diagnostico'],
    'deportes': ['deportes', 'futbol', 'baloncesto', 'tenis', 'competicion','natacion','basquet','rugby'],
    'medioambiente': ['medioambiente', 'ecologia', 'naturaleza', 'sostenibilidad', 'cambio climatico'],
    'economia': ['economia', 'finanzas', 'negocios', 'mercado', 'inversion','dolar'],
    'politica': ['politica', 'gobierno', 'elecciones', 'legislación', 'parlamento'],
    'entretenimiento': ['entretenimiento', 'cine', 'musica', 'celebridades', 'espectaculos'],
    'horoscopo': ['horoscopo', 'astrologia', 'signos zodiacales', 'predicciones', 'astrologia diaria','luna','ascendente'],
    'cultura': ['cultura', 'arte', 'literatura', 'tradiciones', 'patrimonio'],
    'ciencia_tecnologia': ['ciencia', 'tecnologia', 'innovacion', 'descubrimientos', 'avances cientificos','IA','avance'],
    'educacion': ['educacion', 'escuela', 'aprendizaje', 'docentes', 'formacion','maestros,']
}


def determinar_categoria(titulo, texto):
    # Convertir el título y texto a minúsculas para una comparación insensible a mayúsculas y minúsculas
    titulo_lower = titulo.lower()
    texto_lower = texto.lower()

    # Iterar sobre las categorías y palabras clave
    for categoria, palabras in palabras_clave.items():
        for palabra in palabras:
            # Verificar si la palabra clave está presente en el título o texto
            if palabra in titulo_lower or palabra in texto_lower:
                return categoria  # Devolver la categoría si se encuentra una palabra clave

    return 'Otra'  # Devolver 'Otra' si ninguna categoría coincide con las palabras clave

# Función para asignar categorías a las noticias
def asignar_categorias_a_noticias():
    # Obtener todas las instancias de Scraping
    scraping_objects = Scraping.objects.all()

    for scraping_obj in scraping_objects:
        # Determinar la categoría para el scraping actual
        categoria = determinar_categoria(scraping_obj.titulo, scraping_obj.texto)

        # Crear una instancia de Noticia con los datos relevantes, incluida la categoría
        noticia = Noticia(
            enlace=scraping_obj.enlace,
            titulo=scraping_obj.titulo,
            texto=scraping_obj.texto,
            categoria=categoria,
            tipo='scraping' if scraping_obj.enlace else 'texto',
            scraping=scraping_obj  # Relacionar la instancia de Noticia con la instancia de Scraping creada
        )

        # Guardar la instancia de Noticia en la base de datos
        noticia.save()

    return 'Categorías asignadas correctamente a las noticias.'


# Función para obtener el título del texto
def obtener_titulo(texto):
    # Buscar el título hasta el primer punto o hasta que encuentre comillas
    match = re.search(r'([^.\n"]+)', texto)
    if match:
        return match.group(0).strip()
    else:
        return "No especificado"

# Función para procesar el texto ingresado manualmente y guardar los resultados en la tabla Scraping
def procesar_texto_manual(texto_noticia):
    # Extraer el título de la noticia
    titulo_noticia = obtener_titulo(texto_noticia)

    # Calcular la longitud del texto de la noticia
    longitud_noticia = len(texto_noticia)

    # Crear un objeto Scraping con los datos recopilados
    scraping_obj = Scraping.objects.create(
        titulo=titulo_noticia,
        caracteres=longitud_noticia,
        fecha=datetime.now(),
        texto=texto_noticia
    )

    # Asignar categoría a la noticia
    categoria = determinar_categoria(titulo_noticia, texto_noticia)

    # Crear una instancia de Noticia con los datos recopilados y la relaciona con la instancia de Scraping
    noticia = Noticia.objects.create(
        titulo=titulo_noticia,
        caracteres=longitud_noticia,
        texto=texto_noticia,
        categoria=categoria,
        tipo='texto',
        scraping=scraping_obj  # Relacionar la instancia de Noticia con la instancia de Scraping creada
    )

    # Devolver la instancia de Noticia creada
    return noticia


def parse_fecha(fecha_str):
    try:
        return datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
    except ValueError:
        return None

def scrape_noticia(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extraer el título de la noticia
    titulo_noticia = soup.find('h1').text.strip() if soup.find('h1') else "No especificado"

    # Extraer el texto de la noticia
    texto_noticia = ' '.join([p.text.strip() for p in soup.find_all('p')])

    # Calcular la longitud del texto
    longitud_texto = len(texto_noticia)

    # Extraer la fecha de la noticia
    fecha_noticia_tag = soup.find(['time', 'span', 'p', 'publication-date', 'fecha'], {'datetime': True})
    fecha_noticia = fecha_noticia_tag['datetime'].strip() if fecha_noticia_tag else "Fecha no encontrada"
    fecha = parse_fecha(fecha_noticia)

    # Crear una instancia de Scraping con los datos recopilados
    scraping_obj = Scraping.objects.create(
        titulo=titulo_noticia,
        caracteres=longitud_texto,  # Guardar la longitud del texto en la instancia de Scraping
        fecha=fecha,
        texto=texto_noticia,
    )

    # Asignar categoría a la noticia
    categoria = determinar_categoria(titulo_noticia, texto_noticia)

    # Crear una instancia de Noticia con los datos recopilados y relacionarla con la instancia de Scraping
    noticia = Noticia.objects.create(
        enlace=url,
        titulo=titulo_noticia,
        texto=texto_noticia,
        caracteres=longitud_texto,
        categoria=categoria,
        tipo='scraping',
        scraping=scraping_obj
    )

    # Devolver la instancia de Noticia creada
    return noticia






def cargar_modelo_svm(ruta_modelo, ruta_svm_vectores):
    try:
        modelo_svm = joblib.load(ruta_modelo)
        vectorizador_tfidf = joblib.load(ruta_svm_vectores)
        return modelo_svm, vectorizador_tfidf
    except Exception as e:
        print(f'Error al cargar el modelo SVM: {e}')
        return None, None

def clasificar_svm(texto_para_clasificar,ruta_modelo_svm, ruta_svm_vectores, ruta_svm_svd):
    try:
        # Cargar el modelo SVM, el vectorizador TF-IDF y el modelo TruncatedSVD
        modelo_svm = joblib.load(ruta_modelo_svm)
        vectorizador_tfidf = joblib.load(ruta_svm_vectores)
        svd = joblib.load(ruta_svm_svd)

        # Preprocesar el texto de entrada
        nlp = spacy.load('es_core_news_sm')
        nlp.max_length = 4000000
        texto = re.sub(r'[^\w\s]', '', texto_para_clasificar)  # Eliminar caracteres no alfanuméricos
        texto = texto.lower()  # Convertir a minúsculas
        doc = nlp(texto)  # Tokenizar el texto
        filtered_words = [
            token.lemma_ for token in doc
            if token.pos_ in ('NOUN', 'ADJ', 'VERB') and token.lemma_.lower() not in nlp.Defaults.stop_words
            and not token.is_digit
        ]
        filtered_text = ' '.join(filtered_words)

# Reducción de dimensionalidad con TruncatedSVD
        n_components = 100  # Ajusta el número de componentes según tus necesidades
        svd = TruncatedSVD(n_components=n_components)
        X_tfidf_svd = svd.fit_transform(X_tfidf)

        # Vectorizar el texto usando TF-IDF
        X_tfidf = vectorizador_tfidf.transform([filtered_text])

        # Reducir la dimensionalidad con TruncatedSVD utilizando la misma transformación que se usó durante el entrenamiento
        X_tfidf_svd = svd.transform(X_tfidf)

        # Realizar la predicción utilizando el modelo SVM
        categoria_predicha = modelo_svm.predict(X_tfidf_svd)[0]

        return categoria_predicha
    except Exception as e:
        return f"Error inesperado al clasificar el texto: {e}"












def cargar_modelo_red_neuronal(ruta_modelo_redes_neuronales_h5):
    try:
        modelo_cargado = load_model(ruta_modelo_redes_neuronales_h5)
        return modelo_cargado
    except Exception as e:
        print(f'Error al cargar el modelo de redes neuronales: {e}')
        return None
    
def cargar_label_encoder(ruta_modelo_redes_neuronales_label):
    try:
        label_encoder_cargado = joblib.load(ruta_modelo_redes_neuronales_label)
        return label_encoder_cargado
    except Exception as e:
        print(f'Error al cargar el LabelEncoder: {e}')
        return None    
    

def predecir_categoria(texto_noticia, modelo_cargado, vectorizer_tfidf):
    try:
        # Normalizar el texto de la noticia
        texto_normalizado = re.sub(r'[^\w\s]', '', texto_noticia.lower())

        # Vectorizar el texto normalizado
        texto_vectorizado = vectorizer_tfidf.transform([texto_normalizado])

        # Convertir la matriz dispersa a un array de NumPy denso
        texto_vectorizado_dense = texto_vectorizado.toarray()

        # Realizar la predicción
        categoria_predicha_numero = np.argmax(modelo_cargado.predict(texto_vectorizado_dense))
        return categoria_predicha_numero
    except Exception as e:
        print(f'Error al realizar la predicción con el modelo de redes neuronales: {e}')
        return None

def clasificar_redes_neuronales(modelo_redes_neuronales, texto):
    try:
        nlp = spacy.load('es_core_news_sm')
        nlp.max_length = 4000000

        # Normalización del texto
        text = re.sub(r'[^\w\s]', '', texto)
        text = text.lower()

        # Uso de spaCy para lematización y eliminación de stopwords
        doc = nlp(text)
        filtered_words = [
            token.lemma_ for token in doc
            if token.pos_ in ('NOUN', 'ADJ', 'VERB') and token.lemma_.lower() not in nlp.Defaults.stop_words
            and not token.is_digit  # Excluir números
        ]
        filtered_text = ' '.join(filtered_words)

        # Contar la frecuencia de las palabras utilizando un diccionario
        word_freq = Counter(filtered_words)

        # Cargar las palabras más frecuentes desde el archivo de texto (o de donde las obtengas)
        palabras_mas_frecuentes = list(word_freq.keys())

        # Vectorización con reducción de dimensionalidad mediante umbral de frecuencia (TF-IDF)
        vectorizer_tfidf = TfidfVectorizer(vocabulary=palabras_mas_frecuentes)
        X_tfidf = vectorizer_tfidf.fit_transform([texto])


        # Imprimir el resumen del modelo para verificar su estructura
        print(modelo_redes_neuronales.summary())

        # Realizar la predicción
        categoria = predecir_categoria(texto, modelo_redes_neuronales, vectorizer_tfidf)
        return categoria
    except Exception as e:
        print(f'Error al realizar la predicción con el modelo de redes neuronales: {e}')
        return None

    
    
    

# Función para cargar el modelo de Random Forest desde un archivo 
import joblib

def cargar_modelo_random_forest(ruta_modelo_random_forest):
    try:
        modelo_random_forest = joblib.load(ruta_modelo_random_forest)
        return modelo_random_forest
    except Exception as e:
        print(f'Error al cargar el modelo Random Forest: {e}')
        return None

def cargar_vectorizador_tf_idf(ruta_vectorizador_random_forest):
    try:
        vectorizador_tfidf = joblib.load(ruta_vectorizador_random_forest)
        return vectorizador_tfidf
    except Exception as e:
        print(f'Error al cargar el vectorizador TF-IDF: {e}')
        return None

def cargar_modelo_truncated_svd(ruta_svd_forest):
    try:
        svd = joblib.load(ruta_svd_forest)
        return svd
    except Exception as e:
        print(f'Error al cargar el modelo Truncated SVD: {e}')
        return None





# Función para realizar la clasificación con el modelo de Random Forest cargado
def clasificar_random_forest(modelo_random_forest, texto):
    try:
        nlp = spacy.load('es_core_news_sm')
        nlp.max_length = 4000000

        # Normalización del texto
        text = re.sub(r'[^\w\s]', '', texto)
        text = text.lower()

        # Uso de spaCy para lematización y eliminación de stopwords
        doc = nlp(text)
        filtered_words = [
            token.lemma_ for token in doc
            if token.pos_ in ('NOUN', 'ADJ', 'VERB') and token.lemma_.lower() not in nlp.Defaults.stop_words
            and not token.is_digit  # Excluir números
        ]
        filtered_text = ' '.join(filtered_words)

        # Contar la frecuencia de las palabras utilizando un diccionario
        word_freq = Counter(filtered_words)

        # Cargar las palabras más frecuentes desde el archivo de texto (o de donde las obtengas)
        palabras_mas_frecuentes = list(word_freq.keys())

        # Vectorización con reducción de dimensionalidad mediante umbral de frecuencia (TF-IDF)
        vectorizer_tfidf = TfidfVectorizer(vocabulary=palabras_mas_frecuentes)
        X_tfidf = vectorizer_tfidf.fit_transform([texto])


        # Imprimir el resumen del modelo para verificar su estructura
        print(modelo_redes_neuronales.summary())

        # Realizar la predicción
        categoria = predecir_categoria(texto, modelo_redes_neuronales, vectorizer_tfidf)
        return categoria
    except Exception as e:
        print(f'Error al realizar la predicción con el modelo de redes neuronales: {e}')
        return None
