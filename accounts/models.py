from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
from core.models import Category, CategoryService
import uuid

# user manager


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.SUPERADMIN)

        return self.create_user(email, password, **extra_fields)


# user model table

class User(AbstractUser):

    username = None

    class Role(models.TextChoices):
        SUPERADMIN = "superadmin", "Super Admin"
        ADMIN = "admin", "Admin"
        VENDOR = "vendor", "Vendor"
        CUSTOMER = "customer", "Customer"

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER
    )
    services = models.ManyToManyField(
        "core.CategoryService", blank=True, related_name="vendors")

    created_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_users"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "phone"]

    objects = UserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"


def generate_order_id():
    return "RCN" + uuid.uuid4().hex[:8].upper()

# bookings


class Booking(models.Model):

    STATUS = (
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )

    service = models.ForeignKey(
        CategoryService,
        on_delete=models.CASCADE
    )

    order_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        default=generate_order_id
    )

    vendor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vendor_bookings"
    )

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)

    address = models.TextField()
    problem = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='pending'
    )

    scheduled_date = models.DateField()
    scheduled_time = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order_id} - {self.service.s_title}"


# booking history(track the order)
class BookingHistory(models.Model):

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="history"
    )

    status = models.CharField(max_length=20)

    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.booking.order_id} - {self.status}"


# payments
class Payment(models.Model):

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    vendor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    service = models.ForeignKey(
        CategoryService,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("paid", "Paid"),
        ],
        default="pending"
    )

    transaction_id = models.CharField(max_length=100, blank=True, null=True)

    screenshot = models.ImageField(
        upload_to="payments/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.booking.order_id} - {self.status}"


class VendorProfile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vendor_profile"
    )

    experience = models.PositiveIntegerField(help_text="Years of experience")

    locality = models.CharField(max_length=200, db_index=True)
    street = models.CharField(max_length=200)
    city = models.CharField(max_length=100, db_index=True)
    postal_code = models.CharField(max_length=10, db_index=True)

    company_name = models.CharField(max_length=200, blank=True)
    company_address = models.TextField(blank=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="vendor_profiles"
    )

    services = models.ManyToManyField(
        CategoryService,
        blank=True,
        related_name="vendor_profiles"
    )

    is_verified = models.BooleanField(default=False)
    rating = models.FloatField(default=0)
    total_jobs = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - VendorProfile"


class CustomerRemark(models.Model):

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
    ]

    booking = models.ForeignKey(
        "Booking",
        on_delete=models.CASCADE,
        related_name="remarks"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="customer_remarks"
    )

    vendor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="vendor_remarks"
    )

    message = models.TextField()

    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default="medium")

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="open")

    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_complaints"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.status}"


class PrivacyPolicy(models.Model):
    title = models.CharField(max_length=200, default="Privacy Policy")
    content = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    

