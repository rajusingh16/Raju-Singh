from rest_framework import serializers

from .models import Department, Floor, NavigationEdge, NavigationPoint, Room


class FloorSerializer(serializers.ModelSerializer):
    model_url = serializers.SerializerMethodField()

    class Meta:
        model = Floor
        fields = ("id", "name", "level", "elevation", "floor_height", "model_url")

    def get_model_url(self, obj):
        return obj.model_file.url if obj.model_file else None


class DepartmentSerializer(serializers.ModelSerializer):
    floor_level = serializers.IntegerField(source="floor.level", allow_null=True)

    class Meta:
        model = Department
        fields = ("id", "name", "short_code", "floor_level")


class NavigationPointSerializer(serializers.ModelSerializer):
    floor_level = serializers.IntegerField(source="floor.level")

    class Meta:
        model = NavigationPoint
        fields = (
            "id", "code", "name", "point_type", "floor_level",
            "x", "y", "z", "is_accessible",
        )


class NavigationEdgeSerializer(serializers.ModelSerializer):
    start = serializers.CharField(source="start_point.code")
    end = serializers.CharField(source="end_point.code")

    class Meta:
        model = NavigationEdge
        fields = ("start", "end", "distance", "accessible", "stairs", "lift", "is_closed")


class RoomSerializer(serializers.ModelSerializer):
    floor_name = serializers.CharField(source="floor.name")
    floor_level = serializers.IntegerField(source="floor.level")
    category = serializers.CharField(source="get_room_type_display")
    department = serializers.CharField(source="department.short_code", allow_null=True)
    navigation_point = serializers.CharField(source="navigation_point.code", allow_null=True)
    layout = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = (
            "id", "room_code", "name", "room_type", "category", "floor_name",
            "floor_level", "department", "navigation_point", "wing", "description",
            "aliases", "x", "y", "z", "width", "length", "capacity", "layout", "model_object_name",
            "is_active", "closure_note",
        )

    def get_layout(self, obj):
        return obj.get_layout()

