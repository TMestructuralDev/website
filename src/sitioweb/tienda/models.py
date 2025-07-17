from django.db import models
from django.utils.text import slugify
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.contrib.auth.models import User

# Create your models here.


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, null=True)  # temporalmente sin unique
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    precio_oferta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,verbose_name="Precio en oferta")
    fecha_fin_oferta = models.DateTimeField(null=True, blank=True, verbose_name="Fin de oferta")
    imagen = models.ImageField(upload_to='productos/')
    descripcion = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:  # Si el slug no está definido
            self.slug = slugify(self.nombre)  # Se genera el slug basado en el nombre del producto
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre
    

class Categoria(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    productos = models.ManyToManyField(Producto, related_name='categoria', blank=True)

    def __str__(self):
        return self.nombre
        
    

class Segmento(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    productos = models.ManyToManyField(Producto, related_name='segmento', blank=True)

    def __str__(self):
        return self.nombre
    

'''Funcion para borrar cache'''
@receiver([post_save, post_delete], sender=Producto)
@receiver([post_save, post_delete], sender=Segmento)
def invalidate_cache(sender, **kwargs):
    cache.delete('productos_destacados')


''' Modelo para pedidos'''    
class Pedido(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    order_id_paypal = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'Pedido {self.id} - {self.nombre_cliente}'


class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.precio_unitario * self.cantidad