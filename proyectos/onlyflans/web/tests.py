from django.contrib.auth.models import User
from django.test import TestCase

from .models import ContactForm, Flan, Testimonio


class VistasPublicasTest(TestCase):
    def setUp(self):
        Flan.objects.create(
            flan_uuid='a1b2c3d4-1111-4a1b-9c1d-000000000001', name='Flan publico',
            description='d', image_url='https://example.com/a.jpg', slug='publico',
            is_private=False, price=3000)
        Flan.objects.create(
            flan_uuid='a1b2c3d4-2222-4a1b-9c1d-000000000002', name='Flan privado',
            description='d', image_url='https://example.com/b.jpg', slug='privado',
            is_private=True, price=3500)

    def test_inicio_muestra_solo_flanes_publicos(self):
        r = self.client.get('/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Flan publico')
        self.assertNotContains(r, 'Flan privado')

    def test_bienvenido_exige_login(self):
        r = self.client.get('/bienvenido')
        self.assertEqual(r.status_code, 302)
        self.assertIn('/accounts/login/', r['Location'])

    def test_bienvenido_muestra_flanes_privados_con_sesion(self):
        User.objects.create_user('demo', password='clave-de-prueba-123')
        self.client.login(username='demo', password='clave-de-prueba-123')
        r = self.client.get('/bienvenido')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Flan privado')

    def test_testimonios(self):
        Testimonio.objects.create(customer_name='Ana', comment='Muy rico', rating=5)
        r = self.client.get('/testimonios')
        self.assertContains(r, 'Muy rico')


class ContactoTest(TestCase):
    def test_formulario_valido_guarda_y_redirige(self):
        r = self.client.post('/contacto', {
            'customer_name': 'Ana', 'customer_email': 'ana@example.com',
            'message': 'Hola'})
        self.assertRedirects(r, '/exito', fetch_redirect_response=False)
        self.assertEqual(ContactForm.objects.count(), 1)

    def test_formulario_invalido_no_guarda(self):
        r = self.client.post('/contacto', {
            'customer_name': 'Ana', 'customer_email': 'no-es-correo', 'message': ''})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(ContactForm.objects.count(), 0)
