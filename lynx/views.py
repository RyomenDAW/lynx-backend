import base64
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from .forms import *
from .models import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.utils import timezone

# Create your views here.
def inicio(request):
    return render(request, 'inicio.html')

def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('inicio')  # CAMBIA ESTO A TU VISTA PRINCIPAL
    else:
        form = RegistroForm()
    return render(request, 'registration/signup.html', {'form': form})



def convertir_imagen_a_base64(imagen):
    """
    Convierte un archivo de imagen (InMemoryUploadedFile) a una cadena base64 con su content_type.
    """
    content_type = imagen.content_type  # 'image/png' o 'image/jpeg'
    imagen_base64 = base64.b64encode(imagen.read()).decode('utf-8')
    return f'data:{content_type};base64,{imagen_base64}'


from .models import Videojuego, Biblioteca

def lista_videojuegos(request):
    juegos = Videojuego.objects.all()

    juegos_comprados = set()
    if request.user.is_authenticated:
        juegos_comprados = set(
            Biblioteca.objects.filter(usuario=request.user).values_list('juego_id', flat=True)
        )

    return render(request, 'videojuegos/lista.html', {
        'juegos': juegos,
        'juegos_comprados': juegos_comprados
    })



def crear_videojuego(request):
    if not request.user.is_authenticated or request.user.rol not in ['ADMIN', 'DIST']:
        return HttpResponseForbidden("No tienes permisos para añadir videojuegos.")

    if request.method == 'POST':
        form = VideojuegoForm(request.POST, request.FILES)
        if form.is_valid():
            videojuego = form.save(commit=False)
            imagen = request.FILES.get('imagen')
            if imagen:
                videojuego.set_imagen_portada_from_file(imagen)
            videojuego.save()
            return redirect('lista_videojuegos')
    else:
        form = VideojuegoForm()

    return render(request, 'videojuegos/formulario.html', {'form': form, 'modo': 'Crear'})


def editar_videojuego(request, id):
    if not request.user.is_authenticated or request.user.rol not in ['ADMIN', 'DIST']:
        return HttpResponseForbidden("No tienes permisos para editar videojuegos.")

    videojuego = get_object_or_404(Videojuego, pk=id)

    if request.method == 'POST':
        form = VideojuegoForm(request.POST, request.FILES, instance=videojuego)
        if form.is_valid():
            videojuego = form.save(commit=False)
            imagen = request.FILES.get('imagen')
            if imagen:
                videojuego.set_imagen_portada_from_file(imagen)
            videojuego.save()
            return redirect('lista_videojuegos')
    else:
        form = VideojuegoForm(instance=videojuego)

    return render(request, 'videojuegos/formulario.html', {'form': form, 'modo': 'Editar'})



def eliminar_videojuego(request, id):
    if not request.user.is_authenticated or request.user.rol not in ['ADMIN', 'DIST']:
        return HttpResponseForbidden("No tienes permisos para eliminar videojuegos.")

    juego = get_object_or_404(Videojuego, id=id)
    if request.method == 'POST':
        juego.delete()
        return redirect('lista_videojuegos')
    return render(request, 'videojuegos/eliminar.html', {'juego': juego})


#==============================================================================================

# VER BIBLIOTECA
@login_required
def biblioteca_usuario(request):
    juegos = Biblioteca.objects.filter(usuario=request.user)
    return render(request, 'biblioteca/lista.html', {'juegos': juegos})


# COMPRAR UN JUEGO
@login_required
def comprar_videojuego(request, id):
    juego = get_object_or_404(Videojuego, pk=id)

    # Comprobamos si ya lo tiene
    ya_comprado = Biblioteca.objects.filter(usuario=request.user, juego=juego).exists()
    if not ya_comprado:
        Biblioteca.objects.create(usuario=request.user, juego=juego)

    return redirect('lista_videojuegos')

# MARCAR COMO FAVORITO
@login_required
def marcar_favorito(request, biblioteca_id):
    registro = get_object_or_404(Biblioteca, id=biblioteca_id, usuario=request.user)
    registro.favorito = not registro.favorito
    registro.save()
    return redirect('biblioteca')


# ELIMINAR DE LA BIBLIOTECA
@login_required
def eliminar_de_biblioteca(request, biblioteca_id):
    registro = get_object_or_404(Biblioteca, id=biblioteca_id, usuario=request.user)
    if request.method == 'POST':
        registro.delete()
    return redirect('biblioteca')

from django.views.decorators.http import require_POST

@login_required
@require_POST
def añadir_tiempo_jugado(request, biblioteca_id):
    registro = get_object_or_404(Biblioteca, id=biblioteca_id, usuario=request.user)
    minutos = int(request.POST.get('minutos', 0))
    if minutos > 0:
        registro.tiempo_jugado += minutos
        registro.save()
    return redirect('biblioteca')



