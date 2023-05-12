from decouple import config
import os


from django.core.wsgi import get_wsgi_application

os.environ.setdefault(
        'DJANGO_SETTINGS_MODULE', 
        f'idea_jet.settings.{config("DJANGO_SETTINGS_ENV")}'
    )

application = get_wsgi_application()
