from tienda.models import Segmento

def obtener_productos_segmentos():
    nombres_segmentos = ['Novedades', 'Mas Vendidos', 'Destacados', 'Ofertas']
    segmentos = Segmento.objects.filter(nombre__in=nombres_segmentos).prefetch_related('productos')
    
    productos = {nombre: [] for nombre in nombres_segmentos}

    for segmento in segmentos:
        productos[segmento.nombre] = segmento.productos.all()

    return productos

def obtener_productos_destacados():
    segmento = Segmento.objects.filter(nombre='Destacados').prefetch_related('productos').first()
    if segmento:
        return segmento.productos.all()
    return []