@login_required
def crear_reseña(request, juego_id):
    juego = get_object_or_404(Videojuego, pk=juego_id)

    # Solo si el usuario tiene ese juego en su biblioteca
    if not Biblioteca.objects.filter(usuario=request.user, juego=juego).exists():
        return HttpResponseForbidden("No puedes reseñar un juego que no tienes.")

    # Evitar múltiples reseñas por el mismo usuario al mismo juego
    if Reseña.objects.filter(usuario=request.user, juego=juego).exists():
        return redirect('lista_videojuegos')  # o mostrar mensaje

    if request.method == 'POST':
        form = ReseñaForm(request.POST)
        if form.is_valid():
            reseña = form.save(commit=False)
            reseña.usuario = request.user
            reseña.juego = juego
            reseña.save()
            return redirect('biblioteca')
    else:
        form = ReseñaForm()

    return render(request, 'reseñas/formulario.html', {'form': form, 'juego': juego})



def ver_reseñas(request, juego_id):
    juego = get_object_or_404(Videojuego, pk=juego_id)
    reseñas = Reseña.objects.filter(juego=juego).order_by('-fecha')
    return render(request, 'reseñas/lista.html', {
        'juego': juego,
        'reseñas': reseñas
    })


@login_required
def editar_reseña(request, id):
    reseña = get_object_or_404(Reseña, pk=id, usuario=request.user)

    if request.method == 'POST':
        form = ReseñaForm(request.POST, instance=reseña)
        if form.is_valid():
            form.save()
            return redirect('ver_reseñas', juego_id=reseña.juego.id)
    else:
        form = ReseñaForm(instance=reseña)

    return render(request, 'reseñas/formulario.html', {
        'form': form,
        'juego': reseña.juego,
        'modo': 'Editar'
    })

@login_required
def eliminar_reseña(request, id):
    reseña = get_object_or_404(Reseña, pk=id, usuario=request.user)

    if request.method == 'POST':
        reseña.delete()
        return redirect('ver_reseñas', juego_id=reseña.juego.id)

    return render(request, 'reseñas/eliminar.html', {'reseña': reseña})


def es_admin_o_dist(user):
    return user.is_authenticated and user.rol in ['ADMIN', 'DIST']

@login_required
def lista_codigos(request):
    codigos = CodigoPromocional.objects.all()
    return render(request, 'codigos/lista.html', {'codigos': codigos})

@user_passes_test(es_admin_o_dist)
def crear_codigo(request):
    if request.method == 'POST':
        form = CodigoPromocionalForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_codigos')
    else:
        form = CodigoPromocionalForm()
    return render(request, 'codigos/formulario.html', {'form': form, 'modo': 'Crear'})

@user_passes_test(es_admin_o_dist)
def editar_codigo(request, id):
    codigo = get_object_or_404(CodigoPromocional, id=id)
    if request.method == 'POST':
        form = CodigoPromocionalForm(request.POST, instance=codigo)
        if form.is_valid():
            form.save()
            return redirect('lista_codigos')
    else:
        form = CodigoPromocionalForm(instance=codigo)
    return render(request, 'codigos/formulario.html', {'form': form, 'modo': 'Editar'})

@user_passes_test(es_admin_o_dist)
def eliminar_codigo(request, id):
    codigo = get_object_or_404(CodigoPromocional, id=id)
    if request.method == 'POST':
        codigo.delete()
        return redirect('lista_codigos')
    return render(request, 'codigos/eliminar.html', {'codigo': codigo})


from django.http import JsonResponse

@login_required
def canjear_codigo(request):
    mensaje = None

    if request.method == 'POST':
        codigo_texto = request.POST.get('codigo').strip()
        try:
            codigo = CodigoPromocional.objects.get(codigo_texto=codigo_texto)

            if codigo.usado or codigo.usos_actuales >= codigo.usos_totales:
                mensaje = "❌ Este código ya ha sido utilizado al máximo."
            elif codigo.fecha_expiracion < timezone.now().date():
                mensaje = "❌ Este código ha expirado."
            else:
                # AÑADIR JUEGO
                if codigo.videojuego:
                    existe = Biblioteca.objects.filter(usuario=request.user, juego=codigo.videojuego).exists()
                    if not existe:
                        Biblioteca.objects.create(usuario=request.user, juego=codigo.videojuego)

                # AÑADIR SALDO
                if codigo.saldo_extra:
                    request.user.saldo_virtual += codigo.saldo_extra
                    request.user.save()  # ✅ IMPORTANTE

                # ACTUALIZAR USOS
                codigo.usos_actuales += 1
                if codigo.usos_actuales >= codigo.usos_totales:
                    codigo.usado = True
                codigo.save()

                mensaje = f"✅ Código canjeado correctamente ({codigo.usos_actuales}/{codigo.usos_totales})"

        except CodigoPromocional.DoesNotExist:
            mensaje = "❌ Código no válido."

    return render(request, 'codigos/canjear.html', {'mensaje': mensaje})


@login_required
def perfil_usuario(request):
    return render(request, 'perfil/perfil.html')
