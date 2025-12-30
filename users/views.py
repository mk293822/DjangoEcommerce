from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from users.forms import LoginForm, UserCreationForm

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
            login(request, user)
            return redirect('product_list')
    else:
        form = UserCreationForm()

    
    return render(request, 'users/sign_up.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('product_list')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('product_list')
    else:
        form = LoginForm()
            
    return render(request, 'users/login.html', {'form': form})