from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.conf import settings
import json
import requests

from .models import Producto, Categoria, Pedido, PedidoItem
from home.utils import obtener_productos_destacados
from .cart import Carrito


# Create your views here.


def producto_detalle(request, slug):
    producto = get_object_or_404(Producto.objects.only("id", "nombre", "slug", "descripcion", "imagen", "precio"),slug=slug)
    productos_destacados = obtener_productos_destacados()
    productos = Producto.objects.only("id", "nombre", "slug", "descripcion", "imagen", "precio")  # Optimización
    context = {
        #'productos_destacados': productos_destacados,#
        'productos': productos,
        'producto': producto,
    }
    return render(request, 'tienda/producto_detalle.html', context)

def listado_productos(request):
    productos_destacados = obtener_productos_destacados()[:8]
    productos = Producto.objects.only("id", "nombre", "slug", "descripcion", "imagen", "precio")[:12]
    categorias_filtradas = list(map(int, request.GET.getlist("categoria")))
    categorias = Categoria.objects.all()

    if categorias_filtradas:
        productos = Producto.objects.only("id", "nombre", "descripcion", "imagen", "slug").filter(
            categoria__id__in=categorias_filtradas
        ).distinct()
    else:
        productos = Producto.objects.only("id", "nombre", "descripcion", "imagen", "slug")

    context = {
        'productos': productos,
        #'productos_destacados': productos_destacados,#
        'categorias': categorias,
        'categorias_filtradas': categorias_filtradas,
    }

    return render(request, 'tienda/listado_productos.html', context)

def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = Carrito(request)
    
    if str(producto.id) not in carrito.carrito:
        carrito.agregar(producto)
    
    return redirect('ver_carrito')

def eliminar_del_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = Carrito(request)
    carrito.eliminar(producto)
    return redirect('ver_carrito')

def ver_carrito(request):
    carrito = Carrito(request)
    
    context = {
        'carrito': carrito,
        'total_carrito': carrito.total,
        'PAYPAL_CLIENT_ID': settings.PAYPAL_CLIENT_ID, 
    }
    return render(request, 'tienda/carrito.html', context)

@require_POST
def limpiar_carrito(request):
    carrito = Carrito(request)
    carrito.limpiar()
    return JsonResponse({
        "status": "ok",
        "total": 0.00
    })


@require_POST
def aumentar_cantidad(request):
    producto_id = request.POST.get('producto_id')
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = Carrito(request)
    carrito.aumentar(producto)
    return redirect('ver_carrito')  # o como se llame tu url para mostrar el carrito

@require_POST
def disminuir_cantidad(request):
    producto_id = request.POST.get('producto_id')
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = Carrito(request)
    carrito.disminuir(producto)
    return redirect('ver_carrito')

def actualizar_cantidad(request, producto_id, cantidad):
    carrito = Carrito(request)
    cantidad = int(cantidad)
    producto = get_object_or_404(Producto, id=producto_id)

    if cantidad <= 0:
        carrito.eliminar(producto)
        subtotal = 0
    else:
        if str(producto_id) in carrito.carrito:
            carrito.carrito[str(producto_id)]["cantidad"] = cantidad
            carrito.guardar()
        subtotal = float(carrito.carrito[str(producto_id)]["precio"]) * cantidad if str(producto_id) in carrito.carrito else 0

    total = carrito.total
    return JsonResponse({
        "subtotal": round(subtotal, 2),
        "total": round(total, 2),
    })

def get_paypal_access_token():
    """Obtiene token de acceso de PayPal usando client_id y secret del sandbox."""
    try:
        # Verificar que las credenciales estén configuradas
        if not settings.PAYPAL_CLIENT_ID or not settings.PAYPAL_SECRET:
            print("Error: Credenciales de PayPal no configuradas")
            return None
            
        resp = requests.post(
            f"{settings.PAYPAL_API_URL}/v1/oauth2/token",
            data={"grant_type": "client_credentials"},
            auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_SECRET),
            headers={'Accept': 'application/json', 'Accept-Language': 'en_US'},
            timeout=30  # Timeout para evitar colgarse
        )
        resp.raise_for_status()
        
        token_data = resp.json()
        token = token_data.get("access_token")
        
        if not token:
            print("Error: No se recibió access_token en la respuesta de PayPal")
            return None
            
        print("Access Token PayPal obtenido exitosamente")
        return token
        
    except requests.exceptions.Timeout:
        print("Error: Timeout conectando con PayPal")
        return None
    except requests.exceptions.ConnectionError:
        print("Error: No se pudo conectar con PayPal")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"Error HTTP de PayPal: {e}")
        print(f"Respuesta: {e.response.text if e.response else 'No response'}")
        return None
    except requests.RequestException as e:
        print(f"Error obteniendo token PayPal: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado obteniendo token PayPal: {e}")
        return None
    
