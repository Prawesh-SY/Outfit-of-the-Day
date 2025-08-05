from rest_framework import viewsets
from .models import Title
from .serializers import TitleSerializer

class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.select_related().all().prefetch_related('occasions','styles','colors','accessories','footwears','outfit_images')
    serializer_class = TitleSerializer