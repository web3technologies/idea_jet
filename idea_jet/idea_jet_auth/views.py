from rest_framework.viewsets import ModelViewSet

from idea_jet_auth.serializers import UserSerializer
from django.contrib.auth import get_user_model


class UserView(ModelViewSet):

    serializer_class = UserSerializer
    user_model = get_user_model()

    def get_object(self, *args, **kwargs):
        return self.user_model.objects.get(id=self.request.user.id)