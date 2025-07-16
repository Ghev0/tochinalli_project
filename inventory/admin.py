from django.contrib import admin
from .models import Supplier, SupplierStock, EstablishmentStock

admin.site.register(Supplier)
admin.site.register(SupplierStock)
admin.site.register(EstablishmentStock)
