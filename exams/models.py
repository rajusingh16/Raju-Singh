from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedSoftDeleteModel


class Exam(TimeStampedSoftDeleteModel):
    class ExamType(models.TextChoices):
        INTERNAL_1 = "INTERNAL_1", _("Internal Assessment 1")
        INTERNAL_2 = "INTERNAL_2", _("Internal Assessment 2")
        INTERNAL_3 = "INTERNAL_3", _("Internal Assessment 3")
        MID_TERM = "MID_TERM", _("Mid Term")
        END_TERM = "END_TERM", _("End Term")
        PRACTICAL = "PRACTICAL", _("Practical Exam")
        VIVA = "VIVA", _("Viva Voce")
        PROJECT = "PROJECT", _("Project Evaluation")
        ASSIGNMENT = "ASSIGNMENT", _("Assignment")
        QUIZ = "QUIZ", _("Quiz")
        OTHER = "OTHER", _("Other")

    subject_offering = models.ForeignKey(
        "academics.SubjectOffering",
        on_delete=models.CASCADE,
        related_name="exams",
    )
    exam_type = models.CharField(_("exam type"), max_length=15, choices=ExamType.choices)
    name = models.CharField(_("name"), max_length=100)
    max_marks = models.PositiveIntegerField(_("max marks"), default=100,
        validators=[MinValueValidator(1), MaxValueValidator(500)])
    weightage = models.DecimalField(_("weightage %"), max_digits=5, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Weightage in final grade calculation")
    exam_date = models.DateField(_("exam date"), db_index=True)
    start_time = models.TimeField(_("start time"))
    end_time = models.TimeField(_("end time"))
    room = models.ForeignKey(
        "campus.Room",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="exams",
    )
    invigilators = models.ManyToManyField(
        "accounts.FacultyProfile",
        blank=True,
        related_name="invigilated_exams",
    )
    instructions = models.TextField(_("instructions"), blank=True)
    is_published = models.BooleanField(_("published"), default=False)
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        db_table = "exams_exam"
        ordering = ("exam_date", "start_time")
        constraints = [
            models.UniqueConstraint(
                fields=["subject_offering", "exam_type"],
                name="unique_subject_offering_exam_type",
            ),
        ]
        indexes = [
            models.Index(fields=["subject_offering", "exam_date", "is_active"]),
        ]

    def __str__(self):
        return f"{self.subject_offering} – {self.get_exam_type_display()}"


class ExamResult(TimeStampedSoftDeleteModel):
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="results",
    )
    student = models.ForeignKey(
        "accounts.StudentProfile",
        on_delete=models.CASCADE,
        related_name="exam_results",
    )
    marks_obtained = models.DecimalField(
        _("marks obtained"),
        max_digits=6,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    graded_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="graded_exam_results",
    )
    graded_at = models.DateTimeField(_("graded at"), null=True, blank=True)
    is_absent = models.BooleanField(_("absent"), default=False)
    is_malpractice = models.BooleanField(_("malpractice"), default=False)
    remarks = models.TextField(_("remarks"), blank=True)
    # For re-evaluation
    re_evaluation_requested = models.BooleanField(_("re-evaluation requested"), default=False)
    re_evaluation_marks = models.DecimalField(
        _("re-evaluation marks"),
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "exams_exam_result"
        constraints = [
            models.UniqueConstraint(
                fields=["exam", "student"],
                name="unique_exam_student_result",
            ),
        ]
        indexes = [
            models.Index(fields=["student", "exam"]),
            models.Index(fields=["exam", "marks_obtained"]),
        ]

    def __str__(self):
        return f"{self.student} – {self.exam}: {self.marks_obtained}/{self.exam.max_marks}"

    @property
    def percentage(self):
        if self.exam.max_marks == 0:
            return 0
        return round((float(self.marks_obtained) / self.exam.max_marks) * 100, 2)


class Grade(TimeStampedSoftDeleteModel):
    class GradeLetter(models.TextChoices):
        O = "O", _("O (Outstanding)")
        A_PLUS = "A+", _("A+")
        A = "A", _("A")
        B_PLUS = "B+", _("B+")
        B = "B", _("B")
        C = "C", _("C")
        P = "P", _("P (Pass)")
        F = "F", _("F (Fail)")
        AB = "AB", _("Absent")
        I = "I", _("Incomplete")

    subject_offering = models.ForeignKey(
        "academics.SubjectOffering",
        on_delete=models.CASCADE,
        related_name="grades",
    )
    student = models.ForeignKey(
        "accounts.StudentProfile",
        on_delete=models.CASCADE,
        related_name="grades",
    )
    grade = models.CharField(_("grade"), max_length=2, choices=GradeLetter.choices)
    grade_points = models.DecimalField(_("grade points"), max_digits=3, decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(10)])
    total_marks = models.DecimalField(_("total marks"), max_digits=6, decimal_places=2, default=0)
    percentage = models.DecimalField(_("percentage"), max_digits=5, decimal_places=2, default=0)
    is_final = models.BooleanField(_("final grade"), default=True)
    calculated_at = models.DateTimeField(_("calculated at"), auto_now_add=True)
    calculated_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="calculated_grades",
    )

    class Meta:
        db_table = "exams_grade"
        constraints = [
            models.UniqueConstraint(
                fields=["subject_offering", "student"],
                condition=models.Q(is_final=True),
                name="unique_final_grade_per_subject",
            ),
        ]
        indexes = [
            models.Index(fields=["student", "grade"]),
            models.Index(fields=["subject_offering", "grade"]),
        ]

    def __str__(self):
        return f"{self.student} – {self.subject_offering}: {self.grade} ({self.grade_points})"


class SemesterResult(TimeStampedSoftDeleteModel):
    """SGPA/CGPA per semester for a student."""
    student = models.ForeignKey(
        "accounts.StudentProfile",
        on_delete=models.CASCADE,
        related_name="semester_results",
    )
    semester = models.ForeignKey(
        "academics.Semester",
        on_delete=models.CASCADE,
        related_name="semester_results",
    )
    sgpa = models.DecimalField(_("SGPA"), max_digits=4, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)])
    cgpa = models.DecimalField(_("CGPA"), max_digits=4, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)])
    total_credits = models.PositiveIntegerField(_("total credits"), default=0)
    earned_credits = models.PositiveIntegerField(_("earned credits"), default=0)
    backlogs = models.PositiveIntegerField(_("backlogs"), default=0)
    is_passed = models.BooleanField(_("passed"), default=True)
    rank = models.PositiveIntegerField(_("rank"), null=True, blank=True)
    total_students = models.PositiveIntegerField(_("total students"), null=True, blank=True)
    calculated_at = models.DateTimeField(_("calculated at"), auto_now_add=True)
    calculated_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="calculated_semester_results",
    )

    class Meta:
        db_table = "exams_semester_result"
        constraints = [
            models.UniqueConstraint(
                fields=["student", "semester"],
                name="unique_student_semester_result",
            ),
        ]
        indexes = [
            models.Index(fields=["semester", "sgpa"]),
            models.Index(fields=["student", "semester"]),
        ]

    def __str__(self):
        return f"{self.student} – {self.semester}: SGPA={self.sgpa}, CGPA={self.cgpa}"