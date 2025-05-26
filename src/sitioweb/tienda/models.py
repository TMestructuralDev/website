from django.db import models
from django.utils.text import slugify

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
    

