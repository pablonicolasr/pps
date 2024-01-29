from django.urls import path
from . import views
from django.conf import settings
from django.contrib.staticfiles.urls import static
from django.urls import re_path
from django.views.generic import RedirectView


urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('noticias/', views.noticias, name='noticias'),
    path('noticias/crear/', views.crear, name='crear'),
    path('noticias/editar/<int:noticia_id>/', views.editar, name='editar'),
    path('noticias/eliminar/<int:id>/', views.eliminar, name='eliminar'),
    path('clasificar/', views.vista_clasificacion, name='vista_clasificacion'),
    path('clasificador/', views.clasificadores, name='clasificador'),
    path('vista-clasificacion/', views.vista_clasificacion, name='vista_clasificacion'),
    re_path(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.ico')),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
