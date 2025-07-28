# ixcaui_app/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings # Para AUTH_USER_MODEL
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
# Importa el TenantAwareManager. Asume que managers.py existe y está bien configurado.
from .managers import TenantAwareManager, OrdenDeCompraManager, get_current_request
# --- Modelos de Estructura de Negocio ---
class Empresa(models.Model):
    nombre = models.CharField(max_length=255, unique=True, verbose_name="Nombre de la Empresa/Cadena")
    razon_social = models.CharField(max_length=255, blank=True, null=True, verbose_name="Razón Social")
    rfc = models.CharField(max_length=13, blank=True, null=True, verbose_name="RFC")
    direccion = models.TextField(blank=True, null=True, verbose_name="Dirección")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, null=True, verbose_name="Email de Contacto")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    objects = TenantAwareManager()
    class Meta:
        verbose_name = "Empresa/Cadena"
        verbose_name_plural = "Empresas/Cadenas"
    def __str__(self):
        return self.nombre
class Proveedor(models.Model):
    nombre = models.CharField(max_length=255, unique=True, verbose_name="Nombre del Proveedor")
    contacto = models.CharField(max_length=255, blank=True, null=True, verbose_name="Persona de Contacto")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, null=True, verbose_name="Email de Contacto")
    direccion = models.TextField(blank=True, null=True, verbose_name="Dirección")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='proveedores', null=True, blank=True, verbose_name="Empresa Asociada")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    objects = TenantAwareManager()
    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
    def __str__(self):
        return self.nombre
