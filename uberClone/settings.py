import os
from pathlib import Path
from corsheaders.defaults import default_headers

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'u43tz3dz834t%=44cx^1pwqi293efec^_u0=w1f-*m!ln4_3rd'
REFRESH_SECRET_KEY = '0z-yx764r0qk+b3zp#erzeka7@32q9bzv^7h&c8d%+@3^o@de@'

DEBUG = True

blackListedTokens = set()
idle_drivers = {}
ride_otps = {}
cancelled_ride = {}

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'uber-clone-v1.onrender.com',
    'uber-clone-v1.up.railway.app',
    'cab-app-api.up.railway.app'
]

INSTALLED_APPS = [
    'daphne',
    'user',
    'trip',
    'driver',
    'ride',
    'corsheaders',
    'rest_framework',
    'drf_spectacular',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'corsheaders.middleware.CorsPostCsrfMiddleware',
]

ROOT_URLCONF = 'uberClone.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'uberClone.wsgi.application'
ASGI_APPLICATION = 'uberClone.routing.application'
DATABASES = {
    'default': {
        # 'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_UC_NAME', 'db_uberclone'),
        'PORT': os.getenv('DB_UC_PORT', '5432'),
        'HOST': os.getenv('DB_UC_HOST_URL', 'localhost'),
        'USER': os.getenv('DB_UC_USERNAME', 'postgres'),
        'PASSWORD': os.getenv('DB_UC_PASSWORD', 'super'),
        'OPTIONS': {
            'sslmode': 'require'
        }
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

# USE_L10N = True

USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# STATICFILES_DIR = [os.path.join(BASE_DIR, "static")]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'user.User'

# CSRF_COOKIE_DOMAIN = 'uberclone.onrender.com'
# CSRF_COOKIE_SECURE = True
# CSRF_COOKIE_SAMESITE = 'None'
# SESSION_COOKIE_SAMESITE = 'None'
# SESSION_COOKIE_SAMESITE_FORCE_ALL = True
SESSION_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://uber-clone-v1.onrender.com',
    'https://uber-clone-v1.up.railway.app',
    'https://cab-app-api.up.railway.app/'
]

CORS_ORIGIN_WHITELIST = [
    'http://localhost',
    'http://localhost:8000',
    'http://127.0.0.1',
    'http://127.0.0.1:8000',
    'https://uber-clone-v1.onrender.com',
    'https://uber-clone-v1.up.railway.app',
    'https://cab-app-api.up.railway.app'
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = list(default_headers) + [
    'refreshtoken',
    'Cookie',
    'Set-Cookie',
    'X-CSRFToken',
    'Authentication',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'user.authentication.SafeJWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'EXCEPTION_HANDLER': 'user.utils.custom_exception_handler',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema'
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Uber Clone API',
    'DESCRIPTION': 'The backend created for uber clone project consisting of both http endpoints and websocket '
                   'endpoints. This doc is provided for those http endpoints.',
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        # 'BACKEND': 'channels.layers.InMemoryChannelLayer',
        'CONFIG': {
            "hosts": [os.environ.get('UC_REDIS_URL', 'redis://localhost:6379')],
        },
    },
}

CACHES = {
    "default": {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': [os.environ.get('UC_REDIS_URL', 'redis://localhost:6379')],
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient'
        }
    }
}
