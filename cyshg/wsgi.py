"""
WSGI config for cyshg project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os, sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cyshg.settings")
os.environ['HTTPS'] = "on"

#sys.path.append('/home/p6n/workplace/website/cyshg')
sys.path.append('/home/p6n/tools/myPythonLib')


application = get_wsgi_application()
