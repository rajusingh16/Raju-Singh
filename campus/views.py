from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Room
from .serializers import RoomListSerializer


class RoomListView(generics.ListAPIView):
    """
    Read-only DRF API returning campus rooms with floor_level, building_code,
    and spatial coordinates (x, y, z in metres).
    Supports filtering by ?floor_level=0 and ?building_code=MAIN.
    """
    serializer_class = RoomListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Room.objects.filter(is_active=True).select_related(
            "floor", "floor__building", "floor__building__campus"
        )
        floor_level = self.request.query_params.get("floor_level")
        building_code = self.request.query_params.get("building_code")

        if floor_level is not None:
            queryset = queryset.filter(floor__level=floor_level)
        if building_code:
            queryset = queryset.filter(floor__building__code__iexact=building_code)

        return queryset