class TipoEstablecimiento(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Tipo de Establecimiento")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    objects = TenantAwareManager() # Este manager debe ser global o asegurar que no filtre por tenant
    class Meta:
        verbose_name = "Tipo de Establecimiento"
        verbose_name_plural = "Tipos de Establecimiento"
    def __str__(self):
        return self.nombre
class Establecimiento(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Nombre del Establecimiento")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='establecimientos', verbose_name="Empresa/Cadena")
    tipo = models.ForeignKey(TipoEstablecimiento, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tipo")
    direccion = models.TextField(blank=True, null=True, verbose_name="Dirección")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, null=True, verbose_name="Email de Contacto")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    objects = TenantAwareManager()
    class Meta:
        verbose_name = "Establecimiento"
        verbose_name_plural = "Establecimientos"
        unique_together = ('nombre', 'empresa')
    def __str__(self):
        return f"{self.nombre} ({self.empresa.nombre})"
# --- Modelos de Usuarios y Permisos ---
class Puesto(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre del Puesto")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='puestos', null=True, blank=True, verbose_name="Empresa Asociada")
    objects = TenantAwareManager()
    class Meta:
        verbose_name = "Puesto"
        verbose_name_plural = "Puestos"
    def __str__(self):
        return self.nombre
class Area(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre del Área")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='areas', null=True, blank=True, verbose_name="Empresa Asociada")
    objects = TenantAwareManager()
    class Meta:
        verbose_name = "Área"
        verbose_name_plural = "Áreas"
    def __str__(self):
        return self.nombre
class NivelJerarquico(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre del Nivel Jerárquico")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    orden = models.IntegerField(unique=True, verbose_name="Orden Jerárquico")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='niveles_jerarquicos', null=True, blank=True, verbose_name="Empresa Asociada")
    objects = TenantAwareManager()
    class Meta:
        verbose_name = "Nivel Jerárquico"
        verbose_name_plural = "Niveles Jerárquicos"
        ordering = ['orden']
    def __str__(self):
        return self.nombre
class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin_global', 'Administrador Global'),
        ('empresa', 'Administrador de Empresa/Cadena'),
        ('establecimiento', 'Administrador de Establecimiento'),
        ('proveedor', 'Proveedor'),
        ('empleado', 'Empleado de Establecimiento'),
        ('comensal', 'Comensal'),
    )
    tipo_usuario = models.CharField(max_length=50, choices=USER_TYPE_CHOICES, default='comensal', verbose_name="Tipo de Usuario")
    empresa_asociada = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios', verbose_name="Empresa Asociada")
    establecimiento_asociado = models.ForeignKey(Establecimiento, on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios', verbose_name="Establecimiento Asociado")
    proveedor_asociado = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios', verbose_name="Proveedor Asociado")
    puesto = models.ForeignKey(Puesto, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Puesto")
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Área")
    nivel_jerarquico = models.ForeignKey(NivelJerarquico, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Nivel Jerárquico")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    objects = TenantAwareManager()
    def save(self, *args, **kwargs):
        # Lógica para asignar empresa/establecimiento automáticamente si no está seteado y el tipo de usuario lo permite
        if not self.empresa_asociada and self.establecimiento_asociado:
            self.empresa_asociada = self.establecimiento_asociado.empresa
        super().save(*args, **kwargs)
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
    def __str__(self):
        return self.username
# --- Modelos de Recetas e Inventario ---
class UnidadMedida(models.Model):
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre de la Unidad")
    abreviatura = models.CharField(max_length=10, unique=True, verbose_name="Abreviatura")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    # Este modelo podría ser global, no necesita empresa_asociada si es universal
    objects = models.Manager() # No aplica filtrado por tenant
    class Meta:
        verbose_name = "Unidad de Medida"
        verbose_name_plural = "Unidades de Medida"
    def __str__(self):
        return self.nombre
class CategoriaIngrediente(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la Categoría")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='categorias_ingrediente', null=True, blank=True, verbose_name="Empresa Asociada")
    objects = TenantAwareManager()
    class Meta:
        verbose_name = "Categoría de Ingrediente"
        verbose_name_plural = "Categorías de Ingredientes"
    def __str__(self):
        return self.nombre
class SubcategoriaIngrediente(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre de la Subcategoría")
    categoria = models.ForeignKey(CategoriaIngrediente, on_delete=models.CASCADE, related_name='subcategorias', verbose_name="Categoría Padre")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='subcategorias_ingrediente', null=True, blank=True, verbose_name="Empresa Asociada")
    objects = TenantAwareManager()
    class Meta:
        verbose_name = "Subcategoría de Ingrediente"
        verbose_name_plural = "Subcategorías de Ingredientes"
        unique_together = ('nombre', 'categoria')
    def __str__(self):
        return f"{self.nombre} ({self.categoria.nombre})"
class Ingrediente(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Nombre del Ingrediente")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    unidad_medida_base = models.ForeignKey(UnidadMedida, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Unidad de Medida Base")
    costo_unitario_base = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name="Costo Unitario Base")
    categoria = models.ForeignKey(CategoriaIngrediente, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Categoría")
    subcategoria = models.ForeignKey(SubcategoriaIngrediente, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Subcategoría")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='ingredientes', null=True, blank=True, verbose_name="Empresa Asociada")
    objects = TenantAwareManager()
    class Meta:
        verbose_name = "Ingrediente"
        verbose_name_plural = "Ingredientes"
        unique_together = ('nombre', 'empresa') # Un ingrediente puede tener el mismo nombre en diferentes empresas
    def __str__(self):
        return self.nombre
class IngredienteSustituto(models.Model):
    ingrediente_principal = models.ForeignKey(Ingrediente, on_delete=models.CASCADE, related_name='sustitutos_principales', verbose_name="Ingrediente Principal")
    ingrediente_sustituto = models.ForeignKey(Ingrediente, on_delete=models.CASCADE, related_name='sustitutos_alternativos', verbose_name="Ingrediente Sustituto")
    factor_conversion = models.DecimalField(max_digits=10, decimal_places=4, default=1.0, verbose_name="Factor de Conversión (ej. 1 kg de A = 0.9 kg de B)")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='ingredientes_sustitutos', null=True, blank=True, verbose_name="Empresa Asociada")
    objects = TenantAwareManager()
    class Meta:
        verbose_name = "Ingrediente Sustituto"
        verbose_name_plural = "Ingredientes Sustitutos"
        unique_together = ('ingrediente_principal', 'ingrediente_sustituto')
    def __str__(self):
        return f"{self.ingrediente_principal.nombre} puede ser sustituido por {self.ingrediente_sustituto.nombre}"
class SubReceta(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Nombre de la Sub-Receta")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    instrucciones = models.TextField(blank=True, null=True, verbose_name="Instrucciones")
    rendimiento_cantidad = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Cantidad de Rendimiento")
    rendimiento_unidad = models.ForeignKey(UnidadMedida, on_delete=models.SET_NULL, null=True, blank=True, related_name='subrecetas_rendimiento', verbose_name="Unidad de Rendimiento")
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Costo Total de Sub-Receta")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='subrecetas', null=True, blank=True, verbose_name="Empresa Asociada")
    creada_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='subrecetas_creadas', verbose_name="Creada por")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    objects = TenantAwareManager()
    class Meta:
        verbose_name = "Sub-Receta"
        verbose_name_plural = "Sub-Recetas"
        unique_together = ('nombre', 'empresa')
    def __str__(self):
        return self.nombre
class RecetaPrincipal(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Nombre de la Receta Principal")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    instrucciones = models.TextField(blank=True, null=True, verbose_name="Instrucciones")
    rendimiento_cantidad = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Cantidad de Rendimiento")
    rendimiento_unidad = models.ForeignKey(UnidadMedida, on_delete=models.SET_NULL, null=True, blank=True, related_name='recetas_principales_rendimiento', verbose_name="Unidad de Rendimiento")
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Costo Total de Receta")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='recetas_principales', null=True, blank=True, verbose_name="Empresa Asociada")
    creada_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='recetas_creadas', verbose_name="Creada por")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    objects = TenantAwareManager()
    class Meta:
        verbose_name = "Receta Principal"
        verbose_name_plural = "Recetas Principales"
        unique_together = ('nombre', 'empresa')
    def __str__(self):
        return self.nombre
class ItemReceta(models.Model):
    receta_principal = models.ForeignKey(RecetaPrincipal, on_delete=models.CASCADE, related_name='items', null=True, blank=True, verbose_name="Receta Principal")
    sub_receta = models.ForeignKey(SubReceta, on_delete=models.CASCADE, related_name='items', null=True, blank=True, verbose_name="Sub-Receta")
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Ingrediente")
    cantidad = models.DecimalField(max_digits=10, decimal_places=4, verbose_name="Cantidad Requerida")
    unidad_medida = models.ForeignKey(UnidadMedida, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Unidad de Medida")
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=4, default=0.00, verbose_name="Costo Unitario en Receta")
    costo_total_item = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Costo Total del Item")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='items_receta', null=True, blank=True, verbose_name="Empresa Asociada")
    objects = TenantAwareManager()
    class Meta:
        verbose_name = "Item de Receta"
        verbose_name_plural = "Items de Receta"
        # Restricción para asegurar que solo uno de los campos (receta_principal, sub_receta, ingrediente) esté lleno
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(receta_principal__isnull=False, sub_receta__isnull=True, ingrediente__isnull=True) |
                    models.Q(receta_principal__isnull=True, sub_receta__isnull=False, ingrediente__isnull=True) |
                    models.Q(receta_principal__isnull=True, sub_receta__isnull=True, ingrediente__isnull=False)
                ),
                name='only_one_item_type_for_recipe'
            )
        ]
    def __str__(self):
        if self.receta_principal:
            return f"Item para Receta Principal: {self.receta_principal.nombre}"
        elif self.sub_receta:
            return f"Item para Sub-Receta: {self.sub_receta.nombre}"
        elif self.ingrediente:
            return f"Item de Ingrediente: {self.ingrediente.nombre}"
        return "Item de Receta (Sin tipo)"
    def save(self, *args, **kwargs):
        # Asegurar que solo uno de los campos de relación esté lleno
        if sum([1 for x in [self.receta_principal, self.sub_receta, self.ingrediente] if x is not None]) != 1:
            raise ValueError("Un ItemReceta debe estar asociado a una RecetaPrincipal, una SubReceta o un Ingrediente, y solo a uno.")
        super().save(*args, **kwargs)
# --- Modelos de Productos, Inventario y Órdenes de Compra ---
class Producto(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Nombre del Producto")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio de Venta")
    unidad_medida = models.ForeignKey(UnidadMedida, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Unidad de Medida de Venta")
    receta_principal = models.ForeignKey(RecetaPrincipal, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Receta Principal Asociada")
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True, verbose_name="Imagen del Producto")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='productos', null=True, blank=True, verbose_name="Empresa Asociada")
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name='productos', null=True, blank=True, verbose_name="Establecimiento Específico")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    objects = TenantAwareManager()
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        unique_together = ('nombre', 'empresa', 'establecimiento') # Producto único por nombre dentro de una empresa o establecimiento
    def __str__(self):
        return self.nombre
class ProductoProveedor(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='precios_proveedor', verbose_name="Producto")
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='productos_ofrecidos', verbose_name="Proveedor")
    precio_compra = models.DecimalField(max_digits=10, decimal_places=4, verbose_name="Precio de Compra")
    unidad_medida_compra = models.ForeignKey(UnidadMedida, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Unidad de Medida de Compra")
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Última Actualización de Precio")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='productos_proveedor', null=True, blank=True, verbose_name="Empresa Asociada")
    objects = TenantAwareManager()
    class Meta:
        verbose_name = "Producto por Proveedor"
        verbose_name_plural = "Productos por Proveedor"
        unique_together = ('producto', 'proveedor')
    def __str__(self):
        return f"{self.producto.nombre} de {self.proveedor.nombre}"
class InventarioEstablecimiento(models.Model):
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name='inventario', verbose_name="Establecimiento")
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE, verbose_name="Ingrediente")
    cantidad = models.DecimalField(max_digits=10, decimal_places=4, default=0.00, verbose_name="Cantidad en Stock")
    unidad_medida = models.ForeignKey(UnidadMedida, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Unidad de Medida")
    costo_promedio = models.DecimalField(max_digits=10, decimal_places=4, default=0.00, verbose_name="Costo Promedio Unitario")
    ultima_entrada = models.DateTimeField(auto_now=True, verbose_name="Última Entrada")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='inventario_establecimientos', null=True, blank=True, verbose_name="Empresa Asociada")
    objects = TenantAwareManager()
    class Meta:
        verbose_name = "Inventario por Establecimiento"
        verbose_name_plural = "Inventarios por Establecimiento"
        unique_together = ('establecimiento', 'ingrediente')
    def __str__(self):
        return f"{self.ingrediente.nombre} en {self.establecimiento.nombre}: {self.cantidad} {self.unidad_medida.abreviatura if self.unidad_medida else ''}"
class InventarioEmpresa(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='inventario_consolidado', verbose_name="Empresa")
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE, verbose_name="Ingrediente")
    cantidad_total = models.DecimalField(max_digits=10, decimal_places=4, default=0.00, verbose_name="Cantidad Total Consolidada")
    unidad_medida = models.ForeignKey(UnidadMedida, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Unidad de Medida")
    costo_promedio_ponderado = models.DecimalField(max_digits=10, decimal_places=4, default=0.00, verbose_name="Costo Promedio Ponderado")
    ultima_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización Consolidada")
    objects = TenantAwareManager()
    class Meta:
        verbose_name = "Inventario Consolidado por Empresa"
        verbose_name_plural = "Inventarios Consolidados por Empresa"
        unique_together = ('empresa', 'ingrediente')
    def __str__(self):
        return f"{self.ingrediente.nombre} (Consolidado {self.empresa.nombre}): {self.cantidad_total} {self.unidad_medida.abreviatura if self.unidad_medida else ''}"
class MovimientoInventario(models.Model):
    TIPO_MOVIMIENTO_CHOICES = (
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
        ('transferencia', 'Transferencia'),
    )
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE, verbose_name="Ingrediente")
    cantidad = models.DecimalField(max_digits=10, decimal_places=4, verbose_name="Cantidad")
    unidad_medida = models.ForeignKey(UnidadMedida, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Unidad de Medida")
    tipo_movimiento = models.CharField(max_length=20, choices=TIPO_MOVIMIENTO_CHOICES, verbose_name="Tipo de Movimiento")
    fecha_movimiento = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Movimiento")
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name="Costo Unitario en el Movimiento")
    establecimiento_origen = models.ForeignKey(Establecimiento, on_delete=models.SET_NULL, null=True, blank=True, related_name='movimientos_salida', verbose_name="Establecimiento Origen")
    establecimiento_destino = models.ForeignKey(Establecimiento, on_delete=models.SET_NULL, null=True, blank=True, related_name='movimientos_entrada', verbose_name="Establecimiento Destino")
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Registrado por")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='movimientos_inventario', null=True, blank=True, verbose_name="Empresa Asociada")
    objects = TenantAwareManager()
    class Meta:
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"
    def __str__(self):
        return f"{self.tipo_movimiento.capitalize()} de {self.cantidad} {self.ingrediente.nombre}"
class OrdenDeCompra(models.Model):
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    )
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='ordenes_compra', verbose_name="Proveedor")
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name='ordenes_compra', null=True, blank=True, verbose_name="Establecimiento Solicitante")
    fecha_orden = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Orden")
    fecha_entrega_esperada = models.DateField(null=True, blank=True, verbose_name="Fecha de Entrega Esperada")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente', verbose_name="Estado")
    total_orden = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total de la Orden")
    creada_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ordenes_compra_creadas', verbose_name="Creada por")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='ordenes_compra_empresa', null=True, blank=True, verbose_name="Empresa Asociada")
    objects = OrdenDeCompraManager() # Usar el manager específico
    class Meta:
        verbose_name = "Orden de Compra"
        verbose_name_plural = "Órdenes de Compra"
    def __str__(self):
        return f"OC-{self.id} a {self.proveedor.nombre} ({self.estado})"
