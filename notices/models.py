from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedSoftDeleteModel


class Notice(TimeStampedSoftDeleteModel):
    class Priority(models.TextChoices):
        LOW = "LOW", _("Low")
        NORMAL = "NORMAL", _("Normal")
        HIGH = "HIGH", _("High")
        URGENT = "URGENT", _("Urgent")

    class TargetAudience(models.TextChoices):
        ALL = "ALL", _("All Users")
        STUDENTS = "STUDENTS", _("Students")
        FACULTY = "FACULTY", _("Faculty")
        STAFF = "STAFF", _("Staff")
        SPECIFIC_DEPT = "SPECIFIC_DEPT", _("Specific Department")
        SPECIFIC_BATCH = "SPECIFIC_BATCH", _("Specific Batch")
        SPECIFIC_DIVISION = "SPECIFIC_DIVISION", _("Specific Division")
        CUSTOM = "CUSTOM", _("Custom Selection")

    title = models.CharField(_("title"), max_length=200)
    content = models.TextField(_("content"))
    priority = models.CharField(_("priority"), max_length=8, choices=Priority.choices, default=Priority.NORMAL)
    audience = models.CharField(_("audience"), max_length=20, choices=TargetAudience.choices, default=TargetAudience.ALL)
    # Targeting fields (used when audience is specific)
    departments = models.ManyToManyField(
        "academics.Department",
        blank=True,
        related_name="notices",
    )
    batches = models.ManyToManyField(
        "academics.Batch",
        blank=True,
        related_name="notices",
    )
    divisions = models.ManyToManyField(
        "academics.Division",
        blank=True,
        related_name="notices",
    )
    specific_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="targeted_notices",
    )
    # Attachments
    attachment = models.FileField(_("attachment"), upload_to="notices/", blank=True, null=True)
    # Publishing
    is_published = models.BooleanField(_("published"), default=False)
    published_at = models.DateTimeField(_("published at"), null=True, blank=True)
    expires_at = models.DateTimeField(_("expires at"), null=True, blank=True)
    # Author
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="authored_notices",
    )
    # Pin to top
    is_pinned = models.BooleanField(_("pinned"), default=False)
    # Read tracking
    read_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="NoticeRead",
        related_name="read_notices",
        blank=True,
    )

    class Meta:
        db_table = "notices_notice"
        ordering = ("-is_pinned", "-published_at", "-created_at")
        indexes = [
            models.Index(fields=["is_published", "published_at", "expires_at"]),
            models.Index(fields=["audience", "is_published"]),
        ]

    def __str__(self):
        return f"[{self.get_priority_display()}] {self.title}"


class NoticeRead(TimeStampedSoftDeleteModel):
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE, related_name="read_records")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notice_reads")
    read_at = models.DateTimeField(_("read at"), auto_now_add=True)

    class Meta:
        db_table = "notices_notice_read"
        constraints = [
            models.UniqueConstraint(fields=["notice", "user"], name="unique_notice_user_read"),
        ]

    def __str__(self):
        return f"{self.user} read {self.notice}"


class Event(TimeStampedSoftDeleteModel):
    class EventType(models.TextChoices):
        ACADEMIC = "ACADEMIC", _("Academic")
        CULTURAL = "CULTURAL", _("Cultural")
        SPORTS = "SPORTS", _("Sports")
        TECHNICAL = "TECHNICAL", _("Technical")
        WORKSHOP = "WORKSHOP", _("Workshop")
        SEMINAR = "SEMINAR", _("Seminar")
        CONFERENCE = "CONFERENCE", _("Conference")
        PLACEMENT = "PLACEMENT", _("Placement Drive")
        HOLIDAY = "HOLIDAY", _("Holiday")
        MAINTENANCE = "MAINTENANCE", _("Maintenance")
        OTHER = "OTHER", _("Other")

    title = models.CharField(_("title"), max_length=200)
    description = models.TextField(_("description"), blank=True)
    event_type = models.CharField(_("event type"), max_length=15, choices=EventType.choices, default=EventType.OTHER)
    start_datetime = models.DateTimeField(_("start datetime"), db_index=True)
    end_datetime = models.DateTimeField(_("end datetime"), db_index=True)
    venue = models.ForeignKey(
        "campus.Room",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )
    venue_custom = models.CharField(_("custom venue"), max_length=200, blank=True)
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="organized_events",
    )
    organizing_dept = models.ForeignKey(
        "academics.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )
    # Registration
    requires_registration = models.BooleanField(_("requires registration"), default=False)
    max_participants = models.PositiveIntegerField(_("max participants"), null=True, blank=True)
    registration_deadline = models.DateTimeField(_("registration deadline"), null=True, blank=True)
    # Visibility
    is_public = models.BooleanField(_("public"), default=True)
    target_audience = models.CharField(
        _("target audience"),
        max_length=20,
        choices=Notice.TargetAudience.choices,
        default=Notice.TargetAudience.ALL,
    )
    departments = models.ManyToManyField(
        "academics.Department",
        blank=True,
        related_name="targeted_events",
    )
    # Status
    is_cancelled = models.BooleanField(_("cancelled"), default=False)
    cancellation_reason = models.TextField(_("cancellation reason"), blank=True)
    # Registrations
    registrations = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="EventRegistration",
        related_name="registered_events",
        blank=True,
    )

    class Meta:
        db_table = "notices_event"
        ordering = ("start_datetime",)
        indexes = [
            models.Index(fields=["start_datetime", "end_datetime", "is_public"]),
            models.Index(fields=["event_type", "is_cancelled"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.start_datetime:%Y-%m-%d %H:%M})"


class EventRegistration(TimeStampedSoftDeleteModel):
    class Status(models.TextChoices):
        REGISTERED = "REGISTERED", _("Registered")
        WAITLISTED = "WAITLISTED", _("Waitlisted")
        CONFIRMED = "CONFIRMED", _("Confirmed")
        CANCELLED = "CANCELLED", _("Cancelled")
        ATTENDED = "ATTENDED", _("Attended")
        NO_SHOW = "NO_SHOW", _("No Show")

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registration_records")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="event_registrations")
    status = models.CharField(_("status"), max_length=12, choices=Status.choices, default=Status.REGISTERED)
    registered_at = models.DateTimeField(_("registered at"), auto_now_add=True)
    confirmed_at = models.DateTimeField(_("confirmed at"), null=True, blank=True)
    attended_at = models.DateTimeField(_("attended at"), null=True, blank=True)

    class Meta:
        db_table = "notices_event_registration"
        constraints = [
            models.UniqueConstraint(fields=["event", "user"], name="unique_event_user_registration"),
        ]

    def __str__(self):
        return f"{self.user} – {self.event} ({self.status})"