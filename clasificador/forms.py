from django import forms
from .models import Noticia


class NoticiaForm(forms.ModelForm):
    class Meta:
        model = Noticia
        fields = ['enlace', 'titulo', 'caracteres', 'texto', 'categoria']

