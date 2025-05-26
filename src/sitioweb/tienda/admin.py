from django.contrib import admin
from .models import Producto, Segmento, Categoria

# Register your models here.

class CategoriaAdmin(admin.ModelAdmin):
    # Usamos filter_horizontal para que el campo de productos se vea como un selector de doble panel
    filter_horizontal = ('productos',)
    
class SegmentoAdmin(admin.ModelAdmin):
    # Usamos filter_horizontal para que el campo de productos se vea como un selector de doble panel
    filter_horizontal = ('productos',)
    
    

admin.site.register(Producto) 

admin.site.register(Segmento, SegmentoAdmin)

admin.site.register(Categoria, CategoriaAdmin)



