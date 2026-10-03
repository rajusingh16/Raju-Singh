from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedSoftDeleteModel


class FeeStructure(TimeStampedSoftDeleteModel):
    class FeeType(models.TextChoices):
        TUITION = "TUITION", _("Tuition Fee")
        LAB = "LAB", _("Laboratory Fee")
        LIBRARY = "LIBRARY", _("Library Fee")
        SPORTS = "SPORTS", _("Sports Fee")
        EXAM = "EXAM", _("Examination Fee")
        DEVELOPMENT = "DEVELOPMENT", _("Development Fee")
        HOSTEL = "HOSTEL", _("Hostel Fee")
        MESS = "MESS", _("Mess Fee")
        TRANSPORT = "TRANSPORT", _("Transport Fee")
        CAUTION_DEPOSIT = "CAUTION_DEPOSIT", _("Caution Deposit")
        OTHER = "OTHER", _("Other")

    program = models.ForeignKey(
        "academics.Program",
        on_delete=models.CASCADE,
        related_name="fee_structures",
    )
    batch = models.ForeignKey(
        "academics.Batch",
        on_delete=models.CASCADE,
        related_name="fee_structures",
    )
    semester = models.ForeignKey(
        "academics.Semester",
        on_delete=models.CASCADE,
        related_name="fee_structures",
    )
    fee_type = models.CharField(_("fee type"), max_length=20, choices=FeeType.choices)
    name = models.CharField(_("name"), max_length=100)
    amount = models.DecimalField(_("amount"), max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)])
    is_mandatory = models.BooleanField(_("mandatory"), default=True)
    due_date = models.DateField(_("due date"))
    late_fine_per_day = models.DecimalField(_("late fine per day"), max_digits=8, decimal_places=2, default=0)
    max_late_fine = models.DecimalField(_("max late fine"), max_digits=8, decimal_places=2, default=0)
    description = models.TextField(_("description"), blank=True)
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        db_table = "fees_fee_structure"
        ordering = ("program", "batch", "semester", "fee_type")
        constraints = [
            models.UniqueConstraint(
                fields=["program", "batch", "semester", "fee_type"],
                name="unique_program_batch_semester_fee_type",
            ),
        ]
        indexes = [
            models.Index(fields=["batch", "semester", "is_active"]),
        ]

    def __str__(self):
        return f"{self.program.code} – {self.batch.batch_code} – {self.get_fee_type_display()}"


class FeePayment(TimeStampedSoftDeleteModel):
    class PaymentMode(models.TextChoices):
        CASH = "CASH", _("Cash")
        CARD = "CARD", _("Card")
        UPI = "UPI", _("UPI")
        NET_BANKING = "NET_BANKING", _("Net Banking")
        CHEQUE = "CHEQUE", _("Cheque")
        DD = "DD", _("Demand Draft")
        SCHOLARSHIP = "SCHOLARSHIP", _("Scholarship")
        WAIVER = "WAIVER", _("Fee Waiver")
        OTHER = "OTHER", _("Other")

    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        SUCCESS = "SUCCESS", _("Success")
        FAILED = "FAILED", _("Failed")
        REFUNDED = "REFUNDED", _("Refunded")
        PARTIAL = "PARTIAL", _("Partial")

    student = models.ForeignKey(
        "accounts.StudentProfile",
        on_delete=models.CASCADE,
        related_name="fee_payments",
    )
    fee_structure = models.ForeignKey(
        FeeStructure,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    amount_paid = models.DecimalField(_("amount paid"), max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)])
    late_fine_paid = models.DecimalField(_("late fine paid"), max_digits=8, decimal_places=2, default=0)
    payment_mode = models.CharField(_("payment mode"), max_length=15, choices=PaymentMode.choices)
    transaction_id = models.CharField(_("transaction ID"), max_length=100, unique=True)
    payment_date = models.DateTimeField(_("payment date"), db_index=True)
    status = models.CharField(_("status"), max_length=12, choices=Status.choices, default=Status.PENDING)
    payment_gateway_response = models.JSONField(_("gateway response"), default=dict, blank=True)
    received_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="received_payments",
    )
    receipt_number = models.CharField(_("receipt number"), max_length=50, unique=True, blank=True)
    remarks = models.TextField(_("remarks"), blank=True)

    class Meta:
        db_table = "fees_fee_payment"
        ordering = ("-payment_date",)
        indexes = [
            models.Index(fields=["student", "status", "payment_date"]),
            models.Index(fields=["fee_structure", "status"]),
            models.Index(fields=["transaction_id"]),
        ]

    def __str__(self):
        return f"{self.student} – {self.fee_structure}: ₹{self.amount_paid} ({self.status})"


