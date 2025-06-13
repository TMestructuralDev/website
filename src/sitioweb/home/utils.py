from tienda.models import Producto, Segmento
from django.db.models import Prefetch

def obtener_productos_segmentos(limite=9):
    nombres_segmentos = ['Novedades', 'Mas Vendidos', 'Destacados', 'Ofertas']
    
    productos_prefetch = Prefetch(
        'productos',
        queryset=Producto.objects.all()
    )
    
    segmentos = Segmento.objects.filter(nombre__in=nombres_segmentos).prefetch_related(productos_prefetch)
    
    productos = {nombre: [] for nombre in nombres_segmentos}
    
    for segmento in segmentos:
        productos[segmento.nombre] = list(segmento.productos.all()[:limite])
    
    return productos

def obtener_productos_destacados():
    segmento = Segmento.objects.filter(nombre='Destacados').prefetch_related('productos').first()
    if segmento:
        return segmento.productos.all()
    return []