from django.db.models import Q
from django.shortcuts import redirect, render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Department, Floor, NavigationEdge, NavigationPoint, QRLocation, Room
from .pathfinding import shortest_path
from .serializers import (
    DepartmentSerializer,
    FloorSerializer,
    NavigationEdgeSerializer,
    NavigationPointSerializer,
    RoomSerializer,
)


def index(request):
    return render(request, "index.html", {"initial_view": request.GET.get("view", "3d")})


def floorplan(request):
    return redirect("/?view=2d")


class BootstrapAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        floors = Floor.objects.select_related("campus").all()
        rooms = Room.objects.select_related("floor", "department", "navigation_point").all()
        points = NavigationPoint.objects.select_related("floor").all()
        edges = NavigationEdge.objects.select_related("start_point", "end_point").all()
        departments = Department.objects.select_related("floor").all()
        qr_locations = QRLocation.objects.select_related("navigation_point").all()
        first_floor = floors.first()
        return Response(
            {
                "campus": {
                    "name": first_floor.campus.name if first_floor else "GWCET",
                    "code": first_floor.campus.code if first_floor else "GWCET",
                },
                "floors": FloorSerializer(floors, many=True).data,
                "rooms": RoomSerializer(rooms, many=True).data,
                "navigation_points": NavigationPointSerializer(points, many=True).data,
                "edges": NavigationEdgeSerializer(edges, many=True).data,
                "departments": DepartmentSerializer(departments, many=True).data,
                "qr_locations": [
                    {
                        "code": qr.code,
                        "label": qr.label,
                        "navigation_point": qr.navigation_point.code,
                    }
                    for qr in qr_locations
                ],
            }
        )


class RoomSearchAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        query = request.GET.get("q", "").strip()
        category = request.GET.get("category", "").strip().upper()
        rooms = Room.objects.select_related("floor", "department", "navigation_point").filter(is_active=True)
        if query:
            rooms = rooms.filter(
                Q(name__icontains=query)
                | Q(room_code__icontains=query)
                | Q(aliases__icontains=query)
                | Q(department__name__icontains=query)
                | Q(department__short_code__icontains=query)
            )
        if category:
            rooms = rooms.filter(room_type=category)
        return Response({"results": RoomSerializer(rooms[:30], many=True).data})


class RouteAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        accessible = request.data.get("accessible", False)
        if isinstance(accessible, str):
            accessible = accessible.strip().lower() in {"1", "true", "yes", "on"}
        else:
            accessible = bool(accessible)
        try:
            result = shortest_path(
                request.data.get("start"),
                request.data.get("destination"),
                accessible,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "start": result["start"].code,
                "destination": result["goal"].code,
                "distance_metres": result["distance"],
                "estimated_minutes": max(1, round(result["distance"] / 65)),
                "accessible": result["accessible"],
                "points": NavigationPointSerializer(result["points"], many=True).data,
                "instructions": [point.name for point in result["points"]],
            }
        )


class QRLocationAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, code):
        qr = QRLocation.objects.select_related("navigation_point__floor").filter(code=code).first()
        if not qr:
            return Response({"detail": "Unknown campus QR code."}, status=status.HTTP_404_NOT_FOUND)
        return Response(
            {
                "code": qr.code,
                "label": qr.label,
                "navigation_point": NavigationPointSerializer(qr.navigation_point).data,
            }
        )
