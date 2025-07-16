from django.shortcuts import render
from .models import InventoryItem

def inventory_list(request):
    inventory_items = InventoryItem.objects.all()
    return render(request, 'inventory/inventory_list.html', {'inventory_items': inventory_items})
