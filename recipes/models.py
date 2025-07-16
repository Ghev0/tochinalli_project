from django.db import models

class Ingredient(models.Model):
    name = models.CharField(max_length=255, unique=True)
    is_commercial = models.BooleanField(default=True) # To distinguish between commercial and elaborated ingredients

    def __str__(self):
        return self.name

class Recipe(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    instructions = models.TextField()
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredient')

    def __str__(self):
        return self.name

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.quantity} {self.unit} of {self.ingredient.name} for {self.recipe.name}"
