from django.shortcuts import render
from .models import SupplierStock, EstablishmentStock

def inventory_list(request):
    supplier_stock = SupplierStock.objects.all()
    establishment_stock = EstablishmentStock.objects.all()
    context = {
        'supplier_stock': supplier_stock,
        'establishment_stock': establishment_stock,
    }
    return render(request, 'inventory/inventory_list.html', context)
