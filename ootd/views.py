from django.shortcuts import render, redirect
from django.http import HttpResponse

# for sign_up, log_in, and log_out
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required





def index(request):
    return render(request, 'index.html')

def sign_up(request):
    if request.method == 'POST':
        username= request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        dob = request.POST.get('dob')
        
                
        username_exists = User.objects.filter(username=username).exists()
        email_exists = User.objects.filter(email=email).exists()
                
        # Username and email validation
        if username_exists:
            message.error(request, "Username already exists")
            return render(request, 'signup.html')
        if email_exists:
            messages.error(request, "Email already exists")
            return render(request, 'signup.html')
        if password!=confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, 'signup.html')
        try:
            user= User.objects.create_user(
                username=username,
                email= email,
                password=password,
                first_name=first_name,
                last_name= last_name,
                )
            # Proceed to login only if user was successfully created
            if user:
                login(request, user)
                messages.success(request, "Account created successfully!")
                return redirect('home')
            else:
                message.error(request, "Failed to create user account")
                
        except Exception as e:
            messages.error(request, f"Error creating account: {str(e)}")
            return render(request, 'signup.html')

    return render(request, 'signup.html')

def outfit(request):
    return render(request, 'outfit.html')

def cup(request):
    if request.method == "POST":
        underbust= request.POST.get('underbust')
        overbust= request.POST.get('overbust')
        
    return render(request, 'cup.html')

def body(request):
    if request.method== "POST":
        bust= request.POST.get('bust')
        waist= request.POST.get('waist')
        hips= request.POST.get('hips')
        return render(request, 'body.html')
                
    return render(request, 'body.html')

def log_in(request):
    if request.method== 'POST':
        username= request.POST.get('username')
        password= request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if not User.objects.filter(username=username).exists():
            messages.error(request,"The username does not exist")
        else:
            user= authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                message.error(request,"The username and password do not match")
    return render(request, 'login.html')

@login_required
def log_out(request):
    logout(request)
    return redirect('home')

def profile(request):
    return render(request,'profile.html')

def about(request):
    return render(request, 'about.html')