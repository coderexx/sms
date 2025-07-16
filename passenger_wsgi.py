import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
# Import the application object
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()