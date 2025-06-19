from tienda.models import Producto, Segmento
from django.db.models import Prefetch
from django.core.cache import cache

def obtener_productos_segmentos(limite=9):
    cache_key = f'productos_segmentos_{limite}'
    productos = cache.get(cache_key)
    if productos is not None:
        return productos

    nombres_segmentos = ['Novedades', 'Mas Vendidos', 'Destacados', 'Ofertas']
    productos_prefetch = Prefetch(
        'productos',
        queryset=Producto.objects.all()
    )
    segmentos = Segmento.objects.filter(nombre__in=nombres_segmentos).prefetch_related(productos_prefetch)
    
    productos = {nombre: [] for nombre in nombres_segmentos}
    for segmento in segmentos:
        productos[segmento.nombre] = list(segmento.productos.all()[:limite])
    
    cache.set(cache_key, productos, 60 * 15)  # 15 minutos
    return productos

def obtener_productos_destacados():
    productos = cache.get('productos_destacados')
    if productos is None:
        segmento = Segmento.objects.filter(nombre='Destacados').prefetch_related('productos').first()
        if segmento:
            productos = list(segmento.productos.all())
        else:
            productos = []
        cache.set('productos_destacados', productos, 60 * 15)  # 15 minutos
    return productos