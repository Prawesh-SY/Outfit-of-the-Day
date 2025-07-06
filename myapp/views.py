from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse

# for sign_up, log_in, and log_out
# from django.contrib.auth.models import User
from .models import Outfit, OutfitImage, FavoriteOutfit, BodyMeasurement, BraSize, CompatibilityRules, Color

from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import logging
import json
from django.views.decorators.http import require_http_methods, require_POST
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.db.models import Q
User = get_user_model()

logger= logging.getLogger(__name__) # This creates a logger with your module's name



def index(request):
    return render(request, 'myapp/index.html')

def sign_up(request):   # Integrated with model
    if request.method == 'POST':
        # username= request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        dob = request.POST.get('dob')
        
                
        # Username and email validation
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return render(request, 'myapp/signup.html')
        if password!=confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, 'myapp/signup.html')
        try:
            # Create user with custom User model
            user= User.objects.create_user(
                # username=username,
                email= email,
                password=password,
                first_name=first_name,
                last_name= last_name,
                dob=dob,
                )
        
            # Proceed to login only if user was successfully created
            if user:
                login(request, user)
                messages.success(request, "Account created successfully!")
                return redirect('home')
            else:
                messages.error(request, "Failed to create user account")
                
        except Exception as e:
            messages.error(request, f"Error creating account: {str(e)}")
            return render(request, 'myapp/signup.html')

    return render(request, 'myapp/signup.html')

def log_in(request):    # Integrated with model
    if request.method== 'POST':
        email= request.POST.get('email')
        password= request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        
        if not User.objects.filter(email=email).exists():
            messages.error(request,"The account does not exist")
        elif user is not None:
                login(request, user)
                return redirect('home')
        else:
            messages.error(request,"The username and password do not match")
    return render(request, 'myapp/login.html')

@login_required
def log_out(request):   # Integrated with model
    logout(request)
    return redirect('home')

def outfit(request):    # Integrated with model
    logger.info("Outfit recommendation view accessed")
    if request.method == 'POST':
        logger.info('POST method requested')
        style= request.POST.get('style')
        color= request.POST.get('color')
        occasion= request.POST.get('occasion')
        logger.info(f"Outfit: Form data - Style: {style}, Color: {color}, Occasion: {occasion}")
        
        # Validate inputs
        if not all([style, occasion]):
            messages.error(request, "Please fill all the fields")
            return render(request, 'myapp/outfit.html')
       
        # Get or create compatibility rule with fallbacks
        try:
            rule = CompatibilityRules.get_or_create_rule(occasion, style, color)
            score = rule.score
            logger.debug(f"Retrieved compatibility score: {score}")
            
            # Get the model instances for database queries
            style_obj= rule.style
            color_obj= rule.color
            occasion_obj= rule.occasion
            
            # Get recommended outfit from the database with image URLs
            # First get exact matches
            exact_matches= OutfitImage.objects.filter(
                color= color_obj,
                style= style_obj,
                occasions= occasion_obj
            ).order_by('-created_at')
            color_instance = Color.objects.get(hex_code=color)
            color_name = color_instance.name
            logger.debug(f"Color name: {color_name}")
            logger.debug(f"Found {exact_matches.count()} exact matches")
            
            # Get the simialr matches
            other_matches= OutfitImage.objects.filter(
                style= style_obj,
                occasions= occasion_obj
            ).exclude(color=color_obj).order_by('-created_at')
            logger.debug(f"Found {other_matches.count()} other matches")

            recommended_outfits = list(exact_matches[:1])   #Get 5 exact matches
            similar_outfits = list(other_matches[:4])   # Get 5 similar matches
            logger.debug(f"Selected {len(recommended_outfits)} exact outfits and {len(similar_outfits)} similar outfits")

            
            logger.info('Ready to set Favorite outfits')
            favorite_outfit_ids = set()
            if request.user.is_authenticated:
                outfit_ids = [o.id for o in recommended_outfits] + [o.id for o in similar_outfits]
                favorite_outfit_ids = set(
                    FavoriteOutfit.objects.filter(
                        user= request.user,
                        outfit_id__in= outfit_ids).values_list('outfit_id', flat= True)
                    )
             

            # Process recommended_outfits data
            exact_outfits_data = [{
                'id' : outfit.id,
                'title' : outfit.title,
                'description' : outfit.description,
                'style' : outfit.style.name,
                'color' : outfit.color.name,                
                'occasions' : occasion,
                'image_url' : outfit.image.url if outfit.image else None,
                'created_at' : outfit.created_at,
                'is_favorite' : outfit.id in favorite_outfit_ids,
            } for outfit in recommended_outfits]
            
            # Process similar_outfits data 
            similar_outfits_data = [{
                'id' : outfit.id,
                'title' : outfit.title,
                'description' : outfit.description,
                'style' : outfit.style.name,
                'color' : outfit.color.name,                
                'occasions' : occasion,
                'image_url' : outfit.image.url if outfit.image else None,
                'created_at' : outfit.created_at,
                'is_favorite' : outfit.id in favorite_outfit_ids,
                } for outfit in similar_outfits]
        
            context = {
                'style': style,
                'color': color,
                'occasion': occasion,
                'score': score,
                'exact_outfits_data': exact_outfits_data,
                'similar_outfits_data': similar_outfits_data,
                'media_url': settings.MEDIA_URL,  # Important for serving media files
                'rule_id': rule.id # Add rule ID for rating form
            }
            # Debugging
            logger.debug(f"""
            === DEBUG OUTPUT ===
           Input Parameters:  Style={style}, Color={color}, Occasion={occasion}
           Compatibility Score: {score}
           
           Database Query Resutls:
            Exact matches found: {len(exact_outfits_data)}
            
            Similar matches found: {len(similar_outfits_data)}
            
           Media URL : 
           
           context = 
                style: {context['style']}
                color: {context['color']}
                occasion: {context['occasion']}
                score: {context['score']}
                exact_outfits_data: 
                    {[(o['id'],
                    o['image_url']) for o in context['exact_outfits_data']] }
                similar_outfits_data:
                    {[(o['id'] , o['image_url']) for o in context['similar_outfits_data']]}
                         """)
            return render(request, 'myapp/recommendation.html', context)
        
        except Exception as e:
            logger.error(f"Error in outfit recommendation: {str(e)}", exc_info= True)
            messages.error(request, "An error occured while processing your request")
            return render(request, 'myapp/outfit.html')
        
    return render(request, 'myapp/outfit.html')

