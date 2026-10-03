from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedSoftDeleteModel


class Campus(TimeStampedSoftDeleteModel):
    name = models.CharField(_("name"), max_length=150)
    code = models.CharField(_("code"), max_length=20, unique=True)
    description = models.TextField(_("description"), blank=True)
    address = models.TextField(_("address"), blank=True)
    latitude = models.DecimalField(_("latitude"), max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(_("longitude"), max_digits=9, decimal_places=6, null=True, blank=True)
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        db_table = "campus_campus"
        ordering = ("name",)

    def __str__(self):
        return f"{self.code} – {self.name}"


class Building(TimeStampedSoftDeleteModel):
    campus = models.ForeignKey(
        Campus,
        on_delete=models.CASCADE,
        related_name="buildings",
    )
    name = models.CharField(_("name"), max_length=150)
    code = models.CharField(_("code"), max_length=20)
    description = models.TextField(_("description"), blank=True)
    latitude = models.DecimalField(_("latitude"), max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(_("longitude"), max_digits=9, decimal_places=6, null=True, blank=True)
    total_floors = models.PositiveSmallIntegerField(_("total floors"), default=1)
    year_built = models.PositiveSmallIntegerField(_("year built"), null=True, blank=True)
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        db_table = "campus_building"
        ordering = ("campus", "name")
        constraints = [
            models.UniqueConstraint(fields=["campus", "code"], name="unique_campus_building_code"),
        ]

    def __str__(self):
        return f"{self.campus.code} – {self.code} ({self.name})"


class Floor(TimeStampedSoftDeleteModel):
    building = models.ForeignKey(
        Building,
        on_delete=models.CASCADE,
        related_name="floors",
    )
    level = models.IntegerField(_("level"))  # 0=ground, -1=basement, 1=first, etc.
    name = models.CharField(_("name"), max_length=50)
    floor_height_meters = models.FloatField(_("floor height (m)"), default=3.66)
    elevation_meters = models.FloatField(_("elevation (m)"), default=0.0)
    layout_image = models.ImageField(_("layout image"), upload_to="floor_layouts/", blank=True, null=True)
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        db_table = "campus_floor"
        ordering = ("building", "level")
        constraints = [
            models.UniqueConstraint(fields=["building", "level"], name="unique_building_floor_level"),
        ]

    def __str__(self):
        return f"{self.building.code} – {self.name} (L{self.level})"


class Room(TimeStampedSoftDeleteModel):
    class RoomType(models.TextChoices):
        CLASSROOM = "CLASSROOM", _("Classroom")
        LABORATORY = "LABORATORY", _("Laboratory")
        LIBRARY = "LIBRARY", _("Library")
        FACULTY_OFFICE = "FACULTY_OFFICE", _("Faculty Office")
        ADMIN_OFFICE = "ADMIN_OFFICE", _("Admin Office")
        HOD_OFFICE = "HOD_OFFICE", _("HOD Office")
        PRINCIPAL_OFFICE = "PRINCIPAL_OFFICE", _("Principal Office")
        STAFF_ROOM = "STAFF_ROOM", _("Staff Room")
        SEMINAR_HALL = "SEMINAR_HALL", _("Seminar Hall")
        AUDITORIUM = "AUDITORIUM", _("Auditorium")
        COMPUTER_LAB = "COMPUTER_LAB", _("Computer Lab")
        RESEARCH_LAB = "RESEARCH_LAB", _("Research Lab")
        HOSTEL_ROOM = "HOSTEL_ROOM", _("Hostel Room")
        WASHROOM = "WASHROOM", _("Washroom")
        STAIRCASE = "STAIRCASE", _("Staircase")
        LIFT = "LIFT", _("Lift")
        CORRIDOR = "CORRIDOR", _("Corridor")
        CANTEEN = "CANTEEN", _("Canteen")
        GYM = "GYM", _("Gym")
        OTHER = "OTHER", _("Other")

    floor = models.ForeignKey(
        Floor,
        on_delete=models.CASCADE,
        related_name="rooms",
    )
    department = models.ForeignKey(
        "academics.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rooms",
    )
    room_code = models.CharField(_("room code"), max_length=30, unique=True)
    name = models.CharField(_("name"), max_length=120)
    room_type = models.CharField(
        _("room type"),
        max_length=20,
        choices=RoomType.choices,
        default=RoomType.OTHER,
    )
    capacity = models.PositiveIntegerField(_("capacity"), default=0,
        validators=[MinValueValidator(0), MaxValueValidator(500)])
    # 3D coordinates (meters from building origin)
    x = models.FloatField(_("x (m)"), default=0.0)
    y = models.FloatField(_("y (m)"), default=0.0)
    z = models.FloatField(_("z (m)"), default=0.0)
    # Dimensions
    width = models.FloatField(_("width (m)"), default=5.0)
    length = models.FloatField(_("length (m)"), default=8.0)
    height = models.FloatField(_("height (m)"), default=3.66)

    @property
    def depth(self):
        """Alias for length for 3D physics/graphics convenience."""
        return self.length

    # 2D layout for floor plan rendering
    layout = models.JSONField(
        _("layout"),
        default=dict,
        blank=True,
        help_text='{"x": 100, "y": 50, "width": 200, "height": 150, "rotation": 0}',
    )
    # Equipment / features
    has_projector = models.BooleanField(_("projector"), default=False)
    has_ac = models.BooleanField(_("AC"), default=False)
    has_whiteboard = models.BooleanField(_("whiteboard"), default=True)
    has_smart_board = models.BooleanField(_("smart board"), default=False)
    computers_count = models.PositiveIntegerField(_("computers"), default=0)
    # Access control
    is_accessible = models.BooleanField(_("wheelchair accessible"), default=True)
    requires_keycard = models.BooleanField(_("keycard required"), default=False)
    # Status
    is_active = models.BooleanField(_("active"), default=True)
    maintenance_note = models.TextField(_("maintenance note"), blank=True)

    class Meta:
        db_table = "campus_room"
        ordering = ("floor__building__campus", "floor__building", "floor__level", "room_code")
        indexes = [
            models.Index(fields=["floor", "room_type", "is_active"]),
            models.Index(fields=["department", "is_active"]),
        ]

    def __str__(self):
        return f"{self.floor.building.code}-{self.floor.level}{self.room_code} – {self.name}"


class RoomBooking(TimeStampedSoftDeleteModel):
    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        CONFIRMED = "CONFIRMED", _("Confirmed")
        CANCELLED = "CANCELLED", _("Cancelled")
        COMPLETED = "COMPLETED", _("Completed")

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    booked_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="room_bookings",
    )
    subject_offering = models.ForeignKey(
        "academics.SubjectOffering",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="room_bookings",
    )
    title = models.CharField(_("title"), max_length=200)
    description = models.TextField(_("description"), blank=True)
    start_time = models.DateTimeField(_("start time"), db_index=True)
    end_time = models.DateTimeField(_("end time"), db_index=True)
    status = models.CharField(_("status"), max_length=12, choices=Status.choices, default=Status.PENDING)
    recurring = models.BooleanField(_("recurring"), default=False)
    recurrence_rule = models.CharField(_("recurrence rule"), max_length=100, blank=True,
        help_text="RRULE string for recurring bookings")
    approved_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_room_bookings",
    )
    approved_at = models.DateTimeField(_("approved at"), null=True, blank=True)

    class Meta:
        db_table = "campus_room_booking"
        ordering = ("-start_time",)
        constraints = [
            # Prevent double-booking same room at same time
            models.UniqueConstraint(
                fields=["room", "start_time", "end_time"],
                condition=models.Q(status__in=["PENDING", "CONFIRMED"]),
                name="unique_room_booking_timeslot",
            ),
        ]
        indexes = [
            models.Index(fields=["room", "start_time", "end_time"]),
            models.Index(fields=["booked_by", "status"]),
        ]

    def __str__(self):
        return f"{self.room} – {self.start_time:%Y-%m-%d %H:%M} to {self.end_time:%H:%M} ({self.status})"