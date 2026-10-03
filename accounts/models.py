from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedSoftDeleteModel


class User(AbstractUser, TimeStampedSoftDeleteModel):
    class Role(models.TextChoices):
        STUDENT = "STUDENT", _("Student")
        FACULTY = "FACULTY", _("Faculty")
        HOD = "HOD", _("Head of Department")
        PRINCIPAL = "PRINCIPAL", _("Principal")
        ADMIN = "ADMIN", _("Admin")
        STAFF = "STAFF", _("Staff")

    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(_("role"), max_length=16, choices=Role.choices, default=Role.STUDENT)
    phone = models.CharField(_("phone"), max_length=15, blank=True, validators=[
        RegexValidator(r"^\+?1?\d{9,15}$", "Enter a valid phone number.")
    ])
    avatar = models.ImageField(_("avatar"), upload_to="avatars/", blank=True, null=True)
    is_verified = models.BooleanField(_("verified"), default=False)
    current_room = models.ForeignKey(
        "campus.Room",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="occupants",
    )
    last_seen_at = models.DateTimeField(_("last seen at"), null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "accounts_user"
        verbose_name = _("user")
        verbose_name_plural = _("users")
        indexes = [
            models.Index(fields=["role", "is_deleted"]),
        ]

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"


class Guardian(TimeStampedSoftDeleteModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="guardian_profile",
        limit_choices_to={"role": User.Role.STUDENT},
    )
    name = models.CharField(_("name"), max_length=120)
    relationship = models.CharField(_("relationship"), max_length=50)
    phone = models.CharField(_("phone"), max_length=15, validators=[
        RegexValidator(r"^\+?1?\d{9,15}$", "Enter a valid phone number.")
    ])
    email = models.EmailField(_("email"), blank=True)
    address = models.TextField(_("address"), blank=True)
    occupation = models.CharField(_("occupation"), max_length=100, blank=True)
    annual_income = models.DecimalField(_("annual income"), max_digits=12, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = "accounts_guardian"

    def __str__(self):
        return f"{self.name} – guardian of {self.user}"


class StudentProfile(TimeStampedSoftDeleteModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
        limit_choices_to={"role": User.Role.STUDENT},
    )
    enrollment_number = models.CharField(
        _("enrollment number"),
        max_length=30,
        unique=True,
        validators=[RegexValidator(r"^[A-Z]{2,4}\d{6,10}$", "Format: DEPT123456")],
    )
    roll_number = models.CharField(
        _("roll number"),
        max_length=20,
        unique=True,
        validators=[RegexValidator(r"^\d{2}[A-Z]{2,4}\d{3,5}$", "Format: 22CS101")],
    )
    admission_year = models.PositiveSmallIntegerField(_("admission year"))
    category = models.CharField(
        _("category"),
        max_length=20,
        choices=[
            ("GEN", "General"),
            ("OBC", "OBC"),
            ("SC", "SC"),
            ("ST", "ST"),
            ("EWS", "EWS"),
            ("PH", "Physically Handicapped"),
        ],
        default="GEN",
    )
    blood_group = models.CharField(_("blood group"), max_length=5, blank=True,
        choices=[("A+", "A+"), ("A-", "A-"), ("B+", "B+"), ("B-", "B-"),
                 ("AB+", "AB+"), ("AB-", "AB-"), ("O+", "O+"), ("O-", "O-")])
    aadhar_number = models.CharField(_("aadhar"), max_length=14, blank=True,
        validators=[RegexValidator(r"^\d{4}\s?\d{4}\s?\d{4}$", "Invalid Aadhar format")])
    guardian = models.OneToOneField(Guardian, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="student")
    current_semester = models.ForeignKey(
        "academics.Semester",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
    )
    division = models.ForeignKey(
        "academics.Division",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
    )

    class Meta:
        db_table = "accounts_student_profile"
        indexes = [
            models.Index(fields=["enrollment_number"]),
            models.Index(fields=["roll_number"]),
            models.Index(fields=["admission_year", "is_deleted"]),
        ]

    def __str__(self):
        return f"{self.enrollment_number} – {self.user.get_full_name()}"


class FacultyProfile(TimeStampedSoftDeleteModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="faculty_profile",
        limit_choices_to={"role__in": [User.Role.FACULTY, User.Role.HOD, User.Role.PRINCIPAL]},
    )
    employee_id = models.CharField(
        _("employee id"),
        max_length=20,
        unique=True,
        validators=[RegexValidator(r"^EMP\d{4,6}$", "Format: EMP12345")],
    )
    designation = models.CharField(
        _("designation"),
        max_length=50,
        choices=[
            ("ASSISTANT_PROF", "Assistant Professor"),
            ("ASSOCIATE_PROF", "Associate Professor"),
            ("PROFESSOR", "Professor"),
            ("HOD", "Head of Department"),
            ("PRINCIPAL", "Principal"),
            ("LECTURER", "Lecturer"),
            ("LAB_ASSISTANT", "Lab Assistant"),
        ],
        default="ASSISTANT_PROF",
    )
    department = models.ForeignKey(
        "academics.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="faculty",
    )
    qualifications = models.JSONField(
        _("qualifications"),
        default=list,
        blank=True,
        help_text='List of degrees: [{"degree": "M.Tech", "field": "CSE", "year": 2015}]',
    )
    experience_years = models.PositiveSmallIntegerField(_("experience years"), default=0)
    joining_date = models.DateField(_("joining date"))
    specialization = models.CharField(_("specialization"), max_length=120, blank=True)
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        db_table = "accounts_faculty_profile"
        indexes = [
            models.Index(fields=["employee_id"]),
            models.Index(fields=["department", "is_deleted"]),
        ]

    def __str__(self):
        return f"{self.employee_id} – {self.user.get_full_name()}"


class StaffProfile(TimeStampedSoftDeleteModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="staff_profile",
        limit_choices_to={"role": User.Role.STAFF},
    )
    employee_id = models.CharField(_("employee id"), max_length=20, unique=True)
    designation = models.CharField(_("designation"), max_length=80)
    department = models.ForeignKey(
        "academics.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="staff",
    )
    joining_date = models.DateField(_("joining date"))
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        db_table = "accounts_staff_profile"

    def __str__(self):
        return f"{self.employee_id} – {self.user.get_full_name()}"