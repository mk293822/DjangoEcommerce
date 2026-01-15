import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from apps.users import constants
from apps.users.models import User
from apps.users.services import UserServices
from .forms import LoginForm, UserCreationForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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
            pass
        elif form_type == constants.FORM_DELETE_ACCOUNT:
            pass
        elif form_type == constants.FORM_VENDOR_DETAILS:
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
            "vendor_details": constants.FORM_VENDOR_DETAILS,
            "delete_account": constants.FORM_DELETE_ACCOUNT,
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
            
    return render(request, 'users/auth/login.html', {'form': form})

@login_required(login_url='login')
@csrf_exempt
def logout_view(request):
    logout(request)
    return redirect('home')