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
                'precio': float(producto.precio),  # ← Cambiar a float
                'cantidad': 1,
                'imagen': producto.imagen.url,
                'slug': producto.slug,
                'id': producto.id,
            }
            self.guardar()
        else:
            # Si ya existe, aumentamos la cantidad
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
            item_copy = item.copy()
            # Asegurar que precio sea float
            item_copy['precio'] = float(item_copy['precio']) if isinstance(item_copy['precio'], str) else item_copy['precio']
            item_copy['subtotal'] = item_copy['precio'] * item_copy['cantidad']
            yield item_copy

    @property
    def total(self):
        total = 0
        for item in self.carrito.values():
            precio = float(item['precio']) if isinstance(item['precio'], str) else item['precio']
            total += precio * item['cantidad']
        return round(total, 2)

    def aumentar(self, producto):
        id = str(producto.id)
        if id in self.carrito:
            self.carrito[id]['cantidad'] += 1
            self.guardar()

    def disminuir(self, producto):
        id = str(producto.id)
        if id in self.carrito:
            self.carrito[id]['cantidad'] -= 1
            if self.carrito[id]['cantidad'] <= 0:
                self.eliminar(producto)
            else:
                self.guardar()

    def get_item_precio_float(self, item):
        """Método helper para obtener precio como float"""
        return float(item['precio']) if isinstance(item['precio'], str) else item['precio']