from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Recipe, Ingredient

class RecipeViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.recipe = Recipe.objects.create(name='Test Recipe', description='Test Description', instructions='Test Instructions')
        self.ingredient = Ingredient.objects.create(name='Test Ingredient')

    def test_recipe_list_view(self):
        response = self.client.get(reverse('recipes:recipe_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.recipe.name)

    def test_recipe_detail_view(self):
        response = self.client.get(reverse('recipes:recipe_detail', args=[self.recipe.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.recipe.name)

    def test_recipe_create_view(self):
        response = self.client.post(reverse('recipes:recipe_create'), {
            'name': 'New Recipe',
            'description': 'New Description',
            'instructions': 'New Instructions',
            'ingredients-TOTAL_FORMS': '1',
            'ingredients-INITIAL_FORMS': '0',
            'ingredients-MIN_NUM_FORMS': '0',
            'ingredients-MAX_NUM_FORMS': '1000',
            'ingredients-0-ingredient': self.ingredient.pk,
            'ingredients-0-quantity': '1',
            'ingredients-0-unit': 'cup',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Recipe.objects.filter(name='New Recipe').exists())

    def test_recipe_update_view(self):
        response = self.client.post(reverse('recipes:recipe_update', args=[self.recipe.pk]), {
            'name': 'Updated Recipe',
            'description': 'Updated Description',
            'instructions': 'Updated Instructions',
            'ingredients-TOTAL_FORMS': '1',
            'ingredients-INITIAL_FORMS': '0',
            'ingredients-MIN_NUM_FORMS': '0',
            'ingredients-MAX_NUM_FORMS': '1000',
            'ingredients-0-ingredient': self.ingredient.pk,
            'ingredients-0-quantity': '2',
            'ingredients-0-unit': 'cups',
        })
        self.assertEqual(response.status_code, 302)
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.name, 'Updated Recipe')

    def test_recipe_delete_view(self):
        response = self.client.post(reverse('recipes:recipe_delete', args=[self.recipe.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Recipe.objects.filter(pk=self.recipe.pk).exists())
