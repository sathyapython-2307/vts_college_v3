import os
import sys
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from a local .env file during development
# This allows settings like DEBUG=true from .env to take effect when running locally.
try:
    from dotenv import load_dotenv
    # Prefer a project root .env if present
    load_dotenv(os.path.join(BASE_DIR, '.env'))
except Exception:
    # If python-dotenv is not available, continue without loading .env
    pass

# SECURITY WARNING: keep the secret key used in production secret!
# Prefer an explicit SECRET_KEY from the environment in production.
# Behavior:
# - If DEBUG=True, use a safe development fallback.
# - If DEBUG=False and SECRET_KEY is provided in the environment, use it.
# - If DEBUG=False and SECRET_KEY is missing, but we're running on Render (or
#   SECRET_KEY auto-generation is enabled), generate a secure key at startup so
#   the app can boot. This avoids an immediate crash during deploys where the
#   secret wasn't configured. Note: generated keys are ephemeral (per instance)
#   and will invalidate existing sessions across restarts.
from pathlib import Path as _Path
import secrets as _secrets

_secret_from_env = os.environ.get('SECRET_KEY')
_debug_env = os.environ.get('DEBUG', 'False').lower() == 'true'

if _secret_from_env:
    SECRET_KEY = _secret_from_env
else:
    if _debug_env:
        # Development fallback - NEVER use this in production
        SECRET_KEY = 'django-insecure-dev-key-only-for-local-development-change-this'
    else:
        # In production: try to auto-generate a secret when running on Render
        # or when auto-generation is explicitly enabled. This guarantees the
        # process can start even if the environment was not configured, which
        # is useful for automated deploys. Prefer setting SECRET_KEY in the
        # environment for a stable secret across restarts.
        _running_on_render = bool(os.environ.get('RENDER_EXTERNAL_HOSTNAME') or os.environ.get('RENDER'))
        _auto_generate = os.environ.get('SECRET_KEY_AUTO_GENERATE', 'true').lower() == 'true'

        if _running_on_render or _auto_generate:
            # Attempt to persist the generated key to a file on the instance so
            # subsequent process restarts on the same instance reuse it. This
            # won't survive deploys, but reduces churn for a single instance.
            try:
                _secret_file = _Path(BASE_DIR) / '.secret_key'
                if _secret_file.exists():
                    SECRET_KEY = _secret_file.read_text().strip()
                else:
                    SECRET_KEY = _secrets.token_urlsafe(64)
                    try:
                        _secret_file.write_text(SECRET_KEY)
                        # Restrict permissions when possible (POSIX only)
                        try:
                            os.chmod(_secret_file, 0o600)
                        except Exception:
                            pass
                    except Exception:
                        # If writing fails, fall back to in-memory secret
                        SECRET_KEY = SECRET_KEY
            except Exception:
                # As a last resort generate an in-memory secret so the app boots
                SECRET_KEY = _secrets.token_urlsafe(64)
            # Warn in logs so operators know a generated secret is in use
            print('Warning: SECRET_KEY was not set; a key was generated at startup. For production set SECRET_KEY in the environment to ensure stability.')
        else:
            raise ValueError('SECRET_KEY environment variable is required in production')

# SECURITY WARNING: don't run with debug turned on in production!
# Default to False unless explicitly set via environment/.env
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Ensure local development using manage.py runserver does not enforce HTTPS.
# This avoids browser auto-upgrade/HSTS loops during local testing.
if 'runserver' in sys.argv or 'runserver_plus' in sys.argv:
    DEBUG = True

# Parse ALLOWED_HOSTS from environment variable or use defaults
ALLOWED_HOSTS_STR = os.environ.get('ALLOWED_HOSTS', '')
if ALLOWED_HOSTS_STR:
    ALLOWED_HOSTS = [h.strip() for h in ALLOWED_HOSTS_STR.split(',') if h.strip()]
else:
    # In development, allow a few handy loopback hostnames that map to 127.0.0.1
    # This helps if your browser has cached HSTS for localhost/127.0.0.1.
    ALLOWED_HOSTS = [
        'localhost',
        '127.0.0.1',
        'testserver',
        'lvh.me',              # lvh.me resolves to 127.0.0.1
        'localtest.me',        # localtest.me resolves to 127.0.0.1
        '127.0.0.1.nip.io',    # nip.io wildcard resolves to the embedded IP
    ]

# Add Render domain if present
RENDER_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_HOSTNAME)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',  # Make sure this is included
    'whitenoise.runserver_nostatic',  # Add WhiteNoise
    'core',  # Your app
]

# Development helper apps (added only if installed)
try:
    import django_extensions  # noqa: F401
    INSTALLED_APPS.append('django_extensions')
