from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedSoftDeleteModel


class University(TimeStampedSoftDeleteModel):
    name = models.CharField(_("name"), max_length=200)
    short_name = models.CharField(_("short name"), max_length=50, unique=True)
    code = models.CharField(_("code"), max_length=20, unique=True)
    address = models.TextField(_("address"), blank=True)
    website = models.URLField(_("website"), blank=True)
    email = models.EmailField(_("email"), blank=True)
    phone = models.CharField(_("phone"), max_length=20, blank=True)
    affiliation_number = models.CharField(_("affiliation number"), max_length=50, blank=True)
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        db_table = "academics_university"
        ordering = ("name",)

    def __str__(self):
        return f"{self.short_name} ({self.code})"


class Department(TimeStampedSoftDeleteModel):
    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name="departments",
    )
    name = models.CharField(_("name"), max_length=150)
    short_code = models.CharField(_("short code"), max_length=10, unique=True)
    code = models.CharField(_("code"), max_length=20, unique=True)
    description = models.TextField(_("description"), blank=True)
    hod = models.ForeignKey(
        "accounts.FacultyProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="headed_department",
        limit_choices_to={"designation": "HOD"},
    )
    established_year = models.PositiveSmallIntegerField(_("established year"), null=True, blank=True)
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        db_table = "academics_department"
        ordering = ("short_code",)
        constraints = [
            models.UniqueConstraint(fields=["university", "short_code"], name="unique_univ_dept_code"),
        ]

    def __str__(self):
        return f"{self.university.short_name} – {self.short_code}"


class Program(TimeStampedSoftDeleteModel):
    class Level(models.TextChoices):
        DIPLOMA = "DIPLOMA", _("Diploma")
        UG = "UG", _("Undergraduate (B.E./B.Tech)")
        PG = "PG", _("Postgraduate (M.E./M.Tech)")
        PHD = "PHD", _("Doctoral")

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="programs",
    )
    name = models.CharField(_("name"), max_length=150)
    short_name = models.CharField(_("short name"), max_length=30)
    code = models.CharField(_("code"), max_length=20)
    level = models.CharField(_("level"), max_length=10, choices=Level.choices, default=Level.UG)
    duration_years = models.PositiveSmallIntegerField(_("duration (years)"), default=4)
    total_semesters = models.PositiveSmallIntegerField(_("total semesters"), default=8)
    credits_required = models.PositiveSmallIntegerField(_("credits required"), default=160)
    intake_capacity = models.PositiveIntegerField(_("intake capacity"), default=60)
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        db_table = "academics_program"
        ordering = ("department__short_code", "code")
        constraints = [
            models.UniqueConstraint(fields=["department", "code"], name="unique_dept_program_code"),
        ]

    def __str__(self):
        return f"{self.department.short_code} – {self.code}"


class Batch(TimeStampedSoftDeleteModel):
    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name="batches",
    )
    academic_year_start = models.PositiveSmallIntegerField(_("academic year start"))
    academic_year_end = models.PositiveSmallIntegerField(_("academic year end"))
    batch_code = models.CharField(_("batch code"), max_length=20)  # e.g., 2022-26
    strength = models.PositiveIntegerField(_("strength"), default=0)
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        db_table = "academics_batch"
        ordering = ("-academic_year_start",)
        constraints = [
            models.UniqueConstraint(fields=["program", "academic_year_start"], name="unique_program_batch_year"),
        ]

    def __str__(self):
        return f"{self.program.code} – {self.batch_code}"


class Semester(TimeStampedSoftDeleteModel):
    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name="semesters",
    )
    number = models.PositiveSmallIntegerField(_("semester number"))
    name = models.CharField(_("name"), max_length=30)  # e.g., "Sem 1", "Sem 3"
    start_date = models.DateField(_("start date"))
    end_date = models.DateField(_("end date"))
    is_current = models.BooleanField(_("current"), default=False)
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        db_table = "academics_semester"
        ordering = ("batch", "number")
        constraints = [
            models.UniqueConstraint(fields=["batch", "number"], name="unique_batch_semester"),
        ]

    def __str__(self):
        return f"{self.batch.batch_code} – {self.name}"


