# tochinalli_project/ixcaui_project/urls.py

from django.contrib import admin
from django.urls import path, include
from ixcaui_app.views import home_view, select_establecimiento_view, producto_list_create_view # Asegúrate de importar producto_list_create_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('ixcaui_app.urls')), # Asumiendo que 'ixcaui_app.urls' contiene las URLs de la API y no las de la web principal

    # URLs de autenticación de Django que usan tus vistas personalizadas de login/logout
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # URLs de autenticación de Django RESTANTES.
    # Es crucial que estas NO interfieran con tu flujo LOGIN_REDIRECT_URL = 'home'.
    # La URL 'accounts/profile/' de Django por defecto ya no nos afectará si LOGIN_REDIRECT_URL apunta a 'home'.
    # Mantenemos esto por si necesitas otras URLs de auth de Django como password_change, etc.
    path('accounts/', include('django.contrib.auth.urls')),

    # ESTA LÍNEA DEBE SER ELIMINADA O COMENTADA.
    # Ya no la necesitas si LOGIN_REDIRECT_URL apunta directamente a 'home'.
    # path('accounts/profile/', custom_login_redirect, name='custom_login_redirect'),

    # Tus otras URLs principales
    path('', home_view, name='home'),
    path('select-establecimiento/', select_establecimiento_view, name='select_establecimiento'),

    # URL para la creación/listado de productos
    path('productos/crear/', producto_list_create_view, name='crear_producto'), # Corregido: usa producto_list_create_view

    # URLs para restablecimiento de contraseña (si las necesitas)
    # Estas también pueden ser cubiertas por path('accounts/', include('django.contrib.auth.urls'))
    # si no necesitas personalizarlas individualmente. Pero las mantenemos explícitas aquí.
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    # Opcional: Si tienes URLs específicas para tu aplicación 'ixcaui_app' que no son la API principal
    # path('app/', include('ixcaui_app.urls')), # Descomentar si tienes un archivo ixcaui_app/urls.py para URLs de la app

]