except Exception:
    # If not installed, skip silently (keeps production clean)
    pass

# Build middleware list. In development (DEBUG=True) we avoid inserting
# SecurityMiddleware so that local runserver never enforces HTTPS or HSTS.
_middleware = [
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add WhiteNoise middleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if not DEBUG:
    # Only enable the SecurityMiddleware in production where SECURE_* settings apply
    MIDDLEWARE = ['django.middleware.security.SecurityMiddleware'] + _middleware
else:
    # During local development we may encounter CSRF token mismatches caused by
    # alternate hostnames, tools, or rapid login/logout cycles. To make local
    # development friction-free, remove the CSRF middleware when DEBUG=True.
    # NOTE: This is ONLY for local development. Do NOT enable this in
    # production environments. If you need stricter diagnostics, re-enable the
    # middleware and follow the debug steps in the project README.
    dev_middleware = [m for m in _middleware if m != 'django.middleware.csrf.CsrfViewMiddleware']
    MIDDLEWARE = dev_middleware

ROOT_URLCONF = 'Online_Course.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

# Database configuration for Render
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Import dj_database_url only when DATABASE_URL is provided so local
    # environments without the package installed won't fail during manage
    # commands like collectstatic.
    try:
        import dj_database_url
    except ImportError:
        from django.core.exceptions import ImproperlyConfigured
        raise ImproperlyConfigured(
            'DATABASE_URL is set but dj_database_url is not installed. '
            'Install dj-database-url or unset DATABASE_URL.'
        )

    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Security Settings - Production only (disabled in DEBUG mode for local dev)
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0  # 1 year in production
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
# Session & CSRF cookie security
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# If the app is behind a proxy (like Render's router), trust the X-Forwarded-Proto
# header so Django can infer the original scheme and correctly build redirect URLs.
# Only enable this in production (when DEBUG=False).
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # Add Render hostname to CSRF trusted origins so CSRF checks succeed for HTTPS requests
    CSRF_TRUSTED_ORIGINS = []
    if RENDER_HOSTNAME:
        CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_HOSTNAME}')
else:
    SECURE_PROXY_SSL_HEADER = None
    # In development, be permissive for common loopback origins so tools
    # and alternate hostnames (localhost, 127.0.0.1) don't trigger CSRF
    # failures when accessing the dev server on different hostnames/ports.
    CSRF_TRUSTED_ORIGINS = [
        'http://localhost',
        'http://localhost:8000',
        'http://127.0.0.1',
        'http://127.0.0.1:8000',
        'http://0.0.0.0',
        'http://0.0.0.0:8000',
    ]

# Additional security settings
SECURE_BROWSER_XSS_FILTER = not DEBUG
X_FRAME_OPTIONS = 'DENY' if not DEBUG else 'SAMEORIGIN'
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
    "script-src": (
        "'self'",
        "cdn.jsdelivr.net",
        "cdnjs.cloudflare.com",
    ),
    "style-src": (
        "'self'",
        "'unsafe-inline'",
        "cdn.jsdelivr.net",
        "cdnjs.cloudflare.com",
    ),
    "img-src": (
        "'self'",
        "data:",
    ),
    "font-src": (
        "'self'",
        "cdnjs.cloudflare.com",
    ),
} if not DEBUG else {}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

# WhiteNoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_MANIFEST_STRICT = False

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication settings
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# First check if razorpay is available
try:
    import razorpay  # noqa: F401
    RAZORPAY_PACKAGE_AVAILABLE = True
except ImportError:
    print('Warning: razorpay package not installed. Install it with: pip install razorpay')
    RAZORPAY_PACKAGE_AVAILABLE = False

# Razorpay Configuration
RAZORPAY_SETTINGS = {
    'ENABLED': os.environ.get('RAZORPAY_ENABLED', 'true').lower() == 'true',
    'KEY_ID': os.environ.get('RAZORPAY_KEY_ID'),
    'KEY_SECRET': os.environ.get('RAZORPAY_KEY_SECRET'),
    'CURRENCY': os.environ.get('RAZORPAY_CURRENCY', 'INR')
}

# Direct settings for easier access in views
RAZORPAY_ENABLED = RAZORPAY_PACKAGE_AVAILABLE and RAZORPAY_SETTINGS['ENABLED']
RAZORPAY_KEY_ID = RAZORPAY_SETTINGS['KEY_ID']
RAZORPAY_KEY_SECRET = RAZORPAY_SETTINGS['KEY_SECRET']
RAZORPAY_CURRENCY = RAZORPAY_SETTINGS['CURRENCY']

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}