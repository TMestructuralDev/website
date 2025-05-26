

class Carrito:
    def __init__(self, request):
        self.session = request.session
        carrito = self.session.get('carrito')
        if not carrito:
            carrito = self.session['carrito'] = {}
        self.carrito = carrito

    def agregar(self, producto):
        id = str(producto.id)
        if id not in self.carrito:
            self.carrito[id] = {
                'nombre': producto.nombre,
                'precio': str(producto.precio),
                'cantidad': 1,
                'imagen': producto.imagen.url,
                'slug': producto.slug,
            }
        else:
            self.carrito[id]['cantidad'] += 1
        self.guardar()

    def eliminar(self, producto):
        id = str(producto.id)
        if id in self.carrito:
            del self.carrito[id]
            self.guardar()

    def limpiar(self):
        self.session['carrito'] = {}
        self.session.modified = True

    def guardar(self):
        self.session['carrito'] = self.carrito
        self.session.modified = True

    def __iter__(self):
        for item in self.carrito.values():
            item['subtotal'] = float(item['precio']) * item['cantidad']
            yield item

    def total(self):
        return sum(float(item['precio']) * item['cantidad'] for item in self.carrito.values())
