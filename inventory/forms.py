from django import forms
from .models import Supplier, SupplierStock, EstablishmentStock

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_info']

class SupplierStockForm(forms.ModelForm):
    class Meta:
        model = SupplierStock
        fields = ['ingredient', 'quantity', 'unit', 'price']

class EstablishmentStockForm(forms.ModelForm):
    class Meta:
        model = EstablishmentStock
        fields = ['ingredient', 'quantity', 'unit']
