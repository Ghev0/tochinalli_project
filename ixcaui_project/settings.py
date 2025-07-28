# tochinalli_project/ixcaui_project/settings.py

from pathlib import Path
import os
from decouple import config
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# -- INICIO DE LAS CONFIGURACIONES CRÍTICAS --
ALLOWED_HOSTS = [
    '*', # Permite todas las URLs de host para desarrollo en Codespaces
    'improved-winner-x5499vxpxwg4297rp.github.dev' # Tu dominio específico de Codespaces
]

# CSRF_TRUSTED_ORIGINS es crucial para los POST requests desde URLs de Codespaces
CSRF_TRUSTED_ORIGINS = [
    'https://*.github.dev', # Cubre subdominios dinámicos de Codespaces (por ejemplo, https://improved-winner-x5499vxpxwg4297rp.github.dev)
    'https://localhost:8000', # MUY IMPORTANTE: Para el error "Origin checking failed - https://localhost:8000"
    'http://localhost:8000', # Para desarrollo local puro (HTTP)
    'http://127.0.0.1:8000', # Para desarrollo local puro (HTTP)
    'https://improved-winner-x5499vxpxwg4297rp.github.dev', # Tu dominio específico de Codespaces (HTTPS)
]
# -- FIN DE LAS CONFIGURACIONES CRÍTICAS --


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',

    # Tus aplicaciones personalizadas:
    'ixcaui_app',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    'ixcaui_app.middleware.RequestMiddleware', # <-- Asegúrate de que esté después de AuthenticationMiddleware
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ixcaui_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'ixcaui_project' / 'templates'], # ¡Añadimos esta ruta!
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.static",
            ],
        },
    },
]

WSGI_APPLICATION = "ixcaui_project.wsgi.application"


# Database
DATABASES = {
    'default': dj_database_url.parse(config('DATABASE_URL'))
}

# Configuración para Supabase
SUPABASE_URL = config('SUPABASE_URL')
SUPABASE_KEY = config('SUPABASE_KEY')
SUPABASE_JWKS_URL = os.environ.get("SUPABASE_JWKS_URL")


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
LANGUAGE_CODE = "es-mx"
TIME_ZONE = "America/Mexico_City"
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'ixcaui_project', 'static'),
]

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Usamos el modelo de usuario personalizado de tu app ixcaui_app
AUTH_USER_MODEL = 'ixcaui_app.User'

ACCOUNT_ACTIVATION_DAYS = 7

# Configuración para Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# Aquí se define el backend de autenticación de Django
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Configuración de sesión para manejar el Establecimiento Activo
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_NAME = 'tochinalli_sessionid'
SESSION_SAVE_EVERY_REQUEST = True
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'