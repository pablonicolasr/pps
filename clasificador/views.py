from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import cargar_svd_random, Clasificacion, Noticia
from .forms import NoticiaForm
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import load_model
import numpy as np
import pickle
from .models import InformIngresada
from .utils import scrape_noticia
from .utils import procesar_texto_manual
from .models import Scraping
from .models import cargar_modelo_svm, cargar_modelo_red_neuronal, preprocesar_datos
from .utils import cargar_modelo_svm, clasificar_svm, cargar_modelo_red_neuronal,cargar_label_encoder, clasificar_redes_neuronales,cargar_modelo_random_forest,cargar_vectorizador_tf_idf,cargar_modelo_truncated_svd, clasificar_random_forest
import os
from django.conf import settings
from .utils import cargar_modelo_svm
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from unidecode import unidecode
from tensorflow.keras.preprocessing.text import Tokenizer
MAX_SEQUENCE_LENGTH = 5587  # Definir la longitud máxima de secuencia según tu modelo
from tensorflow.keras.preprocessing.sequence import pad_sequences




def inicio(request):
    return render(request, 'paginas/inicio.html')

def clasificadores(request):
    noticias = Noticia.objects.all()  # Obtener todas las noticias
    return render(request, 'paginas/clasif_form.html')


def noticias(request):
    noticias = Noticia.objects.all()
    informes_ingresados = InformIngresada.objects.all()  # Obtener todos los InformIngresada
    return render(request, 'noticias/index.html', {'noticias': noticias, 'informes_ingresados': informes_ingresados})


def crear(request):
    if request.method == 'POST':
        if 'url_noticia' in request.POST:
            # Se proporcionó una URL, guarda en la BD en la tabla InformIngresada
            enlace = request.POST['url_noticia']
            inform_ingresada = InformIngresada.objects.create(enlace=enlace)
            # Realizar web scraping y guardar en Scraping
            scraping_obj = scrape_noticia(enlace)
            scraping_obj.ingresada = inform_ingresada
            scraping_obj.save()
        elif 'texto_noticia' in request.POST:
            # Se proporcionó texto directo, guarda en la BD en la tabla InformIngresada
            texto = request.POST['texto_noticia']
            inform_ingresada = InformIngresada.objects.create(texto=texto)
            # Procesar el texto manualmente y guardar en Scraping
            scraping_obj = procesar_texto_manual(texto)
            scraping_obj.ingresada = inform_ingresada
            scraping_obj.save()
        return redirect('noticias')

    return render(request, 'noticias/crear.html')


def editar(request, id):
    noti = Noticia.objects.get(id=id)
    formulario = NoticiaForm(request.POST or None, request.FILES or None, instance=noti)
    if formulario.is_valid() and request.POST:
        formulario.save()
        return redirect('noticias')
    return render(request, 'noticias/editar.html', {'formulario': formulario})

def eliminar(request, id):
    noti = Noticia.objects.get(id=id)
    noti.delete()
    return redirect('noticias')


vectorizador_tfidf = TfidfVectorizer()