class ItemOrdenDeCompra(models.Model):
    orden = models.ForeignKey(OrdenDeCompra, on_delete=models.CASCADE, related_name='items', verbose_name="Orden de Compra")
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Ingrediente")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Producto") # Para productos terminados de proveedor
    cantidad = models.DecimalField(max_digits=10, decimal_places=4, verbose_name="Cantidad")
    unidad_medida = models.ForeignKey(UnidadMedida, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Unidad de Medida")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=4, verbose_name="Precio Unitario Acordado")
    total_item = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total del Item")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='items_orden_compra', null=True, blank=True, verbose_name="Empresa Asociada")
    objects = TenantAwareManager()
    class Meta:
        verbose_name = "Item de Orden de Compra"
        verbose_name_plural = "Items de Órdenes de Compra"
        # Asegurar que solo uno de los campos (ingrediente, producto) esté lleno
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(ingrediente__isnull=False, producto__isnull=True) |
                    models.Q(ingrediente__isnull=True, producto__isnull=False)
                ),
                name='only_one_type_for_order_item'
            )
        ]
    def __str__(self):
        if self.ingrediente:
            return f"Item: {self.ingrediente.nombre} - Cant: {self.cantidad}"
        elif self.producto:
            return f"Item: {self.producto.nombre} - Cant: {self.cantidad}"
        return "Item de Orden de Compra (Sin tipo)"
    def save(self, *args, **kwargs):
        # Asegurar que solo uno de los campos de relación esté lleno
        if sum([1 for x in [self.ingrediente, self.producto] if x is not None]) != 1:
            raise ValueError("Un ItemOrdenDeCompra debe estar asociado a un Ingrediente o un Producto, y solo a uno.")
        super().save(*args, **kwargs)
