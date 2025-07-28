# tochinalli_project/ixcaui_app/forms.py

from django import forms
from .models import Producto, Empresa, Establecimiento, UnidadMedida # Asegúrate de importar todos los modelos necesarios

class ProductoForm(forms.ModelForm):
    # Campos adicionales si un superusuario necesita seleccionar empresa/establecimiento
    # Para usuarios normales (empresa), estos campos pueden ser ocultos o pre-llenados en la vista
    empresa_asociada = forms.ModelChoiceField(queryset=Empresa.objects.all(), required=False, label="Empresa Asociada")
    establecimiento = forms.ModelChoiceField(queryset=Establecimiento.objects.all(), required=False, label="Establecimiento Específico")

    class Meta:
        model = Producto
        # Incluye todos los campos que quieres que se puedan editar en el formulario
        fields = [
            'nombre', 'descripcion', 'precio_venta', 'unidad_medida',
            'receta_principal', 'imagen', 'activo',
            # 'empresa_asociada', 'establecimiento' (estos se manejan por separado para control de visibilidad)
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None) # Obtén el request si se pasa
        super().__init__(*args, **kwargs)

        # Ajustar los querysets y visibilidad de los campos 'empresa_asociada' y 'establecimiento'
        user = self.request.user if self.request else None
        
        if user and user.is_superuser:
            # Superusuarios pueden seleccionar cualquier empresa o establecimiento
            self.fields['empresa_asociada'].required = True # Fuerza a superusuario a seleccionar una empresa
            self.fields['establecimiento'].required = False
            self.fields['establecimiento'].queryset = Establecimiento.objects.all()
        elif user and user.tipo_usuario == 'empresa' and user.empresa_asociada:
            # Usuarios de empresa no ven estos campos en el form, se llenan automáticamente
            del self.fields['empresa_asociada']
            self.fields['establecimiento'].queryset = user.empresa_asociada.establecimientos.all()
            if user.restringido_a_establecimiento and user.establecimiento_asociado:
                # Si el usuario empresa está restringido a un establecimiento, solo puede asignar a ese
                self.fields['establecimiento'].queryset = Establecimiento.objects.filter(id=user.establecimiento_asociado.id)
                self.fields['establecimiento'].initial = user.establecimiento_asociado # Preseleccionar
                self.fields['establecimiento'].widget = forms.HiddenInput() # O hacer readonly
            self.fields['establecimiento'].required = False # Puede ser un producto de empresa (sin establecimiento)
        else:
            # Para otros usuarios (proveedor, anónimo), no deberían crear productos
            # O puedes decidir mostrar estos campos de forma diferente
            del self.fields['empresa_asociada']
            del self.fields['establecimiento']

    def clean(self):
        cleaned_data = super().clean()
        user = self.request.user if self.request else None

        # Si el usuario es empresa y tiene establecimiento activo, asegurarse de que coincidan.
        # Esto es más bien una validación a nivel de vista o save.
        # Aquí en el form, si un establecimiento fue seleccionado, debe pertenecer a la empresa asociada.
        establecimiento = cleaned_data.get('establecimiento')
        empresa_asociada_form = cleaned_data.get('empresa_asociada') # Para superusuarios

        if user and user.tipo_usuario == 'empresa' and user.empresa_asociada:
            if establecimiento and establecimiento.empresa != user.empresa_asociada:
                self.add_error('establecimiento', 'El establecimiento seleccionado no pertenece a tu empresa.')
        elif user and user.is_superuser and empresa_asociada_form:
            if establecimiento and establecimiento.empresa != empresa_asociada_form:
                self.add_error('establecimiento', 'El establecimiento seleccionado no pertenece a la empresa que asociaste.')
        
        return cleaned_data