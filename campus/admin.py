from django.contrib import admin
from .models import Campus, Building, Floor, Room, RoomBooking


class FloorInline(admin.TabularInline):
    model = Floor
    extra = 1
    fields = ("level", "name", "floor_height_meters", "elevation_meters", "is_active")


class BuildingInline(admin.TabularInline):
    model = Building
    extra = 1
    fields = ("code", "name", "total_floors", "is_active")


@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "latitude", "longitude", "is_active", "created_at")
    search_fields = ("code", "name")
    list_filter = ("is_active",)
    inlines = [BuildingInline]


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "campus", "total_floors", "is_active", "created_at")
    search_fields = ("code", "name", "campus__code", "campus__name")
    list_filter = ("campus", "is_active")
    inlines = [FloorInline]


@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    list_display = ("name", "level", "building", "floor_height_meters", "elevation_meters", "is_active")
    search_fields = ("name", "building__name", "building__code")
    list_filter = ("building__campus", "building", "level", "is_active")
    ordering = ("building", "level")


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = (
        "room_code",
        "name",
        "floor",
        "room_type",
        "capacity",
        "x",
        "y",
        "z",
        "width",
        "length",
        "is_active",
    )
    search_fields = ("room_code", "name", "floor__name", "floor__building__code")
    list_filter = ("floor__building", "floor__level", "room_type", "is_active")
    fieldsets = (
        ("Identification", {
            "fields": ("room_code", "name", "floor", "department", "room_type", "capacity", "is_active")
        }),
        ("3D Coordinates (in metres)", {
            "description": "Spatial location on campus. x is East/West, y is North/South, z is elevation.",
            "fields": ("x", "y", "z")
        }),
        ("Dimensions (in metres)", {
            "fields": ("width", "length", "height")
        }),
        ("Floor Plan Layout & Features", {
            "fields": ("layout", "has_projector", "has_ac", "has_whiteboard", "has_smart_board", "computers_count", "is_accessible", "requires_keycard", "maintenance_note")
        }),
    )


@admin.register(RoomBooking)
class RoomBookingAdmin(admin.ModelAdmin):
    list_display = ("room", "title", "booked_by", "start_time", "end_time", "status")
    search_fields = ("title", "room__room_code", "room__name", "booked_by__email")
    list_filter = ("status", "start_time")
