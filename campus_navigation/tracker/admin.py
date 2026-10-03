from django.contrib import admin

from .models import (
    Campus, Department, Floor, LocationShare, NavigationEdge,
    NavigationPoint, QRLocation, Room, UserLocation,
)


@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "latitude", "longitude")


@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    list_display = ("name", "campus", "level", "elevation", "floor_height")
    list_filter = ("campus",)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("short_code", "name", "floor")
    search_fields = ("short_code", "name")


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("room_code", "name", "room_type", "floor", "wing", "is_active")
    list_filter = ("floor", "room_type", "wing", "is_active")
    search_fields = ("room_code", "name", "aliases", "department__name")
    list_editable = ("is_active",)


@admin.register(NavigationPoint)
class NavigationPointAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "floor", "point_type", "is_accessible")
    list_filter = ("floor", "point_type", "is_accessible")
    search_fields = ("code", "name")


@admin.register(NavigationEdge)
class NavigationEdgeAdmin(admin.ModelAdmin):
    list_display = ("start_point", "end_point", "distance", "accessible", "is_closed")
    list_filter = ("accessible", "stairs", "lift", "is_closed")


@admin.register(QRLocation)
class QRLocationAdmin(admin.ModelAdmin):
    list_display = ("code", "label", "navigation_point")
    search_fields = ("code", "label")


admin.site.register(UserLocation)
admin.site.register(LocationShare)
