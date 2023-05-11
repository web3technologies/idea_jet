from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path("auth/", include("idea_jet_auth.urls")),
    path("business-idea/", include("idea_jet_business.urls"))
]
