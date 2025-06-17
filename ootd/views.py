from django.shortcuts import render, redirect
from django.http import HttpResponse

# for sign_up, log_in, and log_out
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import logging

logger= logging.getLogger(__name__) # This creates a logger with your module's name



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
    logger.info("This is a test info message")
    logger.debug("This is a test debug message")
    if request.method == 'POST':
        style= request.POST.get('style')
        color= request.POST.get('color')
        occasion= request.POST.get('occasion')
        logger.debug(f"Outfit: Form data - Style: {style}, Color: {color}, Occasion: {occasion}")
        
        # Define compatibility rules
        compatibility_rules={
            # Format: (occasion, style, color): compatibility_score (1-10)
            # Occasion: Work
            ('work', 'casual','black'): "Need scoring",
            ('work', 'casual','white'): "Need scoring",
            ('work', 'casual','red'): "Need scoring",
            ('work', 'casual','any'): "Need scoring",
            
            ('work', 'formal','black'): "Need scoring",
            ('work', 'formal','white'): "Need scoring",
            ('work', 'formal','red'): "Need scoring",
            ('work', 'formal','any'): "Need scoring",
            
            ('work', 'ethinc','black'): "Need scoring",
            ('work', 'ethinc','white'): "Need scoring",
            ('work', 'ethinc','red'): "Need scoring",
            ('work', 'ethinc','any'): "Need scoring",
            
            ('work', 'party','black'): "Need scoring",
            ('work', 'party','white'): "Need scoring",
            ('work', 'party','red'): "Need scoring",
            ('work', 'party','any'): "Need scoring",
            
            ('work', 'sporty','black'): "Need scoring",
            ('work', 'sporty','white'): "Need scoring",
            ('work', 'sporty','red'): "Need scoring",
            ('work', 'sporty','any'): "Need scoring",
            
            # Occasion: Wedding
            ('wedding', 'casual','black'): "Need scoring",
            ('wedding', 'casual','white'): "Need scoring",
            ('wedding', 'casual','red'): "Need scoring",
            ('wedding', 'casual','any'): "Need scoring",
            
            ('wedding', 'formal','black'): "Need scoring",
            ('wedding', 'formal','white'): "Need scoring",
            ('wedding', 'formal','red'): "Need scoring",
            ('wedding', 'formal','any'): "Need scoring",
            
            ('wedding', 'ethinc','black'): "Need scoring",
            ('wedding', 'ethinc','white'): "Need scoring",
            ('wedding', 'ethinc','red'): "Need scoring",
            ('wedding', 'ethinc','any'): "Need scoring",
            
            ('wedding', 'party','black'): "Need scoring",
            ('wedding', 'party','white'): "Need scoring",
            ('wedding', 'party','red'): "Need scoring",
            ('wedding', 'party','any'): "Need scoring",
            
            ('wedding', 'sporty','black'): "Need scoring",
            ('wedding', 'sporty','white'): "Need scoring",
            ('wedding', 'sporty','red'): "Need scoring",
            ('wedding', 'sporty','any'): "Need scoring",
            
            # Occasion: Date
            ('date', 'casual','black'): "Need scoring",
            ('date', 'casual','white'): "Need scoring",
            ('date', 'casual','red'): "Need scoring",
            ('date', 'casual','any'): "Need scoring",
            
            ('date', 'formal','black'): "Need scoring",
            ('date', 'formal','white'): "Need scoring",
            ('date', 'formal','red'): "Need scoring",
            ('date', 'formal','any'): "Need scoring",
            
            ('date', 'ethinc','black'): "Need scoring",
            ('date', 'ethinc','white'): "Need scoring",
            ('date', 'ethinc','red'): "Need scoring",
            ('date', 'ethinc','any'): "Need scoring",
            
            ('date', 'party','black'): "Need scoring",
            ('date', 'party','white'): "Need scoring",
            ('date', 'party','red'): "Need scoring",
            ('date', 'party','any'): "Need scoring",
            
            ('date', 'sporty','black'): "Need scoring",
            ('date', 'sporty','white'): "Need scoring",
            ('date', 'sporty','red'): "Need scoring",
            ('date', 'sporty','any'): "Need scoring",
            
            # Occasion: Vacation
            ('vacation', 'casual','black'): "Need scoring",
            ('vacation', 'casual','white'): "Need scoring",
            ('vacation', 'casual','red'): "Need scoring",
            ('vacation', 'casual','any'): "Need scoring",
            
            ('vacation', 'formal','black'): "Need scoring",
            ('vacation', 'formal','white'): "Need scoring",
            ('vacation', 'formal','red'): "Need scoring",
            ('vacation', 'formal','any'): "Need scoring",
            
            ('vacation', 'ethinc','black'): "Need scoring",
            ('vacation', 'ethinc','white'): "Need scoring",
            ('vacation', 'ethinc','red'): "Need scoring",
            ('vacation', 'ethinc','any'): "Need scoring",
            
            ('vacation', 'party','black'): "Need scoring",
            ('vacation', 'party','white'): "Need scoring",
            ('vacation', 'party','red'): "Need scoring",
            ('vacation', 'party','any'): "Need scoring",
            
            ('vacation', 'sporty','black'): "Need scoring",
            ('vacation', 'sporty','white'): "Need scoring",
            ('vacation', 'sporty','red'): "Need scoring",
            ('vacation', 'sporty','any'): "Need scoring",
            
            # Occasion: Daily
            ('daily', 'casual','black'): "Need scoring",
            ('daily', 'casual','white'): "Need scoring",
            ('daily', 'casual','red'): "Need scoring",
            ('daily', 'casual','any'): "Need scoring",
            
            ('daily', 'formal','black'): "Need scoring",
            ('daily', 'formal','white'): "Need scoring",
            ('daily', 'formal','red'): "Need scoring",
            ('daily', 'formal','any'): "Need scoring",
            
            ('daily', 'ethinc','black'): "Need scoring",
            ('daily', 'ethinc','white'): "Need scoring",
            ('daily', 'ethinc','red'): "Need scoring",
            ('daily', 'ethinc','any'): "Need scoring",
            
            ('daily', 'party','black'): "Need scoring",
            ('daily', 'party','white'): "Need scoring",
            ('daily', 'party','red'): "Need scoring",
            ('daily', 'party','any'): "Need scoring",
            
            ('daily', 'sporty','black'): "Need scoring",
            ('daily', 'sporty','white'): "Need scoring",
            ('daily', 'sporty','red'): "Need scoring",
            ('daily', 'sporty','any'): "Need scoring",
            
        }
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

def closet(request):
    return render(request,'closet.html')