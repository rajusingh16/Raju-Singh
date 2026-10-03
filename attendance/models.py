from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedSoftDeleteModel


class TimetableSlot(TimeStampedSoftDeleteModel):
    class DayOfWeek(models.IntegerChoices):
        MONDAY = 0, _("Monday")
        TUESDAY = 1, _("Tuesday")
        WEDNESDAY = 2, _("Wednesday")
        THURSDAY = 3, _("Thursday")
        FRIDAY = 4, _("Friday")
        SATURDAY = 5, _("Saturday")
        SUNDAY = 6, _("Sunday")

    class SlotType(models.TextChoices):
        LECTURE = "LECTURE", _("Lecture")
        LAB = "LAB", _("Lab")
        TUTORIAL = "TUTORIAL", _("Tutorial")
        SEMINAR = "SEMINAR", _("Seminar")
        PROJECT = "PROJECT", _("Project")
        EXAM = "EXAM", _("Exam")
        OTHER = "OTHER", _("Other")

    subject_offering = models.ForeignKey(
        "academics.SubjectOffering",
        on_delete=models.CASCADE,
        related_name="timetable_slots",
    )
    faculty = models.ForeignKey(
        "accounts.FacultyProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="timetable_slots",
    )
    division = models.ForeignKey(
        "academics.Division",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="timetable_slots",
    )
    day = models.IntegerField(_("day"), choices=DayOfWeek.choices)
    start_time = models.TimeField(_("start time"))
    end_time = models.TimeField(_("end time"))
    room = models.ForeignKey(
        "campus.Room",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="timetable_slots",
    )
    slot_type = models.CharField(_("slot type"), max_length=12, choices=SlotType.choices, default=SlotType.LECTURE)
    is_recurring = models.BooleanField(_("recurring"), default=True)
    effective_from = models.DateField(_("effective from"))
    effective_to = models.DateField(_("effective to"), null=True, blank=True)
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        db_table = "attendance_timetable_slot"
        ordering = ("day", "start_time")
        constraints = [
            # Prevent faculty double-booking
            models.UniqueConstraint(
                fields=["faculty", "day", "start_time", "end_time"],
                condition=models.Q(is_active=True, faculty__isnull=False),
                name="unique_faculty_timeslot",
            ),
            # Prevent room double-booking
            models.UniqueConstraint(
                fields=["room", "day", "start_time", "end_time"],
                condition=models.Q(is_active=True, room__isnull=False),
                name="unique_room_timeslot",
            ),
            # Prevent division double-booking
            models.UniqueConstraint(
                fields=["division", "day", "start_time", "end_time"],
                condition=models.Q(is_active=True, division__isnull=False),
                name="unique_division_timeslot",
            ),
        ]
        indexes = [
            models.Index(fields=["day", "start_time", "is_active"]),
            models.Index(fields=["subject_offering", "is_active"]),
        ]

    def __str__(self):
        return f"{self.subject_offering} – {self.get_day_display()} {self.start_time}-{self.end_time}"


class AttendanceRecord(TimeStampedSoftDeleteModel):
    class Status(models.TextChoices):
        PRESENT = "PRESENT", _("Present")
        ABSENT = "ABSENT", _("Absent")
        LATE = "LATE", _("Late")
        EXCUSED = "EXCUSED", _("Excused")
        ON_DUTY = "ON_DUTY", _("On Duty")

    timetable_slot = models.ForeignKey(
        TimetableSlot,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )
    student = models.ForeignKey(
        "accounts.StudentProfile",
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )
    date = models.DateField(_("date"), db_index=True)
    status = models.CharField(_("status"), max_length=10, choices=Status.choices, default=Status.ABSENT)
    marked_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="marked_attendance",
    )
    marked_at = models.DateTimeField(_("marked at"), auto_now_add=True)
    notes = models.TextField(_("notes"), blank=True)
    # For late arrivals
    minutes_late = models.PositiveSmallIntegerField(_("minutes late"), default=0,
        validators=[MinValueValidator(0), MaxValueValidator(180)])

    class Meta:
        db_table = "attendance_attendance_record"
        ordering = ("-date", "timetable_slot__start_time")
        constraints = [
            # One record per student per slot per date
            models.UniqueConstraint(
                fields=["timetable_slot", "student", "date"],
                name="unique_student_slot_date",
            ),
        ]
        indexes = [
            models.Index(fields=["student", "date", "status"]),
            models.Index(fields=["timetable_slot", "date", "status"]),
        ]

    def __str__(self):
        return f"{self.student} – {self.timetable_slot} on {self.date} ({self.status})"


class LeaveRequest(TimeStampedSoftDeleteModel):
    class Type(models.TextChoices):
        SICK = "SICK", _("Sick Leave")
        CASUAL = "CASUAL", _("Casual Leave")
        ON_DUTY = "ON_DUTY", _("On Duty")
        ACADEMIC = "ACADEMIC", _("Academic Leave")
        EMERGENCY = "EMERGENCY", _("Emergency")
        OTHER = "OTHER", _("Other")

    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        APPROVED = "APPROVED", _("Approved")
        REJECTED = "REJECTED", _("Rejected")
        CANCELLED = "CANCELLED", _("Cancelled")

    student = models.ForeignKey(
        "accounts.StudentProfile",
        on_delete=models.CASCADE,
        related_name="leave_requests",
    )
    leave_type = models.CharField(_("leave type"), max_length=12, choices=Type.choices)
    start_date = models.DateField(_("start date"), db_index=True)
    end_date = models.DateField(_("end date"), db_index=True)
    reason = models.TextField(_("reason"))
    supporting_document = models.FileField(_("supporting document"), upload_to="leave_docs/", blank=True, null=True)
    status = models.CharField(_("status"), max_length=12, choices=Status.choices, default=Status.PENDING)
    applied_at = models.DateTimeField(_("applied at"), auto_now_add=True)
    reviewed_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_leaves",
    )
    reviewed_at = models.DateTimeField(_("reviewed at"), null=True, blank=True)
    review_notes = models.TextField(_("review notes"), blank=True)

    class Meta:
        db_table = "attendance_leave_request"
        ordering = ("-applied_at",)
        indexes = [
            models.Index(fields=["student", "status", "start_date"]),
            models.Index(fields=["start_date", "end_date", "status"]),
        ]

    def __str__(self):
        return f"{self.student} – {self.get_leave_type_display()} ({self.start_date} to {self.end_date}) [{self.status}]"


class AttendanceSummary(TimeStampedSoftDeleteModel):
    """Pre-computed attendance percentage for quick reporting."""
    student = models.ForeignKey(
        "accounts.StudentProfile",
        on_delete=models.CASCADE,
        related_name="attendance_summaries",
    )
    subject_offering = models.ForeignKey(
        "academics.SubjectOffering",
        on_delete=models.CASCADE,
        related_name="attendance_summaries",
    )
    month = models.DateField(_("month"))  # First day of month
    total_sessions = models.PositiveIntegerField(_("total sessions"), default=0)
    attended_sessions = models.PositiveIntegerField(_("attended sessions"), default=0)
    percentage = models.DecimalField(_("percentage"), max_digits=5, decimal_places=2, default=0)

    class Meta:
        db_table = "attendance_attendance_summary"
        constraints = [
            models.UniqueConstraint(
                fields=["student", "subject_offering", "month"],
                name="unique_student_subject_month_summary",
            ),
        ]
        indexes = [
            models.Index(fields=["student", "month"]),
            models.Index(fields=["subject_offering", "month"]),
        ]

    def __str__(self):
        return f"{self.student} – {self.subject_offering} ({self.month:%Y-%m}): {self.percentage}%"