# --- Modelos de Eventos ---
class Evento(models.Model):
    nombre_evento = models.CharField(max_length=255, verbose_name="Nombre del Evento")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción del Evento")
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name='eventos', verbose_name="Establecimiento Anfitrión")
    fecha_evento = models.DateField(verbose_name="Fecha del Evento")
    tipo_evento = models.CharField(max_length=100, blank=True, null=True, verbose_name="Tipo de Evento (Cena, Catering, etc.)")
    numero_invitados_esperado = models.IntegerField(null=True, blank=True, verbose_name="Número de Invitados Esperado")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='eventos_creados', verbose_name="Creado por")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='eventos_empresa', null=True, blank=True, verbose_name="Empresa Asociada")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    objects = TenantAwareManager()
    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        unique_together = ('nombre_evento', 'establecimiento', 'fecha_evento')
    def __str__(self):
        return f"{self.nombre_evento} en {self.establecimiento.nombre} el {self.fecha_evento}"
class EventoReceta(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='recetas_asociadas', verbose_name="Evento")
    receta_principal = models.ForeignKey(RecetaPrincipal, on_delete=models.CASCADE, related_name='eventos_asociados', verbose_name="Receta Principal")
    cantidad_a_preparar = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cantidad a Preparar")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='evento_recetas', null=True, blank=True, verbose_name="Empresa Asociada")
    objects = TenantAwareManager()
    class Meta:
        verbose_name = "Receta de Evento"
        verbose_name_plural = "Recetas de Eventos"
        unique_together = ('evento', 'receta_principal')
    def __str__(self):
        return f"{self.receta_principal.nombre} para {self.evento.nombre_evento}"
