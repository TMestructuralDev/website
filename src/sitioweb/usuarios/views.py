from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import RegistroForm
from django.contrib import messages
from django.contrib.auth import logout
from tienda.models import Pedido
from tienda.cart import Carrito
from django.core.mail import send_mail
from django.utils.timezone import now


def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cuenta creada exitosamente. Ahora puedes iniciar sesión.')
            return redirect('login')
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
    
    form_password = PasswordChangeForm(user=request.user)

    if request.method == 'POST' and 'cambiar_password' in request.POST:
        form_password = PasswordChangeForm(user=request.user, data=request.POST)
        if form_password.is_valid():
            user = form_password.save()
            update_session_auth_hash(request, user)
            send_mail(
                subject='Cambio de contraseña exitoso',
                message=f'Hola {user.first_name},\n\nTu contraseña ha sido cambiada exitosamente el {now().strftime("%d/%m/%Y a las %H:%M")}.\n\nSi no realizaste este cambio, por favor contacta con soporte inmediatamente.',
                from_email=None,
                recipient_list=[user.email],
                fail_silently=False,
            )
            messages.success(request, 'Tu contraseña ha sido cambiada exitosamente.')
            return redirect('perfil')
        else:
            messages.error(request, 'Por favor corrige los errores abajo.')
            
    return render(request, 'perfil/perfil.html', {'pedidos': pedidos, 'carrito_items': productos_carrito, 'total_carrito': carrito.total(), 'form_password': form_password})
