from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from apps.users import choices
from apps.users.constants import GROUP_CUSTOMER, GROUP_VENDOR
from .models import User, Vendor


User = get_user_model()

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = ('email', 'name', 'is_active', 'is_staff', 'is_vendor')
    search_fields = ('email', 'name')
    
    def save_model(self, request, obj, form, change):
        raw_password = form.cleaned_data.get('password')
        if raw_password:
            validate_password(raw_password, obj)
            obj.set_password(raw_password)
        
        super().save_model(request, obj, form, change)
        
@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    model = Vendor
    list_display = ('user', 'status', 'store_name', 'is_stripe_connected', 'can_receive_payouts')
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        vendor_group, _ = Group.objects.get_or_create(name=GROUP_VENDOR)
        customer_group, _ = Group.objects.get_or_create(name=GROUP_CUSTOMER)

        if obj.status == choices.Status.APPROVED:
            obj.user.is_staff = True
            obj.user.save(update_fields=['is_staff'])
            obj.user.groups.add(vendor_group)
            obj.user.groups.remove(customer_group)

        else:
            obj.user.is_staff = False
            obj.user.save(update_fields=['is_staff'])
            obj.user.groups.remove(vendor_group)
            obj.user.groups.add(customer_group)
            