import json
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, update_session_auth_hash, logout
from apps.users import choices, constants
from apps.users.models import User, Vendor
from apps.users.services import UserServices
from .forms import LoginForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.db import DatabaseError, transaction

@login_required(login_url='login')
def profile(request):
    user: User = request.user
    
    if request.method == 'POST':
        post_request = request.POST
        form_type = post_request.get('form-type')
        
        # User Information Update Form
        if form_type == constants.FORM_USER_INFO:
            result = UserServices.update_user_information(post_request, request.FILES, user)
            
            if result.get('updated'):
                messages.success(request, 'Profile Updated Successfully!')
            else:
                messages.info(request, 'No changed detected!')
            
            return redirect('profile')
        
        # Update Password Form
        elif form_type == constants.FORM_UPDATE_PASSWORD:
            password = post_request.get('password')
            password_confirmation = post_request.get('password_confirmation')
            
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
        
        # Delete Account Form
        elif form_type == constants.FORM_DELETE_ACCOUNT:
            password_confirmation = post_request.get('password_confirmation')
            
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
        
        elif form_type == constants.FORM_APPLY_VENDOR:
            
            store_name = post_request.get("store_name").strip()
            store_address = post_request.get("store_address").strip()
            
            if not store_name:
                messages.error(request, "Store name cannot be empty.")
                return redirect('profile')
            
            success, msg = Vendor.apply(user=user, store_name=store_name, store_address=store_address)
            if success:
                messages.success(request, msg)
            else:
                messages.info(request, msg)
            return redirect('profile')
            
        elif form_type == constants.FORM_VENDOR_DETAILS:
            store_name = post_request.get("store_name").strip()
            store_address = post_request.get("store_address").strip()
            
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
            
        elif form_type == constants.FORM_STRIPE_CONNECT:
            pass
    
    js_messages = json.dumps([
        {"tags": m.tags, "text": m.message} 
        for m in messages.get_messages(request)
    ])
    
    # context
    context = {
        'user': user,
        "form_types": {
            "user_info": constants.FORM_USER_INFO,
            "update_password": constants.FORM_UPDATE_PASSWORD,
            "delete_account": constants.FORM_DELETE_ACCOUNT,
            "apply_vendor": constants.FORM_APPLY_VENDOR,
            "vendor_details": constants.FORM_VENDOR_DETAILS,
            "stripe_connect": constants.FORM_STRIPE_CONNECT
        },
        "js_messages": js_messages,
    }
    return render(request, "users/profile.html", context)

# Create your views here.
def signup(request):
    
    #check if theuser is authenticatedd or not
    if request.user.is_authenticated:
        return redirect('product_list')
    
    if request.method == 'POST':
        # validate the form data here (omitted for brevity)
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')
    else:
        form = UserCreationForm()
    
    return render(request, 'users/auth/sign_up.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('home')
            
    else:
        form = LoginForm()
    
    js_messages = json.dumps([
        {"tags": m.tags, "text": m.message} 
        for m in messages.get_messages(request)
    ])
    return render(request, 'users/auth/login.html', {'form': form, 'js_messages': js_messages})

@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect('home')