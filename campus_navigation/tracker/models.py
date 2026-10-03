from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Campus(models.Model):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=20, unique=True, default="GWCET")
    description = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        verbose_name_plural = "campuses"

    def __str__(self):
        return self.name


class Floor(models.Model):
    campus = models.ForeignKey(Campus, related_name="floors", on_delete=models.CASCADE)
    level = models.IntegerField()
    name = models.CharField(max_length=50)
    elevation = models.FloatField(default=0, help_text="Elevation in metres.")
    floor_height = models.FloatField(default=3.66, help_text="Floor-to-floor height in metres.")
    model_file = models.FileField(upload_to="models/", blank=True)

    class Meta:
        ordering = ("level",)
        constraints = [
            models.UniqueConstraint(fields=("campus", "level"), name="unique_campus_floor")
        ]

    def __str__(self):
        return f"{self.campus.code} · {self.name}"


class Department(models.Model):
    name = models.CharField(max_length=120)
    short_code = models.CharField(max_length=20, unique=True)
    floor = models.ForeignKey(
        Floor, related_name="departments", null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.short_code


class NavigationPoint(models.Model):
    class PointType(models.TextChoices):
        GATE = "GATE", "Gate"
        ENTRANCE = "ENTRANCE", "Entrance"
        CORRIDOR = "CORRIDOR", "Corridor"
        ROOM_DOOR = "ROOM_DOOR", "Room door"
        COURTYARD = "COURTYARD", "Courtyard"
        STAIR = "STAIR", "Stair"
        LIFT = "LIFT", "Lift"
        EXIT = "EXIT", "Exit"

    floor = models.ForeignKey(Floor, related_name="navigation_points", on_delete=models.CASCADE)
    code = models.CharField(max_length=60, unique=True)
    name = models.CharField(max_length=120)
    point_type = models.CharField(
        max_length=20, choices=PointType.choices, default=PointType.CORRIDOR
    )
    x = models.FloatField(help_text="East/west coordinate in metres (+X is east).")
    y = models.FloatField(help_text="North/south coordinate in metres (+Y is north).")
    z = models.FloatField(default=0, help_text="Elevation in metres.")
    is_accessible = models.BooleanField(default=True)

    class Meta:
        ordering = ("floor__level", "code")

    def __str__(self):
        return self.code


class Room(models.Model):
    class RoomType(models.TextChoices):
        ADMINISTRATION = "ADMINISTRATION", "Administration"
        CLASSROOM = "CLASSROOM", "Classroom"
        LABORATORY = "LABORATORY", "Laboratory"
        LIBRARY = "LIBRARY", "Library"
        STAFF_ROOM = "STAFF_ROOM", "Staff room"
        WASHROOM = "WASHROOM", "Washroom"
        STAIRCASE = "STAIRCASE", "Staircase"
        ENTRANCE = "ENTRANCE", "Entrance"
        SERVICE_COUNTER = "SERVICE_COUNTER", "Service counter"
        OTHER = "OTHER", "Other"

    floor = models.ForeignKey(Floor, related_name="rooms", on_delete=models.CASCADE)
    navigation_point = models.ForeignKey(
        NavigationPoint,
        related_name="rooms",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    department = models.ForeignKey(
        Department, related_name="rooms", null=True, blank=True, on_delete=models.SET_NULL
    )
    room_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    room_type = models.CharField(
        max_length=24, choices=RoomType.choices, default=RoomType.OTHER
    )
    wing = models.CharField(max_length=30, blank=True)
    description = models.TextField(blank=True)
    aliases = models.CharField(
        max_length=240, blank=True, help_text="Comma-separated alternative search terms."
    )
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField(default=0)
    width = models.FloatField(default=5)
    length = models.FloatField(default=8.5)
    layout = models.JSONField(
        default=dict,
        blank=True,
        help_text='Floor-plan layout dictionary: {"x": 40, "y": 20, "width": 120, "height": 80}'
    )
    model_object_name = models.CharField(max_length=80, blank=True)
    is_active = models.BooleanField(default=True)
    closure_note = models.CharField(max_length=240, blank=True)

    class Meta:
        ordering = ("floor__level", "name")

    def get_layout(self):
        """Returns floor-plan bounding box dict: {"x": ..., "y": ..., "width": ..., "height": ...}."""
        if isinstance(self.layout, dict) and "x" in self.layout:
            return self.layout
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.length,
        }

    def __str__(self):
        return f"{self.room_code} · {self.name}"


class NavigationEdge(models.Model):
    start_point = models.ForeignKey(
        NavigationPoint, related_name="edges_from", on_delete=models.CASCADE
    )
    end_point = models.ForeignKey(
        NavigationPoint, related_name="edges_to", on_delete=models.CASCADE
    )
    distance = models.FloatField(default=0, help_text="Metres; zero calculates from coordinates.")
    accessible = models.BooleanField(default=True)
    stairs = models.BooleanField(default=False)
    lift = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("start_point", "end_point"), name="unique_navigation_edge"
            )
        ]

    def clean(self):
        if self.start_point_id == self.end_point_id:
            raise ValidationError("A navigation edge must connect two different points.")

    def __str__(self):
        return f"{self.start_point.code} ↔ {self.end_point.code}"


class QRLocation(models.Model):
    code = models.CharField(max_length=80, unique=True)
    label = models.CharField(max_length=120)
    navigation_point = models.OneToOneField(
        NavigationPoint, related_name="qr_location", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.label


class UserLocation(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name="indoor_location", on_delete=models.CASCADE
    )
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE)
    navigation_point = models.ForeignKey(
        NavigationPoint, null=True, blank=True, on_delete=models.SET_NULL
    )
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} · {self.floor.name}"


class LocationShare(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="location_shares", on_delete=models.CASCADE
    )
    viewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="shared_locations", on_delete=models.CASCADE
    )
    start_time = models.DateTimeField(auto_now_add=True)
    expiry_time = models.DateTimeField()
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ("-start_time",)

    @property
    def is_valid(self):
        return self.active and self.expiry_time > timezone.now()

    def clean(self):
        if self.owner_id == self.viewer_id:
            raise ValidationError("Choose another user as the viewer.")

    def __str__(self):
        return f"{self.owner} → {self.viewer}"