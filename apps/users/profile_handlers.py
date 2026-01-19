from django.shortcuts import redirect
from django.urls import reverse
from apps.users.services import UserServices
from django.contrib import messages
from django.db import DatabaseError, transaction
from django.core.exceptions import ValidationError
from apps.users.models import Vendor
from django.contrib.auth import update_session_auth_hash, logout
from django.contrib.auth.password_validation import validate_password

def handle_user_info(request, user):
    result = UserServices.update_user_information(request.POST, request.FILES, user)
            
    if result.get('updated'):
        messages.success(request, 'Profile Updated Successfully!')
    else:
        messages.info(request, 'No changed detected!')
    
    return redirect('profile')


def handle_update_password(request, user):
    password = request.POST.get('password')
    password_confirmation = request.POST.get('password_confirmation')
    
    if password != password_confirmation:
        messages.error(request, "Password doesn't match!")
        return redirect('profile')
    try:
        validate_password(password, user)
    except ValidationError as e:
        for error in e.messages:
            messages.error(request, error)
        return redirect('profile')
    
    user.set_password(password)
    user.save(update_fields=['password'])
    update_session_auth_hash(request, user)

    messages.success(request, "Password updated successfully.")
    return redirect('profile')


def handle_delete_account(request, user):
    password_confirmation = request.POST.get('password_confirmation')
    
    if not user.check_password(password_confirmation):
        messages.error(request, "Password Wrong!")
        return redirect('profile')
    
    try:
        with transaction.atomic():
            user.delete()
    except DatabaseError:
        messages.error(request, "Something went wrong! Try again.")
        return redirect('profile')
    
    messages.success(request, 'Account Deleted Successfully!')
    logout(request)
    return redirect('login')


def handle_apply_vendor(request, user):
    store_name = request.POST.get("store_name").strip()
    store_address = request.POST.get("store_address").strip()
    
    if not store_name:
        messages.error(request, "Store name cannot be empty.")
        return redirect('profile')
    
    success, msg = Vendor.apply(user=user, store_name=store_name, store_address=store_address)
    if success:
        messages.success(request, msg)
    else:
        messages.info(request, msg)
    return redirect('profile')


def handle_vendor_details(request, user):
    store_name = request.POST.get("store_name").strip()
    store_address = request.POST.get("store_address").strip()
    
    if not store_name:
        messages.error(request, "Store name cannot be empty.")
        return redirect('profile')
    
    try:
        vendor: Vendor = user.vendor_details
    except Vendor.DoesNotExist:
        messages.error(request, "Vendor details not found.")
        return redirect('profile')
    
    fields_to_update = []
    if vendor.store_name != store_name:
        vendor.store_name = store_name
        fields_to_update.append("store_name")

    if vendor.store_address != store_address:
        vendor.store_address = store_address
        fields_to_update.append("store_address")

    if fields_to_update:
        vendor.save(update_fields=fields_to_update)
        messages.success(request, "Vendor details updated successfully!")
    else:
        messages.info(request, "No changes detected.")
        
    return redirect('profile')


def handle_stripe_connect(request, user):
    vendor = user.vendor_details
    
    if not vendor.stripe_account_id:
        UserServices.create_express_account(user)
        
    link = UserServices.create_onboarding_link(
        vendor,
        refresh_url=request.build_absolute_uri(
            reverse("stripe_refresh")
        ),
        return_url=request.build_absolute_uri(
            reverse("stripe_return")
        ),
    )

    return redirect(link.url)
