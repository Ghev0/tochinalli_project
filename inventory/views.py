from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Supplier, SupplierStock, EstablishmentStock
from .forms import SupplierForm, SupplierStockForm, EstablishmentStockForm

# Supplier Views
class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = 'inventory/supplier_list.html'
    context_object_name = 'suppliers'

class SupplierCreateView(LoginRequiredMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('inventory:supplier_list')

class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('inventory:supplier_list')

# SupplierStock Views
class SupplierStockListView(LoginRequiredMixin, ListView):
    model = SupplierStock
    template_name = 'inventory/supplier_stock_list.html'
    context_object_name = 'supplier_stock'

class SupplierStockCreateView(LoginRequiredMixin, CreateView):
    model = SupplierStock
    form_class = SupplierStockForm
    template_name = 'inventory/supplier_stock_form.html'
    success_url = reverse_lazy('inventory:supplier_stock_list')

class SupplierStockUpdateView(LoginRequiredMixin, UpdateView):
    model = SupplierStock
    form_class = SupplierStockForm
    template_name = 'inventory/supplier_stock_form.html'
    success_url = reverse_lazy('inventory:supplier_stock_list')

# EstablishmentStock Views
class EstablishmentStockListView(LoginRequiredMixin, ListView):
    model = EstablishmentStock
    template_name = 'inventory/establishment_stock_list.html'
    context_object_name = 'establishment_stock'

class EstablishmentStockCreateView(LoginRequiredMixin, CreateView):
    model = EstablishmentStock
    form_class = EstablishmentStockForm
    template_name = 'inventory/establishment_stock_form.html'
    success_url = reverse_lazy('inventory:establishment_stock_list')

class EstablishmentStockUpdateView(LoginRequiredMixin, UpdateView):
    model = EstablishmentStock
    form_class = EstablishmentStockForm
    template_name = 'inventory/establishment_stock_form.html'
    success_url = reverse_lazy('inventory:establishment_stock_list')
