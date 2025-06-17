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
            ('work', 'casual','black'): 8,
            ('work', 'casual','white'): 8,
            ('work', 'casual','red'): 8,
            ('work', 'casual','any'): 7,
            ('work', 'casual','black'): 8,
            ('work', 'casual','white'): 8,
            ('work', 'casual','red'): 8,
            ('work', 'casual','any'): 7,
            
            ('work', 'formal','black'): 10,
            ('work', 'formal','white'): 10,
            ('work', 'formal','red'): 10,
            ('work', 'formal','any'): 9,
            ('work', 'formal','black'): 10,
            ('work', 'formal','white'): 10,
            ('work', 'formal','red'): 10,
            ('work', 'formal','any'): 9,
            
            ('work', 'ethinc','black'): 9,
            ('work', 'ethinc','white'): 9,
            ('work', 'ethinc','red'): 8,
            ('work', 'ethinc','any'): 9,
            ('work', 'ethinc','black'): 9,
            ('work', 'ethinc','white'): 9,
            ('work', 'ethinc','red'): 8,
            ('work', 'ethinc','any'): 9,
            
            ('work', 'party','black'): 9,
            ('work', 'party','white'): 8,
            ('work', 'party','red'): 9,
            ('work', 'party','any'): 9,
            ('work', 'party','black'): 9,
            ('work', 'party','white'): 8,
            ('work', 'party','red'): 9,
            ('work', 'party','any'): 9,
            
            ('work', 'sporty','black'): 3,
            ('work', 'sporty','white'): 3,
            ('work', 'sporty','red'): 2,
            ('work', 'sporty','any'): 2,
            ('work', 'sporty','black'): 3,
            ('work', 'sporty','white'): 3,
            ('work', 'sporty','red'): 2,
            ('work', 'sporty','any'): 2,
            
            # Occasion: Wedding
            ('wedding', 'casual','black'): 5,
            ('wedding', 'casual','white'): 5,
            ('wedding', 'casual','red'): 5,
            ('wedding', 'casual','any'): 5,
            ('wedding', 'casual','black'): 5,
            ('wedding', 'casual','white'): 5,
            ('wedding', 'casual','red'): 5,
            ('wedding', 'casual','any'): 5,
            
            ('wedding', 'formal','black'): 7,
            ('wedding', 'formal','white'): 7,
            ('wedding', 'formal','red'): 8,
            ('wedding', 'formal','any'): 8,
            ('wedding', 'formal','black'): 7,
            ('wedding', 'formal','white'): 7,
            ('wedding', 'formal','red'): 8,
            ('wedding', 'formal','any'): 8,
            
            ('wedding', 'ethinc','black'): 9,
            ('wedding', 'ethinc','white'): 8,
            ('wedding', 'ethinc','red'): 10,
            ('wedding', 'ethinc','any'): 9,
            ('wedding', 'ethinc','black'): 9,
            ('wedding', 'ethinc','white'): 8,
            ('wedding', 'ethinc','red'): 10,
            ('wedding', 'ethinc','any'): 9,
            
            ('wedding', 'party','black'): 9,
            ('wedding', 'party','white'): 7,
            ('wedding', 'party','red'): 10,
            ('wedding', 'party','any'): 9,
            ('wedding', 'party','black'): 9,
            ('wedding', 'party','white'): 7,
            ('wedding', 'party','red'): 10,
            ('wedding', 'party','any'): 9,
            
            ('wedding', 'sporty','black'): 0,
            ('wedding', 'sporty','white'): 0,
            ('wedding', 'sporty','red'): 0,
            ('wedding', 'sporty','any'): 0,
            ('wedding', 'sporty','black'): 0,
            ('wedding', 'sporty','white'): 0,
            ('wedding', 'sporty','red'): 0,
            ('wedding', 'sporty','any'): 0,
            
            # Occasion: Date
            ('date', 'casual','black'): 7,
            ('date', 'casual','white'): 8,
            ('date', 'casual','red'): 9,
            ('date', 'casual','any'): 9,
            ('date', 'casual','black'): 7,
            ('date', 'casual','white'): 8,
            ('date', 'casual','red'): 9,
            ('date', 'casual','any'): 9,
            
            ('date', 'formal','black'): 10,
            ('date', 'formal','white'): 10,
            ('date', 'formal','red'): 10,
            ('date', 'formal','any'): 9,
            ('date', 'formal','black'): 10,
            ('date', 'formal','white'): 10,
            ('date', 'formal','red'): 10,
            ('date', 'formal','any'): 9,
            
            ('date', 'ethinc','black'): 9,
            ('date', 'ethinc','white'): 8,
            ('date', 'ethinc','red'): 10,
            ('date', 'ethinc','any'): 10,
            ('date', 'ethinc','black'): 9,
            ('date', 'ethinc','white'): 8,
            ('date', 'ethinc','red'): 10,
            ('date', 'ethinc','any'): 10,
            
            ('date', 'party','black'): 8,
            ('date', 'party','white'): 8,
            ('date', 'party','red'): 9,
            ('date', 'party','any'): 9,
            ('date', 'party','black'): 8,
            ('date', 'party','white'): 8,
            ('date', 'party','red'): 9,
            ('date', 'party','any'): 9,
            
            ('date', 'sporty','black'): 7,
            ('date', 'sporty','white'): 7,
            ('date', 'sporty','red'): 8,
            ('date', 'sporty','any'): 8,
            ('date', 'sporty','black'): 7,
            ('date', 'sporty','white'): 7,
            ('date', 'sporty','red'): 8,
            ('date', 'sporty','any'): 8,
            
            # Occasion: Vacation
            ('vacation', 'casual','black'): 9,
            ('vacation', 'casual','white'): 9,
            ('vacation', 'casual','red'): 10,
            ('vacation', 'casual','any'): 10,
            ('vacation', 'casual','black'): 9,
            ('vacation', 'casual','white'): 9,
            ('vacation', 'casual','red'): 10,
            ('vacation', 'casual','any'): 10,
            
            ('vacation', 'formal','black'): 9,
            ('vacation', 'formal','white'): 9,
            ('vacation', 'formal','red'): 10,
            ('vacation', 'formal','any'): 10,
            ('vacation', 'formal','black'): 9,
            ('vacation', 'formal','white'): 9,
            ('vacation', 'formal','red'): 10,
            ('vacation', 'formal','any'): 10,
            
            ('vacation', 'ethinc','black'): 10,
            ('vacation', 'ethinc','white'): 10,
            ('vacation', 'ethinc','red'): 10,
            ('vacation', 'ethinc','any'): 10,
            ('vacation', 'ethinc','black'): 10,
            ('vacation', 'ethinc','white'): 10,
            ('vacation', 'ethinc','red'): 10,
            ('vacation', 'ethinc','any'): 10,
            
            ('vacation', 'party','black'): 9,
            ('vacation', 'party','white'): 9,
            ('vacation', 'party','red'): 10,
            ('vacation', 'party','any'): 10,
            ('vacation', 'party','black'): 9,
            ('vacation', 'party','white'): 9,
            ('vacation', 'party','red'): 10,
            ('vacation', 'party','any'): 10,
            
            ('vacation', 'sporty','black'): 10,
            ('vacation', 'sporty','white'): 8,
            ('vacation', 'sporty','red'): 9,
            ('vacation', 'sporty','any'): 9,
            ('vacation', 'sporty','black'): 10,
            ('vacation', 'sporty','white'): 8,
            ('vacation', 'sporty','red'): 9,
            ('vacation', 'sporty','any'): 9,
            
            # Occasion: Daily
            ('daily', 'casual','white'): 9,
            ('daily', 'casual','black'): 9,
            ('daily', 'casual','red'): 8,
            ('daily', 'casual','any'): 10,
            ('daily', 'casual','white'): 9,
            ('daily', 'casual','black'): 9,
            ('daily', 'casual','red'): 8,
            ('daily', 'casual','any'): 10,
            
            ('daily', 'formal','black'): 10,
            ('daily', 'formal','white'): 10,
            ('daily', 'formal','red'): 10,
            ('daily', 'formal','any'): 9,
            ('daily', 'formal','black'): 10,
            ('daily', 'formal','white'): 10,
            ('daily', 'formal','red'): 10,
            ('daily', 'formal','any'): 9,
            
            ('daily', 'ethinc','black'): 10,
            ('daily', 'ethinc','white'): 9,
            ('daily', 'ethinc','red'): 10,
            ('daily', 'ethinc','any'): 10,
            ('daily', 'ethinc','black'): 10,
            ('daily', 'ethinc','white'): 9,
            ('daily', 'ethinc','red'): 10,
            ('daily', 'ethinc','any'): 10,
            
            ('daily', 'party','black'): 9,
            ('daily', 'party','white'): 7,
            ('daily', 'party','red'): 7,
            ('daily', 'party','any'): 10,
            ('daily', 'party','black'): 9,
            ('daily', 'party','white'): 7,
            ('daily', 'party','red'): 7,
            ('daily', 'party','any'): 10,
            
            ('daily', 'sporty','black'): 10,
            ('daily', 'sporty','white'): 5,
            ('daily', 'sporty','red'): 7,
            ('daily', 'sporty','any'): 8,
            
            ('daily', 'sporty','black'): 10,
            ('daily', 'sporty','white'): 5,
            ('daily', 'sporty','red'): 7,
            ('daily', 'sporty','any'): 8,
    
        }
        key = (occasion, color, style)
        score = compatibility_rules.get(key)
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