from django.contrib import admin
from .models import Producto, Segmento, Categoria, Pedido, PedidoItem, ProductoDetalle

# ---- Inlines ----
class ProductoDetalleInline(admin.StackedInline):
    model = ProductoDetalle
    extra = 0
    can_delete = True
    max_num = 1

    # Muestra un formulario vacío sólo si el producto aún no tiene detalle
    def get_extra(self, request, obj=None, **kwargs):
        if obj and not hasattr(obj, "detalle"):
            return 1
        return 0

class PedidoItemInline(admin.TabularInline):
    model = PedidoItem
    readonly_fields = ('producto', 'cantidad', 'precio_unitario')
    extra = 0

# ---- Admins ----
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'activo', 'fecha_creacion')
    list_filter = ('activo', 'fecha_creacion')
    search_fields = ('nombre', 'slug')
    prepopulated_fields = {"slug": ("nombre",)}
    inlines = [ProductoDetalleInline]

class CategoriaAdmin(admin.ModelAdmin):
    filter_horizontal = ('productos',)

class SegmentoAdmin(admin.ModelAdmin):
    filter_horizontal = ('productos',)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'email', 'total', 'fecha', 'order_id_paypal')
    list_filter = ('fecha',)
    # Si no tienes 'nombre_cliente' en el modelo, usa campos reales:
    search_fields = ('email', 'order_id_paypal', 'usuario__username')
    inlines = [PedidoItemInline]
    readonly_fields = ('usuario', 'email', 'total', 'order_id_paypal', 'fecha')

@admin.register(PedidoItem)
class PedidoItemAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'producto', 'cantidad', 'precio_unitario')
    readonly_fields = ('pedido', 'producto', 'cantidad', 'precio_unitario')

# Registros restantes
admin.site.register(Segmento, SegmentoAdmin)
admin.site.register(Categoria, CategoriaAdmin)

