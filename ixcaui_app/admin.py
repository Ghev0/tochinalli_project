# tochinalli_project/ixcaui_app/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, Permission
from django.db.models import Sum, F
from django.urls import reverse
from django.utils.html import format_html

# Importa TODOS tus modelos de ixcaui_app que quieres ver en el admin
from .models import (
    Empresa, Proveedor, TipoEstablecimiento, Establecimiento, Puesto, Area, NivelJerarquico,
    UnidadMedida, CategoriaIngrediente, SubcategoriaIngrediente,
    Ingrediente, SubReceta, RecetaPrincipal, ItemReceta,
    Producto, ProductoProveedor, InventarioEstablecimiento, InventarioEmpresa, OrdenDeCompra, ItemOrdenDeCompra,
    Evento, EventoReceta,
    User,  # Asegúrate que tu modelo de usuario se llama 'User' y está definido en models.py
)

# Desregistra el User y Group por defecto de Django si ya lo tenías registrado
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass

# --- Custom User Admin ---
@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    # Asegúrate de que estos campos existen en tu modelo User
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'is_staff', 'tipo_usuario',
        'empresa_asociada', 'establecimiento_asociado', 'proveedor_asociado'
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'tipo_usuario', 'empresa_asociada', 'establecimiento_asociado')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
        ('Información de Tochinalli', {'fields': ('tipo_usuario', 'empresa_asociada', 'establecimiento_asociado', 'proveedor_asociado')}),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)


# --- Clases inline (deben definirse ANTES de usarlas en inlines) ---

class ItemRecetaInline(admin.TabularInline):
    model = ItemReceta
    extra = 1
    # Asegúrate que 'ingrediente' y 'unidad_medida' son ForeignKeys o campos directos
    raw_id_fields = ('ingrediente', 'unidad_medida')
    # 'costo_estimado' es un método en el modelo ItemReceta
    readonly_fields = ('costo_estimado_display',)
    fields = ('ingrediente', 'cantidad', 'unidad_medida', 'costo_estimado_display')

    @admin.display(description='Costo Estimado')
    def costo_estimado_display(self, obj):
        # Asegúrate de que este método exista en tu modelo ItemReceta
        return obj.costo_estimado if hasattr(obj, 'costo_estimado') else 'N/A'


class ItemSubRecetaInline(admin.TabularInline):
    # Asume que ItemReceta tiene un campo ForeignKey a SubReceta llamado 'sub_receta'
    model = ItemReceta # El modelo Inline es ItemReceta
    fk_name = 'sub_receta' # El campo ForeignKey en ItemReceta que apunta a SubReceta
    extra = 1
    raw_id_fields = ('ingrediente', 'unidad_medida')
    readonly_fields = ('costo_estimado_display',)
    fields = ('ingrediente', 'cantidad', 'unidad_medida', 'costo_estimado_display')

    @admin.display(description='Costo Estimado')
    def costo_estimado_display(self, obj):
        return obj.costo_estimado if hasattr(obj, 'costo_estimado') else 'N/A'


class ItemOrdenDeCompraInline(admin.TabularInline):
    model = ItemOrdenDeCompra
    extra = 1
    raw_id_fields = ('producto_proveedor',)
    readonly_fields = ('precio_total_calculado',)
    fields = ('producto_proveedor', 'cantidad_pedida', 'cantidad_recibida', 'precio_total_calculado')

    @admin.display(description='Precio Total')
    def precio_total_calculado(self, obj):
        return obj.precio_total if hasattr(obj, 'precio_total') else 'N/A' # Asume que precio_total es una propiedad en ItemOrdenDeCompra


class EventoRecetaInline(admin.TabularInline):
    model = EventoReceta
    extra = 1
    raw_id_fields = ('receta_principal',)
    fields = ('receta_principal', 'cantidad_a_producir',) # Asegúrate que estos campos existen en EventoReceta


# --- Clases Admin para Modelos ---

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'razon_social', 'rfc', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'razon_social', 'rfc')


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    # Asumo 'contacto_principal' es un campo directo. Si es una relación, raw_id_fields
    list_display = ('nombre', 'contacto_principal', 'telefono', 'email', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'contacto_principal', 'email')
    # Si contacto_principal fuera un ForeignKey a User: raw_id_fields = ('contacto_principal',)


