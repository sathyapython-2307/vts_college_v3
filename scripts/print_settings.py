import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Online_Course.settings')
try:
    django.setup()
    from django.conf import settings
    print('DEBUG =', getattr(settings, 'DEBUG', None))
    print('SECURE_SSL_REDIRECT =', getattr(settings, 'SECURE_SSL_REDIRECT', None))
    print('SECURE_HSTS_SECONDS =', getattr(settings, 'SECURE_HSTS_SECONDS', None))
    print('SESSION_COOKIE_SECURE =', getattr(settings, 'SESSION_COOKIE_SECURE', None))
    print('CSRF_COOKIE_SECURE =', getattr(settings, 'CSRF_COOKIE_SECURE', None))
    print('RAZORPAY_SETTINGS =', getattr(settings, 'RAZORPAY_SETTINGS', None))
    print('RAZORPAY_ENABLED =', getattr(settings, 'RAZORPAY_ENABLED', None))
    print('RAZORPAY_KEY_ID =', getattr(settings, 'RAZORPAY_KEY_ID', None))
    print('RAZORPAY_KEY_SECRET present =', bool(getattr(settings, 'RAZORPAY_KEY_SECRET', None)))
except Exception as e:
    print('ERROR:', e)
    sys.exit(1)
