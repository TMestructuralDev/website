from django.urls import path

from . import views

urlpatterns = [
    path('producto/<slug:slug>/', views.producto_detalle, name='producto_detalle'),
    path("", views.listado_productos, name="tienda"),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/eliminar/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
]