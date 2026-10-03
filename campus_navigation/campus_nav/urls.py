from django.contrib import admin
from django.urls import path

from tracker import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path("floorplan/", views.floorplan, name="floorplan"),
    path("api/bootstrap/", views.BootstrapAPIView.as_view(), name="api-bootstrap"),
    path("api/rooms/search/", views.RoomSearchAPIView.as_view(), name="api-room-search"),
    path("api/route/", views.RouteAPIView.as_view(), name="api-route"),
    path("api/qr/<str:code>/", views.QRLocationAPIView.as_view(), name="api-qr"),
]
