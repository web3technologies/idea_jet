from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from idea_jet_business.views import LandingPageView, LoginView


urlpatterns = [
    path('', LandingPageView.as_view(), name="landing_page"),
    path('login/', LoginView.as_view(), name='login'),
    path('admin/', admin.site.urls),
    path("auth/", include("idea_jet_auth.urls")),
    path("async/", include("idea_jet_async.urls")),
    path("business-idea/", include("idea_jet_business.urls"))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
