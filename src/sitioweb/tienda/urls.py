from django.urls import path

from . import views

urlpatterns = [
    path('producto/<slug:slug>/', views.producto_detalle, name='producto_detalle'),
    path("", views.listado_productos, name="tienda"),
]