# --- Modelos de Alertas y Notificaciones ---
class Alerta(models.Model):
    TIPO_ALERTA_CHOICES = (
        ('stock_bajo', 'Stock Bajo'),
        ('orden_retrasada', 'Orden Retrasada'),
        ('inventario_alto', 'Inventario Alto'),
        ('nuevo_proveedor', 'Nuevo Proveedor'),
        ('otro', 'Otro'),
    )
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Establecimiento Relacionado")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Empresa Relacionada")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Usuario Relacionado")
    tipo_alerta = models.CharField(max_length=50, choices=TIPO_ALERTA_CHOICES, default='otro', verbose_name="Tipo de Alerta")
    mensaje = models.TextField(verbose_name="Mensaje de Alerta")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    leida = models.BooleanField(default=False, verbose_name="Leída")
    activa = models.BooleanField(default=True, verbose_name="Activa")
    objects = TenantAwareManager()
    class Meta:
        verbose_name = "Alerta"
        verbose_name_plural = "Alertas"
        ordering = ['-fecha_creacion']
    def __str__(self):
        return f"Alerta ({self.tipo_alerta}): {self.mensaje[:50]}..."
class IngredienteCambioCorporativo(models.Model):
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE, verbose_name="Ingrediente")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='cambios_corporativos_ingrediente', verbose_name="Empresa")
    costo_anterior = models.DecimalField(max_digits=10, decimal_places=4, verbose_name="Costo Anterior")
    costo_nuevo = models.DecimalField(max_digits=10, decimal_places=4, verbose_name="Costo Nuevo")
    fecha_cambio = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Cambio")
    realizado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Realizado por")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")
    objects = TenantAwareManager()
    class Meta:
        verbose_name = "Cambio Corporativo de Ingrediente"
        verbose_name_plural = "Cambios Corporativos de Ingredientes"
        ordering = ['-fecha_cambio']
    def __str__(self):
        return f"Cambio de costo para {self.ingrediente.nombre} en {self.empresa.nombre}: de {self.costo_anterior} a {self.costo_nuevo}"