@admin.register(TipoEstablecimiento)
class TipoEstablecimientoAdmin(admin.ModelAdmin):
    list_display = ('nombre',) # Corregido: 'nombre_tipo' a 'nombre'
    search_fields = ('nombre',)


@admin.register(Establecimiento)
class EstablecimientoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'empresa', 'tipo_establecimiento', 'activo')
    list_filter = ('activo', 'empresa', 'tipo_establecimiento')
    search_fields = ('nombre', 'empresa__nombre', 'tipo_establecimiento__nombre')
    raw_id_fields = ('empresa', 'tipo_establecimiento')


@admin.register(Puesto)
class PuestoAdmin(admin.ModelAdmin):
    # Corregido: 'nombre_puesto' a 'nombre_puesto', y asegurando los FKs para list_display y filter
    list_display = ('nombre_puesto', 'nivel_jerarquico', 'empresa', 'establecimiento')
    list_filter = ('nivel_jerarquico', 'empresa', 'establecimiento')
    search_fields = ('nombre_puesto', 'nivel_jerarquico__nombre', 'empresa__nombre', 'establecimiento__nombre')
    raw_id_fields = ('nivel_jerarquico', 'empresa', 'establecimiento') # Corregido: deben ser FKs


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'empresa', 'establecimiento')
    list_filter = ('empresa', 'establecimiento')
    search_fields = ('nombre', 'empresa__nombre', 'establecimiento__nombre')
    raw_id_fields = ('empresa', 'establecimiento')


@admin.register(NivelJerarquico)
class NivelJerarquicoAdmin(admin.ModelAdmin):
    # Corregido: 'nombre_nivel' a 'nombre'
    list_display = ('nombre', 'nivel_numerico')
    search_fields = ('nombre',)
    ordering = ('nivel_numerico',)


@admin.register(UnidadMedida)
class UnidadMedidaAdmin(admin.ModelAdmin):
    # Corregido: es_sistema_metrico y categoria_uso son campos directos
    list_display = ('nombre', 'simbolo', 'es_sistema_metrico', 'categoria_uso')
    list_filter = ('es_sistema_metrico', 'categoria_uso')
    search_fields = ('nombre', 'simbolo')


@admin.register(CategoriaIngrediente)
class CategoriaIngredienteAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


@admin.register(SubcategoriaIngrediente)
class SubcategoriaIngredienteAdmin(admin.ModelAdmin):
    # Corregido: categoria_padre es FK
    list_display = ('nombre', 'categoria_padre')
    list_filter = ('categoria_padre',)
    search_fields = ('nombre', 'categoria_padre__nombre')
    raw_id_fields = ('categoria_padre',) # Correcto si es FK


@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'subcategoria', 'unidad_compra_base', 'precio_por_unidad')
    list_filter = ('categoria', 'subcategoria', 'unidad_compra_base')
    search_fields = ('nombre', 'descripcion')
    raw_id_fields = ('categoria', 'subcategoria', 'unidad_compra_base')


