from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Supplier, SupplierStock, EstablishmentStock
from recipes.models import Ingredient

class InventoryViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.supplier = Supplier.objects.create(name='Test Supplier', contact_info='Test Contact')
        self.ingredient = Ingredient.objects.create(name='Test Ingredient')
        self.supplier_stock = SupplierStock.objects.create(
            supplier=self.supplier,
            ingredient=self.ingredient,
            quantity=10,
            unit='kg',
            price=5.00
        )
        self.establishment_stock = EstablishmentStock.objects.create(
            ingredient=self.ingredient,
            quantity=5,
            unit='kg'
        )

    def test_supplier_list_view(self):
        response = self.client.get(reverse('inventory:supplier_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.supplier.name)

    def test_supplier_create_view(self):
        response = self.client.post(reverse('inventory:supplier_create'), {
            'name': 'New Supplier',
            'contact_info': 'New Contact'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Supplier.objects.filter(name='New Supplier').exists())

    def test_supplier_stock_list_view(self):
        response = self.client.get(reverse('inventory:supplier_stock_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.ingredient.name)

    def test_establishment_stock_list_view(self):
        response = self.client.get(reverse('inventory:establishment_stock_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.ingredient.name)
