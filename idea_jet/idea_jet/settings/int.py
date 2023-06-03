from idea_jet.settings.settings import *

DEBUG = False

APP_URL = "https://int.app.ideajet.ai"

CORS_ORIGIN_WHITELIST = [
    "https://idea-jet-web.vercel.app",
    APP_URL
]

MEDIA_ROOT = "/applications/idea_jet_media/"
STATIC_ROOT = f"/applications/idea_jet/static/"   #collectstatic places all files found here in prod
STATICFILES_DIRS = [
    os.path.join("/applications/idea_jet/", "venv/lib/python3.10/site-packages/idea_jet_static"),
    os.path.join("/applications/idea_jet/", "venv/lib/python3.10/site-packages/idea_jet_business/templates/idea_jet_business/")
]

CELERY_WORKER_DISABLE_REMOTE_CONTROL = True
CELERY_BROKER_URL = "sqs://"
CELERY_TASK_DEFAULT_QUEUE = 'idea_jet_int'
CELERY_TASK_DEFAULT_EXCHANGE = 'idea_jet_int'
CELERY_TASK_DEFAULT_ROUTING_KEY = 'idea_jet_int'


CELERY_BROKER_TRANSPORT_OPTIONS = {
    'region': 'us-east-2',
    'predefined_queues': {
        'idea_jet_int': {
            'url': 'https://sqs.us-east-2.amazonaws.com/490305332793/idea_jet_int',
        },
        # 'celery.pidbox': {
        #     'url': 'https://sqs.us-east-2.amazonaws.com/490305332793/celery.pidbox',
        # },
        # Add other special queues as needed...
    },
    'visibility_timeout': 3600,
    'polling_interval': 5.0,
    'queue_name_prefix': '',
}
