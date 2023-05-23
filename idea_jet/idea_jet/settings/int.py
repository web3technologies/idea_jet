from idea_jet.settings.settings import *

DEBUG = False

CORS_ORIGIN_WHITELIST = [
    "https://idea-jet-web.vercel.app",
    "https://int.app.ideajet.ai"
]

MEDIA_ROOT = "/applications/idea_jet_media/"
STATIC_ROOT = f"/applications/idea_jet/static/"   #collectstatic places all files found here in prod
STATICFILES_DIRS = [
    os.path.join("/applications/idea_jet/", "venv/lib/python3.10/site-packages/idea_jet_static"),
    os.path.join("/applications/idea_jet/", "venv/lib/python3.10/site-packages/idea_jet_business/templates/idea_jet_business/")
]