@login_required
def favorite_outfits(request):  # Integrated with model
    favorites = FavoriteOutfit.objects.filter(user=request.user).select_related('outfit')
    return render(request, 'myapp/favorites.html', {'favorites': favorites})

@require_POST
def toggle_favorite(request, outfit_id):    # Integrated with model
    if not request.user.is_authenticated:
        logger.debug("The user has not logged in")
        return JsonResponse({'status':'error', 'message': 'Login required'}, status= 403)
    try:
        logger.debug(f"Raw POST data: {request.POST}"
                     )
        outfit = OutfitImage.objects.get(id=outfit_id)
        favorite, created = FavoriteOutfit.objects.get_or_create(
            user=request.user,
            outfit=outfit
        )
        
        if not created:
            favorite.delete()
            return JsonResponse({'status': 'removed'})
        
        return JsonResponse({'status': 'added'})
    
    except Exception as e:
        logger.error(f"Error in toggle_favorite: {str(e)}")
        return JsonResponse({'status': 'error', 'message': 'Outfit not found'}, status=404)

def cup(request):
    logger.info("Cup invoked")

    if request.method == "POST":
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        logger.info("Method Post")
        try:
            underbust = float(request.POST.get('underbust') or request.body.decode().split(':')[1].split(',')[0])  # Handle both form and JSON
            overbust = float(request.POST.get('overbust') or request.body.decode().split(':')[2].split('}')[0])

            logger.info(f'Request received: underbust:{underbust}, overbust: {overbust}')

            if not (24 <= underbust <= 60) or not (24 <= overbust <= 80):
                error_msg = "Invalid measurements. Underbust (24-60), Overbust (24-80)"
                if is_ajax:
                    return JsonResponse({'error': error_msg}, status=400)
                messages.error(request, error_msg)
                return render(request, 'myapp/cup.html', {'underbust': underbust, 'overbust': overbust})
            # Calculate size
            bra_size = BraSize(underbust=underbust, overbust=overbust)
            bra_size.calculate_size()
            
            if request.user.is_authenticated:
                bra_size, created = BraSize.objects.update_or_create(
                    user=request.user,
                    defaults={'underbust': underbust, 'overbust': overbust}
                )
            else:
                messages.info(request, "Sign in to save your measurements")

            if is_ajax:
                return JsonResponse({
                    'band_size': bra_size.band_size,
                    'cup_size': bra_size.cup_size,
                    'underbust': underbust,
                    'overbust': overbust
                })

            if request.user.is_authenticated:
                messages.success(request, "Bra size saved successfully!")

            return render(request, 'myapp/cup.html', {
                'band_size': bra_size.band_size,
                'cup_size': bra_size.get_cup_size_display(),
                'underbust': underbust,
                'overbust': overbust,
                'saved': request.user.is_authenticated
            })

        except ValueError:
            logger.warning("Invalid input: could not convert to float.")
            if is_ajax:
                return JsonResponse({'error': "Please enter valid numbers"}, status=400)
            messages.error(request, "Please enter valid numbers")

        except Exception as e:
            logger.error(f"Error in bra size calculation: {str(e)}")
            if is_ajax:
                return JsonResponse({'error': "An error occurred during calculation"}, status=500)
            messages.error(request, "An error occurred during calculation")

    # Handle GET or failed POST
    bra_data = None
    if request.user.is_authenticated:
        bra_sizes = BraSize.objects.filter(user=request.user).order_by('-last_updated')
        if bra_sizes.exists():
            bra_data = bra_sizes.first()

    return render(request, 'myapp/cup.html', {
        'bra_data': bra_data,
        'underbust': request.POST.get('underbust', ''),
        'overbust': request.POST.get('overbust', '')
    })

