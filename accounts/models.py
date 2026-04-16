from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, BaseUserManager



# USER MANAGER

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



# USER MODEL

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


    created_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_users"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

class Service(models.Model):
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to="services/", null=True, blank=True)

    def __str__(self):
        return self.name





class Booking(models.Model):

    STATUS = (
        ('pending', 'Pending'),
        ('progress','Progress'),
        ('completed', 'Completed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)

    address = models.TextField()
    problem = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)