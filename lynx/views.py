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


@login_required
def editar_perfil(request):
    usuario = request.user
    avatar_original = usuario.avatar_base64  # ← GUARDAMOS EL AVATAR ACTUAL

    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, request.FILES, instance=usuario)

        if form.is_valid():
            avatar = request.FILES.get('avatar')

            if avatar:
                usuario.set_avatar_from_file(avatar)
            else:
                usuario.avatar_base64 = avatar_original  # ← RESTAURAMOS EL AVATAR ORIGINAL

            form.save()  # ← AHORA SÍ, sin que se borre el campo

            return redirect('perfil_usuario')
    else:
        form = EditarPerfilForm(instance=usuario)

    return render(request, 'perfil/editar_perfil.html', {'form': form})



import requests
from django.contrib import messages

import requests
from django.contrib import messages
from django.shortcuts import redirect
from .models import Videojuego
from datetime import datetime

import requests
from django.contrib import messages
from django.shortcuts import redirect
from .models import Videojuego
from datetime import datetime

def importar_desde_steam(request):
    if request.method == 'POST' and request.user.is_authenticated and request.user.rol in ['ADMIN', 'DIST']:
        nombre_juego = request.POST.get('nombre_juego')
        # 1. Buscar AppID a partir del nombre del juego
        lista_url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
        lista_respuesta = requests.get(lista_url)

        if lista_respuesta.status_code != 200:
            messages.error(request, "No se pudo acceder al listado de juegos de Steam.")
            return redirect('lista_videojuegos')

        juegos = lista_respuesta.json().get("applist", {}).get("apps", [])
        nombre_juego = request.POST.get('nombre_juego', '').strip().lower()
        
        nombre_juego = request.POST.get('nombre_juego', '').strip().lower()


        import unicodedata

        # FUNCION AUXILIAR PARA NORMALIZAR TEXTO (sin acentos ni símbolos raros)
        def normalizar(texto):
            texto = texto.strip().lower()
            texto = unicodedata.normalize("NFKD", texto)
            texto = "".join(c for c in texto if not unicodedata.combining(c))
            return texto.replace("™", "").replace("®", "").strip()

        # Normalizamos el nombre introducido
        nombre_normalizado = normalizar(nombre_juego)

        # ==============================================
        # CASO 1: Coincidencia exacta del nombre completo
        # Ejemplo: "portal" == "portal"
        # ==============================================
        juego_encontrado = next(
            (j for j in juegos if normalizar(j["name"]) == nombre_normalizado),
            None
        )

        # =====================================================
        # CASO 2: Comienza por el nombre buscado
        # Ejemplo: "rocket" encuentra "Rocket League®"
        # =====================================================
        if not juego_encontrado:
            juego_encontrado = next(
                (j for j in juegos if normalizar(j["name"]).startswith(nombre_normalizado)),
                None
            )

        # =============================================================
        # CASO 3: Coincidencia parcial (en cualquier parte del título)
        # Ejemplo: "dota" encuentra "Dota 2 - Reborn Update"
        # =============================================================
        if not juego_encontrado:
            juego_encontrado = next(
                (j for j in juegos if nombre_normalizado in normalizar(j["name"])),
                None
            )

        appid = juego_encontrado["appid"]

        # 2. Usar tu importador de siempre con ese appid
        url = f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=es&l=spanish"
        response = requests.get(url)

        if response.status_code != 200:
            messages.error(request, "Error al conectar con la API de Steam.")
            return redirect('lista_videojuegos')

        data = response.json()
        juego_data = data.get(str(appid), {}).get('data', {})

        if not data.get(str(appid), {}).get('success') or not juego_data:
            messages.error(request, "No se pudo obtener información del juego.")
            return redirect('lista_videojuegos')

        # Evitar duplicados por título
        if Videojuego.objects.filter(titulo__iexact=juego_data.get('name')).exists():
            messages.warning(request, f'El juego "{juego_data.get("name")}" ya existe en la tienda.')
            return redirect('lista_videojuegos')

        # Extraer y mapear los datos
        titulo = juego_data.get('name', 'Sin título')
        descripcion = juego_data.get('short_description', 'Sin descripción')
        genero = ', '.join([g['description'] for g in juego_data.get('genres', [])]) if juego_data.get('genres') else 'Desconocido'
        desarrollador = juego_data.get('developers', ['Desconocido'])[0]
        distribuidor = juego_data.get('publishers', ['Desconocido'])[0]
        requisitos_min = juego_data.get('pc_requirements', {}).get('minimum', 'No especificado')
        requisitos_rec = juego_data.get('pc_requirements', {}).get('recommended', 'No especificado')
        soporte_mando = juego_data.get('controller_support', None) is not None

        precio_raw = juego_data.get('price_overview', {}).get('final')
        precio = precio_raw / 100 if precio_raw else 0.00

        try:
            fecha_str = juego_data['release_date']['date']
            fecha = datetime.strptime(fecha_str, '%d %b, %Y').date()
        except:
            fecha = datetime.today().date()

        nuevo = Videojuego(
            titulo=titulo,
            descripcion=descripcion,
            genero=genero,
            precio=precio,
            desarrollador=desarrollador,
            distribuidor=distribuidor,
            requisitos_minimos=requisitos_min,
            requisitos_recomendados=requisitos_rec,
            soporte_mando=soporte_mando,
            fecha_lanzamiento=fecha,
            disponible=True
        )

        imagen_url = juego_data.get('header_image')
        if imagen_url:
            img_response = requests.get(imagen_url)
            if img_response.status_code == 200:
                nuevo.set_imagen_portada_from_response(img_response)

        nuevo.save()
        messages.success(request, f'Videojuego "{titulo}" importado correctamente.')
        return redirect('lista_videojuegos')


def detalle_videojuego(request, id):
    juego = get_object_or_404(Videojuego, pk=id)
    return render(request, 'videojuegos/detalle.html', {'juego': juego})


from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model

from django.db.models import F

@user_passes_test(lambda u: u.is_authenticated and u.rol == 'ADMIN')
def ver_usuarios(request):
    User = get_user_model()
    sort = request.GET.get('sort', 'username')
    direction = request.GET.get('dir', 'asc')

    if sort not in ['id', 'username', 'email', 'rol', 'date_joined', 'saldo_virtual', 'reputacion']:
        sort = 'username'

    if direction == 'desc':
        sort = f"-{sort}"

    usuarios = User.objects.all().order_by(sort)
    return render(request, 'usuarios/lista.html', {
        'usuarios': usuarios,
        'sort': request.GET.get('sort', ''),
        'dir': direction
    })


@user_passes_test(lambda u: u.is_authenticated and u.rol == 'ADMIN')
@require_POST
def eliminar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    if usuario != request.user:  
        usuario.delete()
    return redirect('ver_usuarios')




from django.db.models import Q

@login_required
def ver_amigos(request):
    user = request.user
    amistades = Amistad.objects.filter(
        Q(solicitante=user) | Q(receptor=user),
        aceptada=True
    )

    amigos = []
    for amistad in amistades:
        if amistad.solicitante == user:
            amigos.append(amistad.receptor)
        else:
            amigos.append(amistad.solicitante)

    return render(request, 'social/amigos.html', {'amigos': amigos})

@login_required
def eliminar_amigo(request, id):
    amigo = get_object_or_404(Usuario, pk=id)
    Amistad.objects.filter(
        Q(solicitante=request.user, receptor=amigo) | Q(solicitante=amigo, receptor=request.user)
    ).delete()
    return redirect('ver_amigos')
