from django.contrib import admin
from .models import Producto, Segmento, Categoria, Pedido, PedidoItem

# Register your models here.

class CategoriaAdmin(admin.ModelAdmin):
    # Usamos filter_horizontal para que el campo de productos se vea como un selector de doble panel
    filter_horizontal = ('productos',)
    
class SegmentoAdmin(admin.ModelAdmin):
    # Usamos filter_horizontal para que el campo de productos se vea como un selector de doble panel
    filter_horizontal = ('productos',)
    
class PedidoItemInline(admin.TabularInline):
    model = PedidoItem
    readonly_fields = ('producto', 'cantidad', 'precio_unitario')
    extra = 0    

admin.site.register(Producto) 

admin.site.register(Segmento, SegmentoAdmin)

admin.site.register(Categoria, CategoriaAdmin)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_cliente', 'email', 'total', 'fecha', 'order_id_paypal')
    list_filter = ('fecha',)
    search_fields = ('nombre_cliente', 'email', 'order_id_paypal')
    inlines = [PedidoItemInline]
    readonly_fields = ('nombre_cliente', 'email', 'total', 'order_id_paypal', 'fecha')

@admin.register(PedidoItem)
class PedidoItemAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'producto', 'cantidad', 'precio_unitario')
    readonly_fields = ('pedido', 'producto', 'cantidad', 'precio_unitario')