# --- Signals ---
# Señal para asegurar que la empresa en Establecimiento se setee correctamente al guardar
@receiver(post_save, sender=Establecimiento)
def set_establecimiento_empresa(sender, instance, created, **kwargs):
    if created and not instance.empresa:
        # Esto solo se ejecutaría si Establecimiento se crea sin empresa,
        # lo cual no debería pasar si el campo 'empresa' es requerido.
        # Si 'empresa' es opcional y se deduce de otro lado, aquí iría la lógica.
        pass
# Señal para asegurar que la empresa en InventarioEstablecimiento se setee correctamente al guardar
@receiver(post_save, sender=InventarioEstablecimiento)
def set_inventarioestablecimiento_empresa(sender, instance, created, **kwargs):
    if created or not instance.empresa:
        if instance.establecimiento and instance.establecimiento.empresa:
            instance.empresa = instance.establecimiento.empresa
            instance.save(update_fields=['empresa'])
# Señal para asegurar que la empresa en OrdenDeCompra se setee correctamente al guardar
@receiver(post_save, sender=OrdenDeCompra)
def set_ordendecompra_empresa(sender, instance, created, **kwargs):
    if created or not instance.empresa:
        if instance.establecimiento and instance.establecimiento.empresa:
            instance.empresa = instance.establecimiento.empresa
            instance.save(update_fields=['empresa'])
