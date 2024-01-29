from django.db import models
import joblib
from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler
import numpy as np
import tensorflow.compat.v1 as tf

class InformIngresada(models.Model):
    enlace = models.URLField(null=True)
    texto = models.TextField(null=True)


class Scraping(models.Model):
    titulo = models.TextField(null=True, blank=True)
    caracteres = models.TextField(null=True, blank=True)
    fecha = models.DateField(null=True, blank=True)
    texto = models.TextField(null=True, blank=True)

class Noticia(models.Model):
    TIPO_CHOICES = [
        ('scraping', 'scraping'),
        ('texto', 'texto manual'),
    ]

    enlace = models.URLField(verbose_name="Enlace", null=True, blank=True)
    titulo = models.TextField(verbose_name='Titulo')
    caracteres = models.TextField()
    texto = models.TextField(null=True, blank=True)
    categoria = models.TextField(verbose_name="Categoria", null=True)
    tipo = models.CharField(default='scraping', max_length=20)
    scraping = models.ForeignKey(Scraping, on_delete=models.CASCADE, null=True, blank=True)
    ingresada = models.ForeignKey(InformIngresada, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Enlace: {self.enlace} - Titulo: {self.titulo}"



class Clasificacion(models.Model):
    MODELOS_CHOICES = [
        ('svm', 'SVM (Support Vector Machine)'),
        ('redes_neuronales', 'Redes Neuronales'),
    ]
    CATEGORIA_CHOICES = [
        ('Salud', 'SALUD'),
        ('Deportes', 'DEPORTES'),
        ('Medioambiente', 'MEDIOAMBIENTE'),
        ('Economia', 'ECONOMIA'),
        ('Politica', 'POLITICA'),
        ('Entretenimiento', 'ENTRETENIMIENTO'),
        ('Horoscopo', 'HOROSCOPO'),
        ('Cultura', 'CULTURA'),
        ('Ciencia y Tecnologia', 'CIENCIA Y TECNOLOGIA'),
        ('Educacion', 'EDUCACION'),
        ('Otra', 'OTRA'),
    ]
    modelo = models.CharField(choices=MODELOS_CHOICES, default='svm', max_length=20)
    categoria = models.CharField(choices=CATEGORIA_CHOICES, default='Otra', max_length=20)
    noticia = models.ForeignKey(Noticia, on_delete=models.CASCADE)

# Funciones relacionadas con la clasificación
def cargar_modelo_svm():
    try:
        modelo_svm = joblib.load('modelos/modelo_svm_mejorado.pkl')
        return modelo_svm
    except Exception as e:
        raise Exception(f'Error al cargar modelo SVM: {str(e)}')
    
def cargar_vector_svm():
    try:
        vector_svm = joblib.load('modelos/vectorizador_svm.pkl')
        return vector_svm
    except Exception as e:
        raise Exception(f'Error al cargar modelo SVM: {str(e)}')

def cargar_modelo_red_neuronal():
    try:
        modelo_red_neuronal = load_model('modelos/modelo_redes_alt.h5')
        return modelo_red_neuronal
    except Exception as e:
        raise Exception(f'Error al cargar modelo de red neuronal: {str(e)}')
    
    
def cargar_label_red_neuronal():
    try:
        label_encoder = joblib.load('modelos/label_encoder.pkl')
        return label_encoder
    except Exception as e:
        raise Exception(f'Error al cargar el LabelEncoder: {str(e)}')
    
    
def cargar_modelo_random():
    try:
        modelo_random = joblib.load('modelos/modelo_rf.pkl')
        return modelo_random
    except Exception as e:
        raise Exception(f'Error al cargar el modelo del random forest: {str(e)}')   
    
    
def cargar_vectorizador_random():
    try:
        vectorizador_random = joblib.load('modelos/vectorizador_random.pkl')
        return vectorizador_random
    except Exception as e:
        raise Exception(f'Error al cargar el vector del random: {str(e)}')   
    
    

def cargar_svd_random():
    try:
        svd_random = joblib.load('modelos/svd_random.pkl')
        return svd_random
    except Exception as e:
        raise Exception(f'Error al cargar el svd del random: {str(e)}')   


def preprocesar_datos(datos):
    scaler = StandardScaler()
    datos_preprocesados = scaler.fit_transform([datos])
    return datos_preprocesados
