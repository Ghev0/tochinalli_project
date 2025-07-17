from django.urls import path
from .views import (
    SupplierListView,
    SupplierCreateView,
    SupplierUpdateView,
    SupplierStockListView,
    SupplierStockCreateView,
    SupplierStockUpdateView,
    EstablishmentStockListView,
    EstablishmentStockCreateView,
    EstablishmentStockUpdateView,
)

app_name = 'inventory'

urlpatterns = [
    path('suppliers/', SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/new/', SupplierCreateView.as_view(), name='supplier_create'),
    path('suppliers/<int:pk>/edit/', SupplierUpdateView.as_view(), name='supplier_update'),

    path('supplier-stock/', SupplierStockListView.as_view(), name='supplier_stock_list'),
    path('supplier-stock/new/', SupplierStockCreateView.as_view(), name='supplier_stock_create'),
    path('supplier-stock/<int:pk>/edit/', SupplierStockUpdateView.as_view(), name='supplier_stock_update'),

    path('establishment-stock/', EstablishmentStockListView.as_view(), name='establishment_stock_list'),
    path('establishment-stock/new/', EstablishmentStockCreateView.as_view(), name='establishment_stock_create'),
    path('establishment-stock/<int:pk>/edit/', EstablishmentStockUpdateView.as_view(), name='establishment_stock_update'),
]
