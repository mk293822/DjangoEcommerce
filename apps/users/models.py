from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid
from apps.core.services.file_services import FileServices
from apps.users.choices import Status
from django.db import transaction

def avatar_upload_to(instance, filename):
    return FileServices.generate_file_path(instance, filename, 'avatar', 'uuid')

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
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("name", "SuperAdmin")

        if not extra_fields.get("is_staff"):
            raise ValueError("SuperAdmin must have is_staff=True")

        return self.create_user(email, password, **extra_fields)

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    
    avatar = models.ImageField(upload_to=avatar_upload_to, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
    def get_vendor_status(self):
        try:
            return self.vendor_details.status
        except Vendor.DoesNotExist:
            return 'none'

    @property
    def is_vendor(self):
        return self.get_vendor_status() == Status.APPROVED

    @property
    def is_pending_vendor(self):
        return self.get_vendor_status() == Status.PENDING

    @property
    def is_rejected_vendor(self):
        return self.get_vendor_status() == Status.REJECTED

        

def vendor_cover_image_upload_to(instance, filename):
    return FileServices.generate_file_path(instance.user, filename, "vendor_cover_images", "uuid")

class Vendor(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="vendor_details")
    store_name = models.CharField(max_length=100)
    store_address = models.TextField(null=True, blank=True)
    cover_image = models.ImageField(upload_to=vendor_cover_image_upload_to, null=True, blank=True)
    status = models.CharField(choices=Status.choices, default=Status.PENDING, max_length=20)
    
    def __str__(self):
        return f"{self.user.name}-{self.store_name}"
    
    @classmethod
    def apply(cls, user, store_name, store_address):

        if user.is_vendor:
            return False, "You are already a vendor!"
        elif user.is_pending_vendor:
            return False, "Your vendor application is pending."
        else:
            # create or update
            with transaction.atomic():
                cls.objects.update_or_create(
                    user=user,
                    defaults={
                        'store_name': store_name,
                        'store_address': store_address,
                        'status': Status.PENDING
                    }
                )
            return True, "Vendor application submitted successfully!"