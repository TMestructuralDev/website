from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import RegistroForm
from django.contrib import messages
from django.contrib.auth import logout
from tienda.models import Pedido
from tienda.cart import Carrito


def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cuenta creada exitosamente. Ahora puedes iniciar sesión.')
            return redirect('usuarios/login.html')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

'''def perfil(request):  
    return render(request, 'perfil/perfil.html') '''
    
    
@login_required
def editar_datos(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        user.email = request.POST['email']
        user.save()
        messages.success(request, 'Datos actualizados correctamente.')
        return redirect('perfil')
    
@login_required
def perfil(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha')
    carrito = Carrito(request)
    productos_carrito = list(carrito) 
    return render(request, 'perfil/perfil.html', {'pedidos': pedidos, 'carrito_items': productos_carrito, 'total_carrito': carrito.total()})