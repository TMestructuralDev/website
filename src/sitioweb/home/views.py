from django.shortcuts import render
#from tienda.models import Segmento
from .utils import obtener_productos_segmentos
#from django.http import HttpResponse

# Create your views here.

def home(request):
    # Llamar a la función para obtener los productos
    productos = obtener_productos_segmentos()

    context = {
        'productos_novedades': productos['Novedades'],
        'productos_mas_vendidos': productos['Mas Vendidos'],
        'productos_ofertas': productos['Ofertas'],
    }

    return render(request, 'home/home.html', context)