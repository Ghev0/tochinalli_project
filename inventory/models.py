from django.db import models
from recipes.models import Ingredient

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_info = models.TextField()

    def __str__(self):
        return self.name

class SupplierStock(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='stock')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='supplier_stock')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} {self.unit} of {self.ingredient.name} from {self.supplier.name}"

class EstablishmentStock(models.Model):
    ingredient = models.OneToOneField(Ingredient, on_delete=models.CASCADE, related_name='establishment_stock')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.quantity} {self.unit} of {self.ingredient.name} in stock"
