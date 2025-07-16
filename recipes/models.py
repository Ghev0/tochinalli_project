from django.db import models

class Recipe(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    instructions = models.TextField()

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    name = models.CharField(max_length=255)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    quantity = models.CharField(max_length=100)

    def __str__(self):
        return self.name