@admin.register(RecetaPrincipal)
class RecetaPrincipalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rendimiento_cantidad', 'unidad_rendimiento', 'costo_total_estimado_display')
    list_filter = ('empresa', 'establecimiento', 'unidad_rendimiento')
    search_fields = ('nombre', 'descripcion')
    raw_id_fields = ('empresa', 'establecimiento', 'unidad_rendimiento', 'creada_por')
    inlines = [ItemRecetaInline]
    readonly_fields = ('costo_total_estimado_display',)
    fieldsets = (
        (None, {
            'fields': ('nombre', 'descripcion', 'empresa', 'establecimiento', 'creada_por')
        }),
        ('Rendimiento y Costo', {
            'fields': ('rendimiento_cantidad', 'unidad_rendimiento', 'costo_total_estimado_display'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Costo Total Estimado')
    def costo_total_estimado_display(self, obj):
        return obj.costo_total_estimado if hasattr(obj, 'costo_total_estimado') else 'N/A'


@admin.register(SubReceta)
class SubRecetaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rendimiento_cantidad', 'unidad_rendimiento', 'costo_total_estimado_display')
    list_filter = ('empresa', 'establecimiento', 'unidad_rendimiento')
    search_fields = ('nombre', 'descripcion')
    raw_id_fields = ('empresa', 'establecimiento', 'unidad_rendimiento', 'creada_por')
    inlines = [ItemSubRecetaInline] # Usamos ItemSubRecetaInline aquí
    readonly_fields = ('costo_total_estimado_display',)
    fieldsets = (
        (None, {
            'fields': ('nombre', 'descripcion', 'empresa', 'establecimiento', 'creada_por')
        }),
        ('Rendimiento y Costo', {
            'fields': ('rendimiento_cantidad', 'unidad_rendimiento', 'costo_total_estimado_display'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Costo Total Estimado')
    def costo_total_estimado_display(self, obj):
        return obj.costo_total_estimado if hasattr(obj, 'costo_total_estimado') else 'N/A'


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_venta', 'unidad_medida', 'receta_principal', 'activo', 'empresa', 'establecimiento')
    list_filter = ('activo', 'unidad_medida', 'empresa', 'establecimiento')
    search_fields = ('nombre', 'descripcion')
    raw_id_fields = ('receta_principal', 'unidad_medida', 'empresa', 'establecimiento')


@admin.register(ProductoProveedor)
class ProductoProveedorAdmin(admin.ModelAdmin):
    # Corregido: 'unidad_medida_compra' a 'unidad_medida', y 'activo'
    list_display = ('producto', 'proveedor', 'precio_compra', 'unidad_medida', 'activo')
    list_filter = ('activo', 'proveedor', 'unidad_medida')
    search_fields = ('producto__nombre', 'proveedor__nombre')
    raw_id_fields = ('producto', 'proveedor', 'unidad_medida') # Corregido: debe ser FK


@admin.register(InventarioEmpresa)
class InventarioEmpresaAdmin(admin.ModelAdmin):
    # Corregido: usando los nombres de campo reales 'cantidad' y 'unidad_medida'
    list_display = ('empresa', 'ingrediente', 'cantidad', 'unidad_medida')
    list_filter = ('empresa', 'ingrediente')
    search_fields = ('empresa__nombre', 'ingrediente__nombre')
    raw_id_fields = ('empresa', 'ingrediente', 'unidad_medida') # 'unidad_medida' es FK


@admin.register(InventarioEstablecimiento)
class InventarioEstablecimientoAdmin(admin.ModelAdmin):
    # Corregido: usando los nombres de campo reales 'cantidad' y 'unidad_medida'
    list_display = ('establecimiento', 'ingrediente', 'cantidad', 'unidad_medida')
    list_filter = ('establecimiento', 'ingrediente')
    search_fields = ('establecimiento__nombre', 'ingrediente__nombre')
    raw_id_fields = ('establecimiento', 'ingrediente', 'unidad_medida') # 'unidad_medida' es FK
    readonly_fields = () # No hay 'ultima_actualizacion' como campo en tu modelo actual


@admin.register(OrdenDeCompra)
class OrdenDeCompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'establecimiento', 'proveedor', 'fecha_orden', 'estado', 'total_orden', 'creada_por')
    list_filter = ('estado', 'establecimiento', 'proveedor', 'fecha_orden')
    search_fields = ('id', 'establecimiento__nombre', 'proveedor__nombre', 'creada_por__username')
    raw_id_fields = ('establecimiento', 'proveedor', 'creada_por')
    inlines = [ItemOrdenDeCompraInline]
    readonly_fields = ('total_orden',)
    fieldsets = (
        (None, {
            'fields': ('establecimiento', 'proveedor', 'fecha_orden', 'fecha_entrega_esperada', 'estado', 'creada_por')
        }),
        ('Totales', {
            'fields': ('total_orden',),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        return self.model.objects.all() # El OrdenDeCompraManager ya filtra


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    # Asegúrate que 'tipo_evento', 'activo', 'creado_por' son los nombres correctos en tu modelo Evento
    list_display = ('nombre_evento', 'establecimiento', 'fecha_evento', 'tipo_evento', 'activo', 'creado_por')
    list_filter = ('establecimiento', 'tipo_evento', 'activo', 'fecha_evento')
    search_fields = ('nombre_evento', 'descripcion', 'establecimiento__nombre')
    raw_id_fields = ('establecimiento', 'creado_por') # 'creado_por' es el nombre correcto según models.py
    inlines = [EventoRecetaInline]
    fieldsets = (
        (None, {
            'fields': ('establecimiento', 'nombre_evento', 'descripcion', 'fecha_evento', 'hora_inicio', 'hora_fin', 'tipo_evento', 'activo', 'creado_por')
        }),
        ('Detalles de Capacidad', {
            'fields': ('capacidad_maxima_personas', 'capacidad_maxima_mesas'),
            'classes': ('collapse',),
        }),
    )