import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from apps.users.models import User
from .forms import LoginForm, UserCreationForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def profile(request):
    user: User = request.user
    
    if request.method == 'POST':
        post_request = request.POST
        name = post_request.get('name', '').strip()
        email = post_request.get('email', '').strip()
        avatar = post_request.get('avatar')
        
        fields = []
        
        if name and name != user.name:
            user.name = name
            fields.append('name')
        if email and email != user.email:
            user.email = email
            fields.append('email')
        if avatar:
            user.avatar = avatar
            fields.append('avatar')
        
        if fields:
            user.save(update_fields=fields)
    
    context = {
        'user': user,
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