# Señal para asegurar que la empresa en ItemOrdenDeCompra se setee correctamente al guardar
@receiver(post_save, sender=ItemOrdenDeCompra)
def set_itemordencompra_empresa(sender, instance, created, **kwargs):
    if created or not instance.empresa:
        if instance.orden and instance.orden.empresa:
            instance.empresa = instance.orden.empresa
            instance.save(update_fields=['empresa'])
        elif instance.orden and instance.orden.establecimiento and instance.orden.establecimiento.empresa:
            instance.empresa = instance.orden.establecimiento.empresa
            instance.save(update_fields=['empresa'])
# Señal para asegurar que la empresa en Evento se setee correctamente al guardar
@receiver(post_save, sender=Evento)
def set_evento_empresa(sender, instance, created, **kwargs):
    if created or not instance.empresa:
        if instance.establecimiento and instance.establecimiento.empresa:
            instance.empresa = instance.establecimiento.empresa
            instance.save(update_fields=['empresa'])
# Señal para asegurar que la empresa en ItemReceta se setee correctamente al guardar
@receiver(post_save, sender=ItemReceta)
def set_itemreceta_empresa(sender, instance, created, **kwargs):
    if created or not instance.empresa:
        if instance.receta_principal and instance.receta_principal.empresa:
            instance.empresa = instance.receta_principal.empresa
            instance.save(update_fields=['empresa'])
        elif instance.sub_receta and instance.sub_receta.empresa:
            instance.empresa = instance.sub_receta.empresa
            instance.save(update_fields=['empresa'])
        elif instance.ingrediente and instance.ingrediente.empresa:
            instance.empresa = instance.ingrediente.empresa
            instance.save(update_fields=['empresa'])
# Señal para asegurar que la empresa en Producto se setee correctamente al guardar
@receiver(post_save, sender=Producto)
def set_producto_empresa(sender, instance, created, **kwargs):
    if created or not instance.empresa:
        if instance.establecimiento and instance.establecimiento.empresa:
            instance.empresa = instance.establecimiento.empresa
            instance.save(update_fields=['empresa'])
        elif instance.empresa: # Si la empresa ya está seteada directamente en el producto
            pass
        else: # Si no tiene establecimiento ni empresa, intentar derivar de la receta principal si existe
            if instance.receta_principal and instance.receta_principal.empresa:
                instance.empresa = instance.receta_principal.empresa
                instance.save(update_fields=['empresa'])