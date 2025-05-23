from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

## Institutions
# Universities
class University(models.Model):
    university_name = models.CharField(max_length=255, blank=False, unique=True)
    address = models.CharField(max_length=255, blank=False)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'University'
        verbose_name_plural = 'Universities'

    def __str__(self):
        return f"{self.university_name}"

# Organizations
class Organization(models.Model):
    organization_type = [
        ('collection', 'Collection'),
        ('processing', 'Processing'),
        ('recycling', 'Recycling')
    ]
    organization_name = models.CharField(max_length=255, blank=False, unique=True)
    organization_type = models.CharField(max_length=20, choices=organization_type)
    address = models.CharField(max_length=255, blank=False)
    additional_information = models.TextField(blank=True)
    website = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'

    def __str__(self):
        return f"{self.organization_name}"

# Users
class UserManager(BaseUserManager):
    def _create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self._create_user(username, email, password, **extra_fields)

# Users
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('university_community', 'University_Community'),
        ('campus_expert', 'Campus_Expert'),
        ('organization_team', 'Organization_Team')
    ]
    email = models.EmailField(blank=False, unique=True, primary_key=True)
    username = models.CharField(max_length=50, blank=False, unique=True)
    university = models.ForeignKey(University, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    password = models.CharField(max_length=255, blank=False) 
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='images/profile_pics/', blank=True, null=True)
    point_earned = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return f"{self.username} ({self.role})"
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def get_full_name(self):
        return self.username
    
    def get_short_name(self):
        return self.email.split('@')[0]


# Activities
class Activity(models.Model):
    ACTIVITY_TYPE_CHOICES = [
        ('forum', 'Forum'),
        ('publication', 'Publication'),
        ('recycle', 'Recycle'),
        ('other', 'Other'),
    ]
    activity_name = models.CharField(max_length=255, blank=False)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPE_CHOICES)
    activity_date = models.DateTimeField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Activity'
        verbose_name_plural = 'Activities'

    def __str__(self):
        return f"{self.activity_name} ({self.activity_type})"


class ActivityRecord(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='activity_records')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_records')
    point_earned = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'ActivityRecord'
        verbose_name_plural = 'ActivityRecords'

    def __str__(self):
        return f"{self.user.username} - {self.activity.activity_name}"


# Consultations
class Consultation(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consultations_requested', null=True, blank=True)
    consultant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consultations_provided')
    date = models.DateField()
    time = models.TimeField()
    duration_hr = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Duration in hours
    location = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Consultation'
        verbose_name_plural = 'Consultations'

    def __str__(self):
        return f"Consultation: {self.user.username} with {self.consultant.username} on {self.date}"


# Incentives
class Incentive(models.Model):
    incentive_picture = models.ImageField(upload_to='images/incentives/', blank=True, null=True)
    name = models.CharField(max_length=255, blank=False)
    description = models.TextField(blank=True)
    points_required = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Incentive'
        verbose_name_plural = 'Incentives'

    def __str__(self):
        return f"{self.name} ({self.points_required} points)"


class IncentiveRedemptionRecord(models.Model):
    incentive = models.ForeignKey(Incentive, on_delete=models.CASCADE, related_name='redemption_records')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incentive_records')
    redemption_date = models.DateTimeField(default=timezone.now)
    quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'IncentiveRedeemedRecord'
        verbose_name_plural = 'IncentiveRedeemedRecords'

    def __str__(self):
        return f"{self.user.username} redeemed {self.incentive.name}"

# Forum and Comments
class Topic(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forums')
    title = models.CharField(max_length=255, blank=False, unique=True)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Topic'
        verbose_name_plural = 'Topics'

    def __str__(self):
        return f"{self.title} by {self.user.username}"


class Comment(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

    def __str__(self):
        return f"Comment by {self.user.username} on {self.topic.title}"


# Publications
class Publication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='publications')
    title = models.CharField(max_length=255, blank=False)
    publication_detail = models.TextField()
    publication_location = models.CharField(max_length=255, blank=True)
    publication_university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='publications', null=False, blank=False)
    event_start_date = models.DateField()
    event_end_date = models.DateField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Publication'
        verbose_name_plural = 'Publications'

    def __str__(self):
        return f"{self.title} by {self.user.username}"
    
# Waste Collection
class WasteCollectionSlot(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('edited', 'Edited'),
        ('cancelled', 'Cancelled'),
    ]
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='waste_collections')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    location = models.CharField(max_length=255)
    collection_date_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'WasteCollection'
        verbose_name_plural = 'WasteCollections'

    def __str__(self):
        return f"Collection at {self.location}"

class WasteCollectionBooking(models.Model):
    status = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('collected', 'Collected'),
        ('rejected', 'Rejected')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='waste_collection_bookings')
    waste_collection_slot = models.ForeignKey(WasteCollectionSlot, on_delete=models.CASCADE, related_name='bookings')
    preferrable_time = models.TimeField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=status, default='pending')
    points_earned = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'WasteCollectionBooking'
        verbose_name_plural = 'WasteCollectionBookings'

    def __str__(self):
        return f"Booking by {self.user.username} for {self.waste_collection_slot}"

class Appliance(models.Model):
    serial_number = models.CharField(max_length=100, blank=True, primary_key=True)
    waste_collection_booking = models.ForeignKey(WasteCollectionBooking, on_delete=models.CASCADE, related_name='appliances')
    product_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Appliance'
        verbose_name_plural = 'Appliances'

    def __str__(self):
        return f"{self.serial_number} - {self.product_name}"

# Transactions
class MovementRecord(models.Model):
    supplier = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='supplied')
    recipeint = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='recieved', null=True, blank=True)
    recipeint_company = models.CharField(max_length=255, blank=True, null=True)
    transaction_datetime = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'MovementRecord'
        verbose_name_plural = 'MovementRecords'

    def __str__(self):
        return f"{self.supplier} to {self.recipeint}"
    
class Component(models.Model):
    appliance = models.ForeignKey(Appliance, on_delete=models.CASCADE, related_name='components')
    component_name = models.CharField(max_length=255)
    amount = models.IntegerField(default=0)
    status = models.CharField(max_length=255)
    record = models.ManyToManyField(MovementRecord, related_name='components')
    is_processed = models.BooleanField(default=False)
    is_recycled = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Component'
        verbose_name_plural = 'Components'

    def __str__(self):
        return f"{self.component_name} from {self.appliance.product_name}"    

class CEApplication(models.Model):
    status = [
        ('pending', 'Pending'), 
        ('approved', 'Approved'), 
        ('rejected', 'Rejected')
              ]
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ce_applications')
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='applications')
    application_datetime = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=status, default='pending')
    application_detail = models.TextField(blank=True)

    class Meta:
        verbose_name = 'CEApplication'
        verbose_name_plural = 'CEApplications'

    
