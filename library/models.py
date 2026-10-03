from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedSoftDeleteModel


class BookCategory(TimeStampedSoftDeleteModel):
    name = models.CharField(_("name"), max_length=100, unique=True)
    code = models.CharField(_("code"), max_length=20, unique=True)
    description = models.TextField(_("description"), blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subcategories",
    )

    class Meta:
        db_table = "library_book_category"
        ordering = ("name",)
        verbose_name_plural = "book categories"

    def __str__(self):
        return self.name


class Book(TimeStampedSoftDeleteModel):
    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", _("Available")
        ISSUED = "ISSUED", _("Issued")
        RESERVED = "RESERVED", _("Reserved")
        LOST = "LOST", _("Lost")
        DAMAGED = "DAMAGED", _("Damaged")
        UNDER_MAINTENANCE = "UNDER_MAINTENANCE", _("Under Maintenance")
        WITHDRAWN = "WITHDRAWN", _("Withdrawn")

    isbn = models.CharField(
        _("ISBN"),
        max_length=17,
        unique=True,
        validators=[RegexValidator(r"^(?:ISBN(?:-1[03])?:? )?(?=[0-9X]{10}$|(?=(?:[0-9]+[- ]){3})[- 0-9X]{13}$|97[89][0-9]{10}$|(?=(?:[0-9]+[- ]){4})[- 0-9]{17}$)(?:97[89][- ]?)?[0-9]{1,5}[- ]?[0-9]+[- ]?[0-9]+[- ]?[0-9X]$", "Invalid ISBN format")],
        blank=True,
        null=True,
    )
    title = models.CharField(_("title"), max_length=300)
    subtitle = models.CharField(_("subtitle"), max_length=300, blank=True)
    authors = models.JSONField(
        _("authors"),
        default=list,
        help_text='[{"name": "Author Name", "role": "author"}]',
    )
    publisher = models.CharField(_("publisher"), max_length=200, blank=True)
    publication_year = models.PositiveIntegerField(_("publication year"), null=True, blank=True)
    edition = models.CharField(_("edition"), max_length=50, blank=True)
    category = models.ForeignKey(
        BookCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="books",
    )
    subject_tags = models.JSONField(_("subject tags"), default=list, blank=True)
    language = models.CharField(_("language"), max_length=50, default="English")
    pages = models.PositiveIntegerField(_("pages"), null=True, blank=True)
    # Physical details
    total_copies = models.PositiveIntegerField(_("total copies"), default=1)
    available_copies = models.PositiveIntegerField(_("available copies"), default=1)
    location = models.CharField(_("location (shelf)"), max_length=100, blank=True)
    status = models.CharField(_("status"), max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    # Pricing
    price = models.DecimalField(_("price"), max_digits=10, decimal_places=2, null=True, blank=True)
    # Metadata
    cover_image = models.ImageField(_("cover image"), upload_to="book_covers/", blank=True, null=True)
    description = models.TextField(_("description"), blank=True)
    keywords = models.TextField(_("keywords"), blank=True)

    class Meta:
        db_table = "library_book"
        ordering = ("title",)
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["isbn"]),
            models.Index(fields=["category", "status"]),
            models.Index(fields=["status", "available_copies"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.isbn or 'No ISBN'})"


class BookCopy(TimeStampedSoftDeleteModel):
    """Individual physical copy of a book."""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="copies")
    copy_number = models.PositiveIntegerField(_("copy number"))
    accession_number = models.CharField(_("accession number"), max_length=50, unique=True)
    barcode = models.CharField(_("barcode"), max_length=100, unique=True, blank=True, null=True)
    status = models.CharField(_("status"), max_length=20, choices=Book.Status.choices, default=Book.Status.AVAILABLE)
    condition = models.CharField(_("condition"), max_length=50, choices=[
        ("NEW", "New"),
        ("GOOD", "Good"),
        ("FAIR", "Fair"),
        ("POOR", "Poor"),
        ("DAMAGED", "Damaged"),
    ], default="GOOD")
    acquired_date = models.DateField(_("acquired date"))
    acquired_from = models.CharField(_("acquired from"), max_length=200, blank=True)
    cost = models.DecimalField(_("cost"), max_digits=10, decimal_places=2, null=True, blank=True)
    current_location = models.CharField(_("current location"), max_length=100, blank=True)

    class Meta:
        db_table = "library_book_copy"
        ordering = ("book", "copy_number")
        constraints = [
            models.UniqueConstraint(fields=["book", "copy_number"], name="unique_book_copy_number"),
        ]
        indexes = [
            models.Index(fields=["book", "status"]),
            models.Index(fields=["accession_number"]),
            models.Index(fields=["barcode"]),
        ]

    def __str__(self):
        return f"{self.book.title} – Copy {self.copy_number} ({self.accession_number})"


class IssueRecord(TimeStampedSoftDeleteModel):
    class IssueType(models.TextChoices):
        REGULAR = "REGULAR", _("Regular Issue")
        REFERENCE = "REFERENCE", _("Reference Only")
        OVERNIGHT = "OVERNIGHT", _("Overnight")
        INTER_LIBRARY = "INTER_LIBRARY", _("Inter-Library Loan")

    book_copy = models.ForeignKey(
        BookCopy,
        on_delete=models.CASCADE,
        related_name="issue_records",
    )
    issued_to = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="issued_books",
    )
    issue_type = models.CharField(_("issue type"), max_length=15, choices=IssueType.choices, default=IssueType.REGULAR)
    issued_at = models.DateTimeField(_("issued at"), auto_now_add=True)
    due_date = models.DateTimeField(_("due date"), db_index=True)
    issued_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issued_by_records",
    )
    # Renewal tracking
    renewal_count = models.PositiveSmallIntegerField(_("renewal count"), default=0)
    max_renewals = models.PositiveSmallIntegerField(_("max renewals"), default=2)
    last_renewed_at = models.DateTimeField(_("last renewed at"), null=True, blank=True)
    # Status
    is_returned = models.BooleanField(_("returned"), default=False)
    returned_at = models.DateTimeField(_("returned at"), null=True, blank=True)
    returned_to = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="received_returns",
    )
    fine_amount = models.DecimalField(_("fine amount"), max_digits=8, decimal_places=2, default=0)
    fine_paid = models.BooleanField(_("fine paid"), default=False)
    notes = models.TextField(_("notes"), blank=True)

    class Meta:
        db_table = "library_issue_record"
        ordering = ("-issued_at",)
        indexes = [
            models.Index(fields=["issued_to", "is_returned", "due_date"]),
            models.Index(fields=["book_copy", "is_returned"]),
            models.Index(fields=["due_date", "is_returned"]),
        ]

    def __str__(self):
        status = "Returned" if self.is_returned else f"Due: {self.due_date:%Y-%m-%d}"
        return f"{self.book_copy} → {self.issued_to} ({status})"


class ReturnRecord(TimeStampedSoftDeleteModel):
    issue_record = models.OneToOneField(
        IssueRecord,
        on_delete=models.CASCADE,
        related_name="return_record",
    )
    returned_at = models.DateTimeField(_("returned at"), auto_now_add=True)
    returned_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_returns",
    )
    received_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="received_returns",
    )
    condition_on_return = models.CharField(_("condition on return"), max_length=20, choices=[
        ("GOOD", "Good"),
        ("FAIR", "Fair"),
        ("DAMAGED", "Damaged"),
        ("LOST", "Lost"),
    ], default="GOOD")
    damage_description = models.TextField(_("damage description"), blank=True)
    damage_fine = models.DecimalField(_("damage fine"), max_digits=8, decimal_places=2, default=0)
    late_fine = models.DecimalField(_("late fine"), max_digits=8, decimal_places=2, default=0)
    total_fine = models.DecimalField(_("total fine"), max_digits=8, decimal_places=2, default=0)
    fine_paid = models.BooleanField(_("fine paid"), default=False)
    payment_reference = models.CharField(_("payment reference"), max_length=100, blank=True)
    remarks = models.TextField(_("remarks"), blank=True)

    class Meta:
        db_table = "library_return_record"

    def __str__(self):
        return f"Return of {self.issue_record} at {self.returned_at:%Y-%m-%d %H:%M}"


class BookReservation(TimeStampedSoftDeleteModel):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reservations")
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="book_reservations")
    reserved_at = models.DateTimeField(_("reserved at"), auto_now_add=True)
    expires_at = models.DateTimeField(_("expires at"))
    is_fulfilled = models.BooleanField(_("fulfilled"), default=False)
    fulfilled_at = models.DateTimeField(_("fulfilled at"), null=True, blank=True)
    cancelled_at = models.DateTimeField(_("cancelled at"), null=True, blank=True)
    position_in_queue = models.PositiveIntegerField(_("position in queue"), default=1)

    class Meta:
        db_table = "library_book_reservation"
        ordering = ("book", "position_in_queue")
        indexes = [
            models.Index(fields=["book", "is_fulfilled", "position_in_queue"]),
            models.Index(fields=["user", "is_fulfilled"]),
        ]

    def __str__(self):
        return f"{self.user} reserved {self.book} (pos: {self.position_in_queue})"


class LibraryFine(TimeStampedSoftDeleteModel):
    """Consolidated fines for a user."""
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="library_fines")
    total_fine = models.DecimalField(_("total fine"), max_digits=10, decimal_places=2, default=0)
    paid_amount = models.DecimalField(_("paid amount"), max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(_("balance"), max_digits=10, decimal_places=2, default=0)
    is_cleared = models.BooleanField(_("cleared"), default=False)
    last_updated = models.DateTimeField(_("last updated"), auto_now=True)

    class Meta:
        db_table = "library_library_fine"
        constraints = [
            models.UniqueConstraint(fields=["user"], name="unique_user_library_fine"),
        ]

    def __str__(self):
        return f"{self.user} – Balance: ₹{self.balance}"