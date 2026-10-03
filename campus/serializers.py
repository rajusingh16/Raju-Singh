from rest_framework import serializers
from .models import Room, Floor, Building, Campus


class RoomListSerializer(serializers.ModelSerializer):
    floor_level = serializers.IntegerField(source="floor.level", read_only=True)
    floor_name = serializers.CharField(source="floor.name", read_only=True)
    building_code = serializers.CharField(source="floor.building.code", read_only=True)
    building_name = serializers.CharField(source="floor.building.name", read_only=True)
    campus_code = serializers.CharField(source="floor.building.campus.code", read_only=True)
    room_type_display = serializers.CharField(source="get_room_type_display", read_only=True)
    depth = serializers.FloatField(source="length", read_only=True)

    class Meta:
        model = Room
        fields = (
            "id",
            "room_code",
            "name",
            "room_type",
            "room_type_display",
            "capacity",
            "floor_level",
            "floor_name",
            "building_code",
            "building_name",
            "campus_code",
            "x",
            "y",
            "z",
            "width",
            "length",
            "depth",
            "height",
            "layout",
            "is_active",
        )
