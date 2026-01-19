import json
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
import stripe
from apps.users import constants
from apps.users.models import User
from apps.users.profile_actions import FORM_HANDLERS
from .forms import LoginForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required(login_url='login')
def profile(request):
    user: User = request.user
    
    if request.method == 'POST':
        form_type = request.POST.get('form-type')
        handler = FORM_HANDLERS.get(form_type)
        
        if handler:
            return handler(request, user)
        
        messages.error(request, "Invalid form submission.")
        return redirect("profile")
    
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

stripe.api_key = settings.STRIPE_API_KEY

@login_required(login_url="login")
def stripe_return(request):
    vendor = request.user.vendor_details
    
    if not vendor.stripe_account_id:
        return redirect("profile")

    account = stripe.Account.retrieve(vendor.stripe_account_id)

    vendor.stripe_onboarded = account.details_submitted
    vendor.charges_enabled = account.charges_enabled
    vendor.payouts_enabled = account.payouts_enabled
    vendor.save()

    return render(request, "vendors/stripe_return.html")

@login_required(login_url="login")
def stripe_refresh(request):
    context = {
        "form_types": {
            "stripe_connect": constants.FORM_STRIPE_CONNECT
        }
    }
    return render(request, "vendors/stripe_refresh.html", context)

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