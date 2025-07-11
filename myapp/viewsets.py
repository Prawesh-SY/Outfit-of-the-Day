from rest_framework import viewsets
from .models import Title
from .serializers import TitleSerializer

class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer