# ixcaui_app/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F, Sum
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpRequest, HttpResponse
from django.contrib import messages
from decimal import Decimal
from typing import Tuple, Optional, List, Dict, Union
# Importar modelos
from .models import (
    RecetaPrincipal, ItemReceta, Ingrediente, IngredienteSustituto,
    InventarioEstablecimiento, InventarioEmpresa, MovimientoInventario,
    Alerta, Establecimiento, IngredienteCambioCorporativo, Empresa, User, SubReceta
)
# Importar forms (asume que existe ProductoForm o similar en forms.py)
from .forms import ProductoForm # Usado como ejemplo, asegúrate de que este import sea correcto
# Importar la función para obtener el request actual (desde middleware)
# Asegúrate de que tu middleware esté configurado correctamente en settings.py
from .managers import get_current_request
# --- Funciones Auxiliares para Lógica de Negocio ---
def obtener_ingrediente_para_receta(
    establecimiento_id: int,
    ingrediente_requerido_id: int,
    cantidad_requerida: Decimal
) -> Tuple[Optional[Ingrediente], Optional[bool], Optional[Ingrediente]]:
    """
    Función central para determinar la disponibilidad de un ingrediente y sus sustitutos.
    Retorna el ingrediente encontrado (principal o sustituto), si es sustituto, y el ingrediente original si se usó un sustituto.
    """
    try:
        ingrediente_principal = Ingrediente.objects.get(id=ingrediente_requerido_id)
    except Ingrediente.DoesNotExist:
        return None, None, None
    inventario = InventarioEstablecimiento.objects.filter(
        establecimiento_id=establecimiento_id,
        ingrediente=ingrediente_principal
    ).first()
    if inventario and inventario.cantidad >= cantidad_requerida:
        return ingrediente_principal, False, None
    # Si no hay suficiente, buscar sustitutos
    sustitutos = IngredienteSustituto.objects.filter(
        ingrediente_principal=ingrediente_principal,
        activo=True
    ).order_by('factor_conversion') # Podrías ordenar por algún criterio de preferencia
    for sustituto_rel in sustitutos:
        ingrediente_sustituto = sustituto_rel.ingrediente_sustituto
        cantidad_necesaria_sustituto = cantidad_requerida * sustituto_rel.factor_conversion
        inventario_sustituto = InventarioEstablecimiento.objects.filter(
            establecimiento_id=establecimiento_id,
            ingrediente=ingrediente_sustituto
        ).first()
        if inventario_sustituto and inventario_sustituto.cantidad >= cantidad_necesaria_sustituto:
            return ingrediente_sustituto, True, ingrediente_principal
    return None, None, None
@login_required
def home_view(request: HttpRequest) -> HttpResponse:
    """
    Vista de la página de inicio para usuarios logueados.
    Muestra información básica basada en el tipo de usuario y sus asociaciones.
    """
    user = request.user
    context = {
        'username': user.username,
        'tipo_usuario': user.get_tipo_usuario_display(),
        'has_establecimiento_selected': False # Por defecto
    }
    if user.is_authenticated:
        # Lógica para mostrar las alertas recientes
        # Filtrar alertas por usuario, establecimiento o empresa
        alertas_recientes = Alerta.objects.filter(activa=True, leida=False).order_by('-fecha_creacion')[:5]
        if user.tipo_usuario == 'establecimiento' and user.establecimiento_asociado:
            alertas_recientes = alertas_recientes.filter(establecimiento=user.establecimiento_asociado)
            request.session['establecimiento_id'] = user.establecimiento_asociado.id
            context['has_establecimiento_selected'] = True
        elif user.tipo_usuario == 'empresa' and user.empresa_asociada:
            alertas_recientes = alertas_recientes.filter(empresa=user.empresa_asociada)
            # Podrías tener un selector de establecimiento si una empresa tiene varios
            if 'establecimiento_id' in request.session:
                context['has_establecimiento_selected'] = True
        elif user.tipo_usuario == 'admin_global':
            # Los admins globales ven todas las alertas, o un resumen
            pass # No se filtra por establecimiento o empresa específica a menos que se seleccione
        elif user.tipo_usuario == 'proveedor' and user.proveedor_asociado:
            # Filtrar alertas relevantes para proveedores (ej. nuevas órdenes de compra)
            # Esto dependerá de cómo se modelen las alertas para proveedores
            alertas_recientes = alertas_recientes.filter(usuario=user) # O por proveedor_asociado si el modelo Alerta lo permite
        context['alertas_recientes'] = alertas_recientes
        # Lógica para redirigir a la selección de establecimiento si es un usuario de empresa sin establecimiento seleccionado
        if user.tipo_usuario == 'empresa' and user.empresa_asociada and 'establecimiento_id' not in request.session:
            # Si la empresa tiene solo un establecimiento, seleccionarlo automáticamente
            establecimientos_empresa = Establecimiento.objects.filter(empresa=user.empresa_asociada, activo=True)
            if establecimientos_empresa.count() == 1:
                request.session['establecimiento_id'] = establecimientos_empresa.first().id
                context['has_establecimiento_selected'] = True
                messages.info(request, f"Establecimiento '{establecimientos_empresa.first().nombre}' seleccionado automáticamente.")
            else:
                return redirect('select_establecimiento')
    return render(request, 'ixcaui_app/home.html', context)
