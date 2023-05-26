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

CELERY_BROKER_URL = f'sqs://{config("AWS_ACCESS_KEY_ID")}:{config("AWS_SECRET_ACCESS_KEY")}@'