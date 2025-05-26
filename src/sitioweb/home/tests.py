from django.test import TestCase
from django.urls import reverse

# Create your tests here.

class PruebasVistaHome(TestCase):
    def test_vista_home_devuelve_estado_200(self):
        # Verifica que la vista responda correctamente (código 200)
        respuesta = self.client.get(reverse('home'))
        self.assertEqual(respuesta.status_code, 200)

    def test_vista_home_utiliza_template_correcto(self):
        # Verifica que la vista esté usando el template correcto
        respuesta = self.client.get(reverse('home'))
        self.assertTemplateUsed(respuesta, 'home/home.html')
