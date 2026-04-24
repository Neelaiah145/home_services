from django.db import models

# Create your models here.
from django.db import models
from django.utils.text import slugify
from django.utils import timezone

# Create your models here.


class News(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    create_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content if self.content else "News"


class HeroBanner(models.Model):
    heading = models.CharField(max_length=255)
    sub_heading = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='hero/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.heading


class Category(models.Model):
    
    slug = models.SlugField(unique=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.ImageField(upload_to='categories/icons/')
    badge = models.CharField(max_length=50, blank=True)
    tags = models.CharField(
        max_length=200,
        blank=True,
        help_text="Enter comma separated tags (e.g. Repair, Cleaning, Plumbing)"
    )
    banner_image = models.ImageField(
        upload_to='categories/banners/', blank=True, null=True)

    category_about_des = models.TextField(blank=True)
    category_about_img = models.ImageField(
        upload_to='categories/about/', blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)   # added

    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

    def save(self, *args, **kwargs):
        # auto-generate slug
        if not self.slug:
            self.slug = slugify(self.title)

        #  ensure slug uniqueness
        original_slug = self.slug
        queryset = Category.objects.filter(slug=self.slug).exclude(pk=self.pk)
        counter = 1
        while queryset.exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1
            queryset = Category.objects.filter(
                slug=self.slug).exclude(pk=self.pk)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class CategoryService(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='services')
    s_tag = models.CharField(max_length=150)
    s_title = models.CharField(max_length=100)
    s_desc = models.TextField()
    image = models.ImageField(
        upload_to='categories_service_images/', blank=True, null=True)

    #  NEW FIELDS
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.s_title


class ServicesCards(models.Model):

    servicename = models.CharField(max_length=150)
    # Card images
    serviceicon = models.ImageField(upload_to='cardSeries/icons/')
    service_image = models.ImageField(upload_to='cardSeries/card_images/')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Job(models.Model):

    STATUS_CHOICES = [
        ('hiring', 'Hiring'),
        ('urgent', 'Urgent'),
    ]

    TYPE_CHOICES = [
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
    ]

    MODE_CHOICES = [
        ('on_site', 'On-site'),
        ('residential', 'Residential'),
        ('remote', 'Remote'),
    ]

    icon = models.ImageField(upload_to='jobs/icons/')
    title = models.CharField(max_length=150)   # Cooks, Baby Care
    description = models.TextField()

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES)
    job_type = models.CharField(
        max_length=20, choices=TYPE_CHOICES, default='full_time')
    work_mode = models.CharField(
        max_length=20, choices=MODE_CHOICES, default='on_site')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ServiceFeedback(models.Model):

    CUSTOMER_TYPE_CHOICES = [
        ('Client', 'Client'),
        ('House_Owner', 'House Owner'),
        ('Business_Owner', 'Business Owner'),
        ('Other', 'Other'),
    ]

    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]

    service_name = models.CharField(max_length=150)
    customer_name = models.CharField(max_length=100)

    customer_type = models.CharField(
        max_length=50,
        choices=CUSTOMER_TYPE_CHOICES
    )

    image = models.ImageField(
        upload_to='feedback_images/',
        blank=True,
        null=True
    )

    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES
    )

    description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - {self.service_name}"



class Footer(models.Model):

    logo_image = models.ImageField(upload_to='footer/logo/', blank=True, null=True)

    footer_description = models.TextField()

    phone_num = models.CharField(max_length=15)
    whatsapp_num = models.CharField(max_length=15)

    email = models.EmailField()
    address = models.TextField()

    facebook = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    whatsapp = models.URLField(blank=True, null=True)
    twitter=models.URLField(blank=True,null=True)
    

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Footer - {self.phone_num}"
    


class Contact(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('contacted', 'Contacted'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ]

    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    city = models.CharField(max_length=100)
    message = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name