class Division(TimeStampedSoftDeleteModel):
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name="divisions",
    )
    name = models.CharField(_("name"), max_length=20)  # A, B, C, etc.
    capacity = models.PositiveIntegerField(_("capacity"), default=60)
    class_advisor = models.ForeignKey(
        "accounts.FacultyProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="advised_divisions",
    )
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        db_table = "academics_division"
        ordering = ("semester", "name")
        constraints = [
            models.UniqueConstraint(fields=["semester", "name"], name="unique_semester_division"),
        ]

    def __str__(self):
        return f"{self.semester} – Div {self.name}"


class Subject(TimeStampedSoftDeleteModel):
    class Type(models.TextChoices):
        THEORY = "THEORY", _("Theory")
        PRACTICAL = "PRACTICAL", _("Practical")
        TUTORIAL = "TUTORIAL", _("Tutorial")
        PROJECT = "PROJECT", _("Project")
        SEMINAR = "SEMINAR", _("Seminar")

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="subjects",
    )
    code = models.CharField(_("code"), max_length=20)
    name = models.CharField(_("name"), max_length=150)
    short_name = models.CharField(_("short name"), max_length=30)
    subject_type = models.CharField(_("type"), max_length=12, choices=Type.choices, default=Type.THEORY)
    credits = models.PositiveSmallIntegerField(_("credits"), default=3,
        validators=[MinValueValidator(1), MaxValueValidator(6)])
    theory_hours = models.PositiveSmallIntegerField(_("theory hours/week"), default=3)
    practical_hours = models.PositiveSmallIntegerField(_("practical hours/week"), default=0)
    tutorial_hours = models.PositiveSmallIntegerField(_("tutorial hours/week"), default=0)
    description = models.TextField(_("description"), blank=True)
    prerequisites = models.ManyToManyField(
        "self",
        symmetrical=False,
        blank=True,
        related_name="dependents",
    )
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        db_table = "academics_subject"
        ordering = ("department__short_code", "code")
        constraints = [
            models.UniqueConstraint(fields=["department", "code"], name="unique_dept_subject_code"),
        ]

    def __str__(self):
        return f"{self.department.short_code}{self.code} – {self.name}"


class Syllabus(TimeStampedSoftDeleteModel):
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="syllabi",
    )
    version = models.CharField(_("version"), max_length=20)
    effective_from = models.DateField(_("effective from"))
    effective_to = models.DateField(_("effective to"), null=True, blank=True)
    topics = models.JSONField(
        _("topics"),
        default=list,
        help_text='[{"unit": 1, "title": "Introduction", "hours": 6, "topics": ["a", "b"]}]',
    )
    reference_books = models.JSONField(
        _("reference books"),
        default=list,
        blank=True,
        help_text='[{"title": "Book", "author": "Author", "edition": "3rd"}]',
    )
    is_current = models.BooleanField(_("current"), default=False)

    class Meta:
        db_table = "academics_syllabus"
        ordering = ("-effective_from",)
        constraints = [
            models.UniqueConstraint(fields=["subject", "version"], name="unique_subject_syllabus_version"),
        ]

    def __str__(self):
        return f"{self.subject.code} – v{self.version}"


class SubjectOffering(TimeStampedSoftDeleteModel):
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name="subject_offerings",
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="offerings",
    )
    division = models.ForeignKey(
        Division,
        on_delete=models.CASCADE,
        related_name="subject_offerings",
    )
    faculty = models.ForeignKey(
        "accounts.FacultyProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subject_offerings",
    )
    is_elective = models.BooleanField(_("elective"), default=False)
    elective_group = models.CharField(_("elective group"), max_length=50, blank=True)
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        db_table = "academics_subject_offering"
        constraints = [
            models.UniqueConstraint(
                fields=["semester", "subject", "division"],
                name="unique_semester_subject_division",
            ),
        ]

    def __str__(self):
        return f"{self.semester} – {self.subject.code} ({self.division})"