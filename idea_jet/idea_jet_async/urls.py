from rest_framework import routers

from idea_jet_async.views import TaskResultViewset


router = routers.SimpleRouter()

router.register(r"task-results", TaskResultViewset)

urlpatterns = []

urlpatterns += router.urls