@login_required
def select_establecimiento_view(request: HttpRequest) -> HttpResponse:
    """
    Permite a los usuarios de tipo 'empresa' seleccionar un establecimiento
    para operar dentro de él.
    """
    user = request.user
    if user.tipo_usuario != 'empresa' or not user.empresa_asociada:
        messages.warning(request, "No tienes permiso para acceder a esta página o no estás asociado a una empresa.")
        return redirect('home')
    establecimientos = Establecimiento.objects.filter(empresa=user.empresa_asociada, activo=True)
    if request.method == 'POST':
        establecimiento_id = request.POST.get('establecimiento')
        try:
            establecimiento_seleccionado = Establecimiento.objects.get(id=establecimiento_id, empresa=user.empresa_asociada, activo=True)
            request.session['establecimiento_id'] = establecimiento_seleccionado.id
            messages.success(request, f"Has seleccionado el establecimiento: {establecimiento_seleccionado.nombre}")
            return redirect('home')
        except Establecimiento.DoesNotExist:
            messages.error(request, "El establecimiento seleccionado no es válido.")
    context = {
        'establecimientos': establecimientos
    }
    return render(request, 'ixcaui_app/select_establecimiento.html', context)
@login_required
def producto_list_create_view(request: HttpRequest) -> HttpResponse:
    user = request.user
    # Asegúrate de que solo los usuarios autorizados puedan acceder (ej. admin_global, empresa, establecimiento)
    if user.tipo_usuario not in ['admin_global', 'empresa', 'establecimiento']:
        messages.error(request, "No tienes permisos para gestionar productos.")
        return redirect('home')
    # Determinar el establecimiento/empresa para filtrar los productos
    empresa_id = None
    establecimiento_id = None
    if user.tipo_usuario == 'establecimiento' and user.establecimiento_asociado:
        establecimiento_id = user.establecimiento_asociado.id
        empresa_id = user.establecimiento_asociado.empresa.id
    elif user.tipo_usuario == 'empresa' and user.empresa_asociada:
        empresa_id = user.empresa_asociada.id
        # Si un usuario de empresa puede ver productos de establecimientos específicos
        # o solo productos a nivel de cadena. Por ahora, asumimos nivel de cadena.
        # Si la empresa ha seleccionado un establecimiento en la sesión, se filtra por él.
        if 'establecimiento_id' in request.session:
            establecimiento_id = request.session['establecimiento_id']
    elif user.tipo_usuario == 'admin_global':
        # Un admin global puede ver todos los productos o filtrar por una empresa/establecimiento
        # que seleccione (ej. a través de un parámetro GET o un selector en la UI)
        # Por ahora, para simplificar, si no hay filtro explícito, solo verá los productos sin establecimiento asociado
        # o podría ver todos si se desea. Aquí se necesita más lógica de UI/UX para el admin global.
        pass
    productos = Producto.objects.all()
    if empresa_id:
        productos = productos.filter(empresa_id=empresa_id)
    if establecimiento_id:
        productos = productos.filter(establecimiento_id=establecimiento_id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, request=request) # Pasa el request al formulario
        if form.is_valid():
            producto = form.save(commit=False)
            # Asignar empresa/establecimiento basado en el usuario logueado o selección del admin
            if request.user.tipo_usuario == 'admin_global':
                # El formulario debería permitir seleccionar empresa/establecimiento para admin_global
                # o se asigna en el form.save() si no se pasa commit=False
                pass # Lógica de asignación en el form o aquí si es necesario
            elif request.user.tipo_usuario == 'empresa' and request.user.empresa_asociada:
                producto.empresa = request.user.empresa_asociada
                producto.establecimiento = None # Producto de cadena, no de establecimiento específico
            elif request.user.tipo_usuario == 'establecimiento' and request.user.establecimiento_asociado:
                # Si un usuario de establecimiento crea un producto, se asocia a su establecimiento y la empresa de este.
                producto.establecimiento = request.user.establecimiento_asociado
                producto.empresa = request.user.establecimiento_asociado.empresa
            producto.save()
            messages.success(request, "Producto creado exitosamente.")
            return redirect('producto_list_create')
        else:
            messages.error(request, "Error al crear el producto. Revise los datos.")
    else:
        form = ProductoForm(request=request) # Pasa el request al formulario
    context = {
        'productos': productos,
        'form': form,
        'establecimiento_id': establecimiento_id, # Pasa el ID del establecimiento para usar en la plantilla
        'empresa_id': empresa_id, # Pasa el ID de la empresa para usar en la plantilla
    }
    return render(request, 'ixcaui_app/producto_list_create.html', context)