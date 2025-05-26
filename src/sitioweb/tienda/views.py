from django.shortcuts import render, get_object_or_404
from .models import Producto, Categoria
from home.utils import obtener_productos_destacados

#from django.http import HttpResponse

# Create your views here.


def producto_detalle(request, slug):
    producto = get_object_or_404(Producto.objects.only("id", "nombre", "slug", "descripcion", "imagen"), slug=slug)
    productos_destacados = obtener_productos_destacados()
    productos = Producto.objects.only("id", "nombre", "slug")  # Optimización
    context = {
        'productos_destacados': productos_destacados,
        'productos': productos,
        'producto': producto,
    }
    return render(request, 'tienda/producto_detalle.html', context)

def listado_productos(request):
    productos_destacados = obtener_productos_destacados()
    categorias = Categoria.objects.only("id", "nombre")
    categorias_filtradas = list(map(int, request.GET.getlist("categoria")))

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