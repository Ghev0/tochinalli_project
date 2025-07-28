# tochinalli_project/ixcaui_app/managers.py

from django.db import models
from django.contrib.auth.models import UserManager as BaseUserManager
from django.db.models import Q
import threading

# Un objeto thread-local para almacenar el request actual.
_current_request = threading.local()

def get_current_request():
    """Retorna el objeto request actual si ha sido establecido."""
    return getattr(_current_request, 'request', None)

def set_current_request(request):
    """Establece el objeto request actual para este hilo."""
    _current_request.request = request

def clear_current_request():
    """Limpia el objeto request del hilo actual."""
    if hasattr(_current_request, 'request'):
        del _current_request.request

class TenantAwareManager(models.Manager):
    """
    Manager personalizado que filtra los objetos por el tenant (empresa/establecimiento/proveedor)
    asociado al usuario logueado en la solicitud actual.
    """
    def get_queryset(self):
        queryset = super().get_queryset()
        request = get_current_request()
        
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user_obj = request.user
            
            # Si es superusuario o admin global, ve todo
            if user_obj.is_superuser or (hasattr(user_obj, 'is_tochinalli_admin') and user_obj.is_tochinalli_admin):
                return queryset # No filtra para admins globales

            # Si el modelo tiene campo 'empresa' y el usuario es de tipo 'empresa'
            if hasattr(self.model, 'empresa') and user_obj.tipo_usuario == 'empresa' and user_obj.empresa_asociada:
                return queryset.filter(empresa=user_obj.empresa_asociada)
            
            # Si el modelo tiene campo 'establecimiento' y el usuario es de tipo 'empresa'
            # y está restringido a un establecimiento específico.
            if hasattr(self.model, 'establecimiento') and user_obj.tipo_usuario == 'empresa' and user_obj.restringido_a_establecimiento and user_obj.establecimiento_asociado:
                # Esto filtrará aún más si ya se filtró por empresa, asegurando que el establecimiento sea de la empresa
                return queryset.filter(establecimiento=user_obj.establecimiento_asociado)

            # Si el modelo tiene campo 'proveedor' y el usuario es de tipo 'proveedor'
            if hasattr(self.model, 'proveedor') and user_obj.tipo_usuario == 'proveedor' and user_obj.proveedor_asociado:
                return queryset.filter(proveedor=user_obj.proveedor_asociado)
        
        # Si no hay usuario, no está autenticado, o no hay filtro por tenant aplicable,
        # para modelos con campos de tenant, se retorna un queryset vacío por seguridad.
        # Para modelos sin campos de tenant (ej. UnidadMedida, o modelos globales), se retorna el queryset completo.
        if hasattr(self.model, 'empresa') or hasattr(self.model, 'proveedor') or hasattr(self.model, 'establecimiento'):
            return queryset.none() # Modelos con tenant, si no hay usuario o no aplica, no se ven
        return queryset # Modelos sin tenant (globales) siempre se ven


# Manager específico para OrdenDeCompra
class OrdenDeCompraManager(TenantAwareManager):
    """
    Manager específico para el modelo OrdenDeCompra,
    aplicando lógica de filtrado de tenant y acceso por roles.
    Hereda de TenantAwareManager para aprovechar la lógica de filtrado base.
    """
    def get_queryset(self):
        queryset = super().get_queryset() # Obtiene el queryset base filtrado por el TenantAwareManager
        # La lógica adicional específica para OrdenDeCompra se manejará automáticamente
        # si los campos 'establecimiento' o 'proveedor' están en OrdenDeCompra
        # y son manejados por TenantAwareManager. No se necesita lógica duplicada aquí.
        return queryset