class FeeReceipt(TimeStampedSoftDeleteModel):
    payment = models.OneToOneField(
        FeePayment,
        on_delete=models.CASCADE,
        related_name="receipt",
    )
    receipt_number = models.CharField(_("receipt number"), max_length=50, unique=True)
    generated_at = models.DateTimeField(_("generated at"), auto_now_add=True)
    generated_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_receipts",
    )
    pdf_file = models.FileField(_("PDF receipt"), upload_to="fee_receipts/", blank=True, null=True)
    is_sent = models.BooleanField(_("sent to student"), default=False)
    sent_at = models.DateTimeField(_("sent at"), null=True, blank=True)

    class Meta:
        db_table = "fees_fee_receipt"

    def __str__(self):
        return f"Receipt {self.receipt_number} for {self.payment}"


class FeeDue(TimeStampedSoftDeleteModel):
    """Outstanding dues for a student."""
    student = models.ForeignKey(
        "accounts.StudentProfile",
        on_delete=models.CASCADE,
        related_name="fee_dues",
    )
    fee_structure = models.ForeignKey(
        FeeStructure,
        on_delete=models.CASCADE,
        related_name="dues",
    )
    total_amount = models.DecimalField(_("total amount"), max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)])
    paid_amount = models.DecimalField(_("paid amount"), max_digits=10, decimal_places=2, default=0)
    late_fine = models.DecimalField(_("late fine"), max_digits=8, decimal_places=2, default=0)
    waiver_amount = models.DecimalField(_("waiver amount"), max_digits=8, decimal_places=2, default=0)
    balance = models.DecimalField(_("balance"), max_digits=10, decimal_places=2, default=0)
    is_cleared = models.BooleanField(_("cleared"), default=False)
    cleared_at = models.DateTimeField(_("cleared at"), null=True, blank=True)
    last_payment_date = models.DateTimeField(_("last payment"), null=True, blank=True)

    class Meta:
        db_table = "fees_fee_due"
        constraints = [
            models.UniqueConstraint(
                fields=["student", "fee_structure"],
                name="unique_student_fee_due",
            ),
        ]
        indexes = [
            models.Index(fields=["student", "is_cleared"]),
            models.Index(fields=["fee_structure", "is_cleared"]),
        ]

    def __str__(self):
        status = "Cleared" if self.is_cleared else f"Due: ₹{self.balance}"
        return f"{self.student} – {self.fee_structure} ({status})"


class Scholarship(TimeStampedSoftDeleteModel):
    class Type(models.TextChoices):
        MERIT = "MERIT", _("Merit Based")
        NEED = "NEED", _("Need Based")
        SPORTS = "SPORTS", _("Sports")
        MINORITY = "MINORITY", _("Minority")
        GOVERNMENT = "GOVERNMENT", _("Government Scheme")
        INSTITUTIONAL = "INSTITUTIONAL", _("Institutional")
        OTHER = "OTHER", _("Other")

    student = models.ForeignKey(
        "accounts.StudentProfile",
        on_delete=models.CASCADE,
        related_name="scholarships",
    )
    name = models.CharField(_("name"), max_length=150)
    scholarship_type = models.CharField(_("type"), max_length=15, choices=Type.choices)
    amount = models.DecimalField(_("amount"), max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)])
    academic_year = models.CharField(_("academic year"), max_length=20)  # e.g., 2023-24
    sanctioned_date = models.DateField(_("sanctioned date"))
    disbursed_date = models.DateField(_("disbursed date"), null=True, blank=True)
    is_disbursed = models.BooleanField(_("disbursed"), default=False)
    sanction_order = models.CharField(_("sanction order"), max_length=100, blank=True)
    remarks = models.TextField(_("remarks"), blank=True)

    class Meta:
        db_table = "fees_scholarship"
        ordering = ("-sanctioned_date",)
        indexes = [
            models.Index(fields=["student", "academic_year"]),
        ]

    def __str__(self):
        return f"{self.student} – {self.name} (₹{self.amount})"