@csrf_exempt
def pago_completado(request):
    """Confirma pago desde PayPal y crea Pedido y PedidoItems."""
    try:
        print("=== DEBUG: Iniciando pago_completado ===")
        
        if request.method != "POST":
            print("ERROR: Método no es POST")
            return JsonResponse({"status": "error", "message": "Método no permitido"}, status=405)

        if not request.user.is_authenticated:
            print("ERROR: Usuario no autenticado")
            return JsonResponse({"status": "error", "message": "Usuario no autenticado"}, status=403)
        
        print(f"DEBUG: Usuario autenticado: {request.user.username}")

        # Parsear body
        try:
            print(f"DEBUG: Request body: {request.body}")
            data = json.loads(request.body)
            order_id = data.get("orderID")
            print(f"DEBUG: Order ID recibido: {order_id}")
            if not order_id:
                return JsonResponse({"status": "error", "message": "Falta orderID"}, status=400)
        except json.JSONDecodeError as e:
            print(f"ERROR: JSON inválido: {e}")
            return JsonResponse({"status": "error", "message": "JSON inválido"}, status=400)

        # Obtener token PayPal con mejor manejo de errores
        print("DEBUG: Obteniendo token de PayPal...")
        access_token = get_paypal_access_token()
        if not access_token:
            print("ERROR: No se pudo obtener token de PayPal")
            return JsonResponse({"status": "error", "message": "No se pudo obtener token de PayPal"}, status=500)
        
        print("DEBUG: Token obtenido exitosamente")

        # Validar pago con PayPal
        try:
            print(f"DEBUG: Consultando orden PayPal: {order_id}")
            print(f"DEBUG: URL: {settings.PAYPAL_API_URL}/v2/checkout/orders/{order_id}")
            
            resp = requests.get(
                f"{settings.PAYPAL_API_URL}/v2/checkout/orders/{order_id}",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            print(f"DEBUG: Status code PayPal: {resp.status_code}")
            print(f"DEBUG: Response PayPal: {resp.text[:500]}...")  # Primeros 500 chars
            
            resp.raise_for_status()
            order_data = resp.json()
            print(f"DEBUG: Orden status: {order_data.get('status')}")
            
        except requests.RequestException as e:
            print(f"ERROR: Exception consultando PayPal: {str(e)}")
            return JsonResponse({"status": "error", "message": f"Error consultando PayPal: {str(e)}"}, status=500)

        if order_data.get("status") != "COMPLETED":
            print(f"ERROR: Pago no completado. Status: {order_data.get('status')}")
            return JsonResponse({"status": "error", "message": "Pago no confirmado"}, status=400)

        print("DEBUG: Pago confirmado, procesando datos...")

        # Datos del pagador con validación
        payer = order_data.get("payer", {})
        nombre_completo = payer.get("name", {})
        nombre_cliente = (nombre_completo.get("given_name", "") + " " + nombre_completo.get("surname", "")).strip()
        email = payer.get("email_address", "")
        
        print(f"DEBUG: Payer data: {payer}")
        print(f"DEBUG: Nombre cliente: {nombre_cliente}")
        print(f"DEBUG: Email: {email}")
        
        # Si no hay nombre, usar el username del usuario autenticado
        if not nombre_cliente:
            nombre_cliente = request.user.get_full_name() or request.user.username
            print(f"DEBUG: Usando nombre de usuario: {nombre_cliente}")

        # Usar la clase Carrito consistentemente
        carrito = Carrito(request)
        print(f"DEBUG: Carrito items: {len(carrito.carrito)}")
        
        if not carrito.carrito:
            print("ERROR: Carrito vacío")
            return JsonResponse({"status": "error", "message": "Carrito vacío"}, status=400)

        # Usar la propiedad total que ya maneja la conversión correctamente
        total = carrito.total
        print(f"DEBUG: Total calculado: {total}")

        print("DEBUG: Creando pedido en base de datos...")

        # Crear Pedido
        pedido = Pedido.objects.create(
            usuario=request.user,
            nombre_cliente=nombre_cliente,
            email=email,
            total=total,
            order_id_paypal=order_id
        )
        print(f"DEBUG: Pedido creado con ID: {pedido.id}")

        # Crear items del pedido
        items_creados = 0
        for producto_id, item in carrito.carrito.items():
            try:
                producto = Producto.objects.get(id=item["id"])
                PedidoItem.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=item["cantidad"],
                    precio_unitario=float(item["precio"])  # Convertir string a float
                )
                items_creados += 1
                print(f"DEBUG: Item creado para producto {producto.nombre}")
            except Producto.DoesNotExist:
                # Log del producto no encontrado pero continúa
                print(f"ERROR: Producto con ID {item['id']} no encontrado")
                continue
            except ValueError as e:
                # Error de conversión de precio
                print(f"ERROR: Error convirtiendo precio del producto {item['id']}: {e}")
                continue

        print(f"DEBUG: Total items creados: {items_creados}")

        # Limpiar carrito usando el método de la clase
        carrito.limpiar()
        print("DEBUG: Carrito limpiado")

        print("DEBUG: Proceso completado exitosamente")

        return JsonResponse({
            "status": "ok",
            "pedido_id": pedido.id,
            "message": "Pedido creado exitosamente"
        })

    except Exception as e:
        # Log del error completo para debugging
        import traceback
        error_traceback = traceback.format_exc()
        print(f"=== ERROR COMPLETO ===")
        print(error_traceback)
        print(f"=== FIN ERROR ===")
        return JsonResponse({"status": "error", "message": f"Error interno: {str(e)}"}, status=500)

'''Vista del template gracias al confirmar compra'''
def gracias(request):
    return render(request, "tienda/gracias.html")


'''Motor de busqueda'''
def autocompletar_productos(request):
    term = request.GET.get("term", "")
    productos = Producto.objects.filter(nombre__icontains=term)[:5]
    resultados = [
        {
            "nombre": p.nombre,
            "url": reverse("producto_detalle", kwargs={"slug": p.slug})
        } for p in productos
    ]
    return JsonResponse(resultados, safe=False)

def buscar_producto(request):
    query = request.GET.get("q", "").strip()
    producto = Producto.objects.filter(nombre__icontains=query).first()
    if producto:
        return redirect("producto_detalle", slug=producto.slug)
    return redirect("tienda")