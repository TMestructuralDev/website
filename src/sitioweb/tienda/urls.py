from django.urls import path

from . import views

urlpatterns = [
    path('producto/<slug:slug>/', views.producto_detalle, name='producto_detalle'),
    path("", views.listado_productos, name="tienda"),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/eliminar/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('actualizar-cantidad/', views.actualizar_cantidad, name='actualizar_cantidad'),
    path('carrito/aumentar/', views.aumentar_cantidad, name='aumentar_cantidad'),
    path('carrito/disminuir/', views.disminuir_cantidad, name='disminuir_cantidad'),
    path('carrito/limpiar/', views.limpiar_carrito, name='limpiar_carrito'),
    path("pago-completado/", views.pago_completado, name="pago_completado"),
    path("gracias/", views.gracias, name="gracias"),
]