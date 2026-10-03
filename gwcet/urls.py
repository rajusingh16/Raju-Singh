"""
URL configuration for gwcet project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from campus.views import RoomListView
from tracker import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path("floorplan/", views.floorplan, name="floorplan"),
    path("api/rooms/", RoomListView.as_view(), name="api-rooms"),
    path("api/bootstrap/", views.BootstrapAPIView.as_view(), name="api-bootstrap"),
    path("api/rooms/search/", views.RoomSearchAPIView.as_view(), name="api-room-search"),
    path("api/route/", views.RouteAPIView.as_view(), name="api-route"),
    path("api/qr/<str:code>/", views.QRLocationAPIView.as_view(), name="api-qr"),
]