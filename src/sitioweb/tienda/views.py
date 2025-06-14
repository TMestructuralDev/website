from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.http import require_POST
from .models import Producto, Categoria
from home.utils import obtener_productos_destacados
from .cart import Carrito


#from django.http import HttpResponse

# Create your views here.


def producto_detalle(request, slug):
    producto = get_object_or_404(Producto.objects.only("id", "nombre", "slug", "descripcion", "imagen", "precio"),slug=slug)
    productos_destacados = obtener_productos_destacados()
    productos = Producto.objects.only("id", "nombre", "slug", "descripcion", "imagen", "precio")  # Optimización
    context = {
        'productos_destacados': productos_destacados,
        'productos': productos,
        'producto': producto,
    }
    return render(request, 'tienda/producto_detalle.html', context)

def listado_productos(request):
    productos_destacados = obtener_productos_destacados()[:8]
    productos = Producto.objects.only("id", "nombre", "slug", "descripcion", "imagen", "precio")[:12]
    categorias_filtradas = list(map(int, request.GET.getlist("categoria")))
    categorias = Categoria.objects.all()

    if categorias_filtradas:
        productos = Producto.objects.only("id", "nombre", "descripcion", "imagen", "slug").filter(
            categoria__id__in=categorias_filtradas
        ).distinct()
    else:
        productos = Producto.objects.only("id", "nombre", "descripcion", "imagen", "slug")

    context = {
        'productos': productos,
        'productos_destacados': productos_destacados,
        'categorias': categorias,
        'categorias_filtradas': categorias_filtradas,
    }

    return render(request, 'tienda/listado_productos.html', context)

def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = Carrito(request)
    
    if str(producto.id) not in carrito.carrito:
        carrito.agregar(producto)
    
    return redirect('ver_carrito')

def eliminar_del_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = Carrito(request)
    carrito.eliminar(producto)
    return redirect('ver_carrito')

def ver_carrito(request):
    carrito = Carrito(request)
    #for key, item in carrito.carrito.items():
        #print(f"ID en carrito: {item.get('id')} tipo: {type(item.get('id'))}")
    return render(request, 'tienda/carrito.html', {'carrito': carrito})

@csrf_exempt  # solo para desarrollo; en producción usa tokens de seguridad
def actualizar_cantidad(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        producto_id = int(data.get('id'))  # asegúrate que sea int
        cantidad = int(data.get('cantidad'))

        carrito = request.session.get('carrito', {})
        for key, item in carrito.items():
            if int(item['id']) == producto_id:
                item['cantidad'] = max(1, cantidad)  # asegúrate que mínimo sea 1
                item['subtotal'] = round(float(item['precio']) * item['cantidad'], 2)
                break

        request.session['carrito'] = carrito
        return JsonResponse({'status': 'ok', 'cantidad': cantidad})

    return JsonResponse({'status': 'error'}, status=400)

@require_POST
def aumentar_cantidad(request):
    producto_id = request.POST.get('producto_id')
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = Carrito(request)
    carrito.aumentar(producto)
    return redirect('ver_carrito')  # o como se llame tu url para mostrar el carrito

@require_POST
def disminuir_cantidad(request):
    producto_id = request.POST.get('producto_id')
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = Carrito(request)
    carrito.disminuir(producto)
    return redirect('ver_carrito')

def limpiar_carrito(request):
    carrito = Carrito(request)
    carrito.limpiar()
    return redirect('ver_carrito')