def vista_clasificacion(request):
 

    if request.method == 'POST':
        modelo = request.POST.get('modelo')
        texto = request.POST.get('texto')
        id= request.POST.get('id') 

        # Rutas de los modelos
        ruta_modelo_svm = os.path.join(settings.BASE_DIR, "clasificador", "modelos", "modelo_svm_mejorado.pkl")
        ruta_svm_vectores=os.path.join(settings.BASE_DIR, "clasificador", "modelos", "vectorizador_svm.pkl")
        ruta_svm_svd=os.path.join(settings.BASE_DIR, "clasificador", "modelos", "svd.pkl")
        ruta_modelo_redes_neuronales_label = os.path.join(settings.BASE_DIR, "clasificador", "modelos", "label_encoder.pkl")
        ruta_modelo_redes_neuronales_h5 = os.path.join(settings.BASE_DIR, "clasificador", "modelos", "modelo_nn.h5")
        ruta_modelo_random_forest = os.path.join(settings.BASE_DIR, "clasificador", "modelos", "modelo_rf.pkl")
        ruta_vectorizador_random_forest = os.path.join(settings.BASE_DIR, "clasificador", "modelos", "vectorizador_random.pkl")
        ruta_svd_forest = os.path.join(settings.BASE_DIR, "clasificador", "modelos", "svd_random.pkl")


        #cargar modelo svm
        modelo_svm, vectorizador_tfidf = cargar_modelo_svm(ruta_modelo_svm, ruta_svm_vectores)
        svd = joblib.load(ruta_svm_svd)
        #cargar modelo redes
        
        
        if modelo == 'svm':
            
        # No es necesario volver a ajustar el vectorizador TF-IDF
            texto_transformado = vectorizador_tfidf.transform([texto])
    
        # Reducir la dimensionalidad con TruncatedSVD utilizando la misma transformación que se usó durante el entrenamiento
            X_tfidf_svd = svd.transform(texto_transformado)
    
            print(X_tfidf_svd.shape)

    # Realizar la predicción utilizando el modelo SVM y el texto transformado
            categoria = modelo_svm.predict(X_tfidf_svd)

            noticia = Noticia.objects.filter(id=id).first()
            
            
            # Guardar la clasificación en la base de datos
            clasificacion = Clasificacion(modelo=modelo, categoria=categoria, noticia=noticia)
            clasificacion.save()

            # Mapear el número de categoría predicha a un nombre de categoría
            nombres_cat = ['Ciencia y Tecnologia', 'Cultura', 'Deportes', 'Economia',
                           'Educacion', 'Entretenimiento', 'Horoscopo', 'Medioambiente',
                           'Politica', 'Salud']
            categoria_nombre = nombres_cat[int(categoria)]

            # Devolver una respuesta JSON con el resultado de la clasificación
            return JsonResponse({'resultado': categoria_nombre})


        elif modelo == 'redes_neuronales':
                        # Cargar el modelo de redes neuronales
            modelo_redes_neuronales = load_model(ruta_modelo_redes_neuronales_h5)

            # Cargar el LabelEncoder
            label_encoder = joblib.load(ruta_modelo_redes_neuronales_label)

            # Tokenizar el texto
            tokenizer = Tokenizer()
            tokenizer.fit_on_texts([texto])
            sequences = tokenizer.texts_to_sequences([texto])
            X = pad_sequences(sequences, maxlen=MAX_SEQUENCE_LENGTH)

            # Realizar la predicción utilizando el modelo de redes neuronales y el texto
# Realizar la predicción utilizando el modelo de redes neuronales y el texto
            predicted_category = np.argmax(modelo_redes_neuronales.predict(X), axis=-1)
            predicted_category = label_encoder.inverse_transform(predicted_category)[0]

# Devolver una respuesta JSON con el resultado de la clasificación
            return JsonResponse({'resultado': predicted_category})


        elif modelo == 'random_forest':
    # Cargar modelo Random Forest, vectorizador TF-IDF y modelo Truncated SVD
            modelo_random_forest = cargar_modelo_random_forest(ruta_modelo_random_forest)
            vectorizador_tfidf = cargar_vectorizador_tf_idf(ruta_vectorizador_random_forest)
            svd = cargar_modelo_truncated_svd(ruta_svd_forest)

    # Preprocesar el texto con el vectorizador TF-IDF y el modelo Truncated SVD
            texto_transformado = vectorizador_tfidf.transform([texto])
            X_tfidf_svd = svd.transform(texto_transformado)

    # Realizar la predicción utilizando el modelo Random Forest y el texto transformado
            categoria = modelo_random_forest.predict(X_tfidf_svd)

    # Obtener la noticia correspondiente al ID
            noticia = Noticia.objects.filter(id=id).first()

    # Guardar la clasificación en la base de datos
            clasificacion = Clasificacion(modelo=modelo, categoria=categoria, noticia=noticia)
            clasificacion.save()

    # Mapear el número de categoría predicha a un nombre de categoría
            nombres_cat = ['Ciencia y Tecnologia', 'Cultura', 'Deportes', 'Economia',
                   'Educacion', 'Entretenimiento', 'Horoscopo', 'Medioambiente',
                   'Politica', 'Salud']
            categoria_nombre = nombres_cat[int(categoria)]

    # Devolver una respuesta JSON con el resultado de la clasificación
            return JsonResponse({'resultado': categoria_nombre})

        # Manejar el caso en el que se acceda a la vista directamente sin enviar el formulario
    return render(request, 'paginas/clasif_form.html', {'noticia': None, 'modelo': None})