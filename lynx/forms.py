from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *

class RegistroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'rol', 'password1', 'password2']
        widgets = {
            'rol': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super(RegistroForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = "Nombre de usuario"
        self.fields['email'].label = "Correo electrónico"
        self.fields['password1'].label = "Contraseña"
        self.fields['password2'].label = "Repite la contraseña"
        self.fields['rol'].label = "Rol en la plataforma"

        # AÑADIMOS CLASES BOOTSTRAP
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        
        
        

class VideojuegoForm(forms.ModelForm):
    imagen = forms.FileField(
        required=False,
        label='Imagen de portada (JPG o PNG)',
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Videojuego
        fields = [
            'titulo', 'descripcion', 'genero', 'precio',
            'desarrollador', 'distribuidor',
            'requisitos_minimos', 'requisitos_recomendados',
            'soporte_mando', 'fecha_lanzamiento',
            'disponible'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'genero': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'desarrollador': forms.TextInput(attrs={'class': 'form-control'}),
            'distribuidor': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'requisitos_minimos': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'requisitos_recomendados': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'fecha_lanzamiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'soporte_mando': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'titulo': 'Título',
            'descripcion': 'Descripción',
            'genero': 'Género',
            'precio': 'Precio (€)',
            'desarrollador': 'Desarrollador',
            'distribuidor': 'Distribuidor',
            'requisitos_minimos': 'Requisitos mínimos',
            'requisitos_recomendados': 'Requisitos recomendados',
            'soporte_mando': '¿Soporta mando?',
            'fecha_lanzamiento': 'Fecha de lanzamiento',
            'disponible': '¿Está disponible?'
        }

    # VALIDACIONES PERSONALIZADAS
    def clean_precio(self):
        precio = self.cleaned_data['precio']
        if precio < 0:
            raise forms.ValidationError("El precio no puede ser negativo.")
        return precio

    def clean_titulo(self):
        titulo = self.cleaned_data['titulo']
        if len(titulo.strip()) < 3:
            raise forms.ValidationError("El título debe tener al menos 3 caracteres.")
        return titulo

    def save(self, commit=True):
        instancia = super().save(commit=False)
        imagen = self.cleaned_data.get('imagen')

        if imagen:
            instancia.set_imagen_portada_from_file(imagen)

        if commit:
            instancia.save()

        return instancia



class ReseñaForm(forms.ModelForm):
    class Meta:
        model = Reseña
        fields = ['puntuacion', 'comentario']
        widgets = {
            'puntuacion': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 10}),
            'comentario': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'puntuacion': 'Puntuación (0-10)',
            'comentario': 'Comentario',
        }


class CodigoPromocionalForm(forms.ModelForm):
    class Meta:
        model = CodigoPromocional
        fields = [
            'codigo_texto', 'descripcion',
            'videojuego', 'saldo_extra',
            'usos_totales', 'fecha_expiracion'
        ]
        widgets = {
            'codigo_texto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'AAAA-BBBB-DDDD'  # PLACEHOLDER
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2
            }),
            'videojuego': forms.Select(attrs={
                'class': 'form-select'
            }),
            'saldo_extra': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'usos_totales': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'fecha_expiracion': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }



class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'avatar_base64']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
