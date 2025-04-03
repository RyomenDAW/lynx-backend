
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegistroForm


# Create your views here.
def inicio(request):
    return render(request, 'inicio.html')

def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('principal')  # CAMBIA ESTO A TU VISTA PRINCIPAL
    else:
        form = RegistroForm()
    return render(request, 'registration/signup.html', {'form': form})
