from .models import Producto

def productos_destacados(request):
    return {
        'productos_destacados': Producto.objects.filter(activo=True)[:6]
    }