@login_required
def bra_size_history(request): # Create: url, and html
    sizes = BraSize.objects.filter(user=request.user).order_by('-last_updated')
    return render(request, 'myapp/bra_history.html', {'sizes': sizes})

def body(request):  # Integrated with model
    if request.method == "POST":
        try:
            bust = float(request.POST.get('bust'))
            waist = float(request.POST.get('waist'))
            hips = float(request.POST.get('hips'))
            
            # Validate measurements
            if not (20 <= bust <= 80) or not (20 <= waist <= 80) or not (20 <= hips <= 80):
                messages.error(request, "Measurements must be between 20 and 80 inches")
                return render(request, 'myapp/body.html')
            
            if request.user.is_authenticated:
                # Create or update body measurement
                body_measurement, created = BodyMeasurement.objects.update_or_create(
                    user=request.user,
                    defaults={
                        'bust': bust,
                        'waist': waist,
                        'hips': hips
                    }
                )
                
                messages.success(request, "Body measurements saved successfully!")
            else:
                messages.error(request, "You must be logged in to save measurements")
                return redirect('login')
                
        except ValueError:
            messages.error(request, "Please enter valid numbers for measurements")
            return render(request, 'myapp/body.html', {
                'body_data': body_data,
                'bust': request.POST.get('bust', ''),
                'waist': request.POST.get('waist', ''),
                'hips': request.POST.get('hips', '')
            })
        except Exception as e:
            logger.error(f"Error saving body measurements: {str(e)}")
            messages.error(request, "An error occurred while saving measurements")
            return render(request, 'myapp/body.html')
                
    # For GET requests or if user isn't submitting measurements
    body_data = None
    if request.user.is_authenticated and hasattr(request.user, 'bodymeasurement'):
        body_data = request.user.bodymeasurement
        logger.debug(f"""
                ===  DEBUG CONSOLE ===
                Body shape: {body_data.body_type}
                Bust: {body_data.bust}
                Waist: {body_data.waist}
                Hips: {body_data.hips}
                     
                    """ )
    
    return render(request, 'myapp/body.html', {'body_data': body_data})



@require_POST
def get_body_type(request): # Integrated with model
    """Handle both existing measurements and new calculations"""
    try:
        # Parse incoming JSON data
        data = json.loads(request.body)
        
        # If we received measurements, calculate body type
        if 'bust' in data and 'waist' in data and 'hips' in data:
            bust = float(data['bust'])
            waist = float(data['waist'])
            hips = float(data['hips'])
            
            # Validate measurements
            if not (20 <= bust <= 80) or not (20 <= waist <= 80) or not (20 <= hips <= 80):
                return JsonResponse({'error': 'Measurements must be between 20 and 80 inches'}, status=400)
            
            # Calculate body type (same logic as in your model)
            if abs(bust - hips) <= 1 and waist < min(bust, hips) - 2:
                body_type = 'Hourglass'
            elif hips > bust + 2 and hips > waist:
                body_type = 'Pear'
            elif waist > bust and waist > hips:
                body_type = 'Apple'
            elif abs(bust - hips) <= 1 and abs(bust - waist) <= 1:
                body_type = 'Rectangle'
            elif bust > hips + 2 and bust > waist:
                body_type = 'Inverted Triangle'
            else:
                body_type = 'Undefined'
            
            return JsonResponse({
                'body_type': body_type,
                'measurements': {
                    'bust': bust,
                    'waist': waist,
                    'hips': hips
                }
            })
        
        # If no measurements provided but user is authenticated, return their saved data
        elif request.user.is_authenticated:
            if hasattr(request.user, 'bodymeasurement'):
                return JsonResponse({
                    'body_type': request.user.bodymeasurement.get_body_type_display(),
                    'measurements': {
                        'bust': request.user.bodymeasurement.bust,
                        'waist': request.user.bodymeasurement.waist,
                        'hips': request.user.bodymeasurement.hips
                    }
                })
            return JsonResponse({'error': 'No measurements found for this user'}, status=404)
        
        else:
            return JsonResponse({'error': 'No measurements provided'}, status=400)
            
    except ValueError:
        return JsonResponse({'error': 'Invalid measurement values'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def profile(request):
    return render(request, 'myapp/profile.html')

def about(request):
    return render(request, 'myapp/about.html')

@login_required
def closet(request):
    return render(request, 'myapp/closet.html')

