from django.utils.translation import gettext_lazy as _ 
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator
import os
from colorfield.fields import ColorField
import webcolors
from webcolors._definitions import _CSS3_NAMES_TO_HEX



# Constants for choices
OCCASION_CHOICES = [
    ('work', 'Work'),
    ('wedding', 'Wedding'),
    ('date', 'Date'),
    ('vacation', 'Vacation'),
    ('daily', 'Daily Wear')
]

STYLE_CHOICES = [
    ('casual', 'Casual'),
    ('formal', 'Formal'),
    ('ethnic', 'Ethnic'),
    ('party', 'Party'),
    ('sporty', 'Sporty')
]

COLOR_CHOICES = [
    ('black', 'Black'),
    ('white', 'White'),
    ('red', 'Red'),
    ('any', 'Any')
]



class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username= None
    dob = models.DateField(null=True, blank=True, verbose_name=_('Date of Birth'))
    email = models.EmailField(_('email address'), unique=True)
    # Use email as the username field
    USERNAME_FIELD = 'email'  # Corrected from USER_NAME
    REQUIRED_FIELDS = []  # Must include username
    
    objects = UserManager()
    
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        db_table = 'auth_user'  # Optional: keeps same table name as default User

    def get_body_measurement(self):
        """Get the user's body measurements if they exist"""
        return getattr(self, 'bodymeasurement', None)

    def get_bra_size(self):
        """Get the user's bra size if it exists"""
        return getattr(self, 'bra_size', None)

    def __str__(self):
        return self.email

class BodyMeasurement(models.Model):
    BODY_TYPES = [
        ('hourglass', 'Hourglass'),
        ('pear', 'Pear'),
        ('apple', 'Apple'),
        ('rectangle', 'Rectangle'),
        ('inverted', 'Inverted Triangle')
    ]
    
    user = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        related_name='bodymeasurement'
    )
    bust = models.FloatField(
        validators=[MinValueValidator(20), MaxValueValidator(80)],
        help_text="Measurement in inches"
    )
    waist = models.FloatField(
        validators=[MinValueValidator(20), MaxValueValidator(80)],
        help_text="Measurement in inches"
    )
    hips = models.FloatField(
        validators=[MinValueValidator(20), MaxValueValidator(80)],
        help_text="Measurement in inches"
    )
    body_type = models.CharField(
        max_length=20,
        choices=BODY_TYPES,
        blank=True,
        editable=False
    )
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Body Measurement'
        verbose_name_plural = 'Body Measurements'

    def save(self, *args, **kwargs):
        self.calculate_body_type()
        super().save(*args, **kwargs)
    
    def calculate_body_type(self):
        bust = self.bust
        waist = self.waist
        hips = self.hips
        
        if abs(bust - hips) <= 2 and waist < min(bust, hips) - 2:
            self.body_type = 'hourglass'
        elif hips >= bust + 2 and hips > waist:
            self.body_type = 'pear'
        elif waist > bust and waist > hips:
            self.body_type = 'apple'
        elif abs(bust - hips) <= 2 and abs(bust - waist) <= 2:
            self.body_type = 'rectangle'
        elif bust >= hips + 2 and bust > waist:
            self.body_type = 'inverted'
        else:
            self.body_type = ''


    def __str__(self):
        return f"{self.user.get_full_name()}'s measurements ({self.body_type or 'Not calculated'})"

class BraSize(models.Model):
    CUP_SIZES = [
        ('AA', 'AA'), ('A', 'A'), ('B', 'B'), ('C', 'C'),
        ('D', 'D'), ('DD', 'DD'), ('E', 'E'), ('F', 'F'),
        ('G', 'G'), ('H', 'H'), ('I', 'I'), ('J', 'J')
    ]
    
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='bra_size'
    )
    underbust = models.FloatField(
        validators=[MinValueValidator(24), MaxValueValidator(60)],
        help_text="Measurement in inches"
    )
    overbust = models.FloatField(
        validators=[MinValueValidator(24), MaxValueValidator(80)],
        help_text="Measurement in inches"
    )
    band_size = models.PositiveSmallIntegerField(
        editable=False,
        null=True
    )
    cup_size = models.CharField(
        max_length=2,
        choices=CUP_SIZES,
        editable=False,
        null=True
    )
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Bra Size'
        verbose_name_plural = 'Bra Sizes'

    def save(self, *args, **kwargs):
        self.calculate_size()
        super().save(*args, **kwargs)
    
    def calculate_size(self):
        """Calculate bra size based on measurements"""
        # Calculate band size (US sizing)
        self.band_size = round(self.underbust)
        if self.band_size % 2 != 0:  # If odd, add 1 to make even
            self.band_size += 1
            
        # Calculate cup size
        difference = round(self.overbust - self.band_size)
        cup_mapping = {
            0: 'AA', 1: 'A', 2: 'B', 3: 'C', 
            4: 'D', 5: 'DD', 6: 'E', 7: 'F',
            8: 'G', 9: 'H', 10: 'I', 11: 'J'
        }
        self.cup_size = cup_mapping.get(difference, 'D')  # Default to D if out of range

    def __str__(self):
        return f"{self.user.first_name if self.user else "Guest"}'s bra size: {self.band_size}{self.cup_size} (Updated: {self.last_updated})"

class Title(models.Model):
    name = models.CharField(max_length=100, unique= True, help_text="Name of your Collection, e.g, Summer Fits, Beach Vacation")
    description= models.TextField(blank= True)
    
    def __str__(self):
        return self.name
    
class Occasion(models.Model):
    name = models.CharField(max_length=21, unique= True, help_text= 'Type of occasion, e.g., Wedding, Party')
    titles= models.ManyToManyField(Title, related_name= 'occasions', blank= True)
    description = models.TextField(blank= True)
    
    def __str__(self):
        return self.name
    
class Style(models.Model):
    name = models.CharField(max_length=20, unique= True)
    titles= models.ManyToManyField(Title, related_name= 'styles', blank= True)
    description = models.TextField(blank= True)
    
    def __str__(self):
        return self.name
    
class Color(models.Model):
    name = models.CharField(max_length= 50, unique= True,)
    title= models.ManyToManyField(Title, related_name= 'colors', blank= True)
    hex_code= ColorField(default='#000000', unique= True)
    
    @classmethod
    def get_or_create_by_hex(cls, hex_code):
        # Automatically generate color name from hex code if not provided
        try:
            self.name = webcolors.hex_to_name(self.hex_code, spec='css3')
        except ValueError:
            rgb = webcolors.hex_to_rgb(self.hex_code)
            name = cls.closest_color_name(rgb)

        color, created = cls.objects.get_or_create(name=name, defaults = {'hex_code': hex_code})
        return color
        
    @staticmethod
    def closest_color_name(requested_rgb):
        min_dist = float('inf')
        closest = None
        for name, hex_value in webcolors._definitions._CSS3_NAMES_TO_HEX.items():
            r_c, g_c, b_c = webcolors.hex_to_rgb(hex_value)
            # squared distance
            dist = (r_c - requested_rgb[0])**2 + \
               (g_c - requested_rgb[1])**2 + \
               (b_c - requested_rgb[2])**2
            if dist < min_dist:
                min_dist = dist
                closest = name
        
        return closest

    def __str__(self):
        return f"{self.name.upper()}"
    
class Accessories(models.Model):
    name= models.CharField(max_length=100, unique= True)
    title= models.ManyToManyField(Title, related_name= 'accessories', blank=True)
    color= models.ManyToManyField(Color, related_name= 'accessories', blank= True)
    style= models.ManyToManyField(Style, related_name= 'accessories', blank= True)
    occasion= models.ManyToManyField(Occasion, related_name= 'accessories', blank= True)
    pass

class Footwear(models.Model):
    name= models.CharField(max_length=100)
    title= models.ManyToManyField(Title, related_name= 'footwears', blank=True)
    color= models.ManyToManyField(Color, related_name= 'footwears', blank= True)
    style= models.ManyToManyField(Style, related_name= 'footwears', blank= True)
    occasion= models.ManyToManyField(Occasion, related_name= 'footwears', blank= True)

class OutfitImage(models.Model):
    
    def image_upload_path(instance, filename):
        return os.path.join('outfits', filename)

    image = models.ImageField(upload_to=image_upload_path)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    style = models.ForeignKey(Style, on_delete= models.PROTECT)
    color = models.ForeignKey(Color, on_delete= models.PROTECT)
    occasions = models.ManyToManyField(
        Occasion,
        related_name= 'outfit_images',
        blank= True
    )
    
    # Compatibility will be calculated dynamically
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        

    def __str__(self):
        return f"{self.title} ({self.style.name})"

    def get_compatibility_score(self, occasion, style, color):
        """
        Calculate compatibility score based on provided rules
        Returns a tuple of (score)
        """
        try:
            # Convert to names of the compatibility lookup
            occasion_name= occasion.name if isinstance(occasion, Occasion) else occasion
            style_name= style.name if isinstance(style, Style) else style
            color_name= color.name if isinstance(color, Color) else color
            COMPATIBILITY_RULES = {
                # Occasion: Work
                ('work', 'casual','black'): 8,
                ('work', 'casual','white'): 8,
                ('work', 'casual','brown'): 'Need scoring',
                ('work', 'casual','violet'): 'Need scoring',
                ('work', 'casual','indigo'): 'Need scoring',
                ('work', 'casual','blue'): 'Need scoring',
                ('work', 'casual','green'): 'Need scoring',
                ('work', 'casual','yellow'): 'Need scoring',
                ('work', 'casual','orange'): 'Need scoring',
                ('work', 'casual','red'): 8,
                ('work', 'casual','any'): 7,
                
                
                ('work', 'formal','black'): 10,
                ('work', 'formal','white'): 10,
                ('work', 'formal','brown'): 'Need scoring',
                ('work', 'formal','violet'): 'Need scoring',
                ('work', 'formal','indigo'): 'Need scoring',
                ('work', 'formal','blue'): 'Need scoring',
                ('work', 'formal','green'): 'Need scoring',
                ('work', 'formal','yellow'): 'Need scoring',
                ('work', 'formal','orange'): 'Need scoring',
                ('work', 'formal','red'): 10,
                ('work', 'formal','any'): 9,
                
                ('work', 'ethnic','black'): 9,
                ('work', 'ethnic','white'): 9,
                ('work', 'ethnic','brown'): 'Need scoring',
                ('work', 'ethnic','violet'): 'Need scoring',
                ('work', 'ethnic','indigo'): 'Need scoring',
                ('work', 'ethnic','blue'): 'Need scoring',
                ('work', 'ethnic','green'): 'Need scoring',
                ('work', 'ethnic','yellow'): 'Need scoring',
                ('work', 'ethnic','orange'): 'Need scoring',
                ('work', 'ethnic','red'): 8,
                ('work', 'ethnic','any'): 9,
                
                ('work', 'party','black'): 9,
                ('work', 'party','white'): 8,
                ('work', 'party','brown'): 'Need scoring',
                ('work', 'party','violet'): 'Need scoring',
                ('work', 'party','indigo'): 'Need scoring',
                ('work', 'party','blue'): 'Need scoring',
                ('work', 'party','green'): 'Need scoring',
                ('work', 'party','yellow'): 'Need scoring',
                ('work', 'party','orange'): 'Need scoring',
                ('work', 'party','red'): 9,
                ('work', 'party','any'): 9,
                
                ('work', 'sporty','black'): 3,
                ('work', 'sporty','white'): 3,
                ('work', 'sporty','brown'): 'Need scoring',
                ('work', 'sporty','violet'): 'Need scoring',
                ('work', 'sporty','indigo'): 'Need scoring',
                ('work', 'sporty','blue'): 'Need scoring',
                ('work', 'sporty','green'): 'Need scoring',
                ('work', 'sporty','yellow'): 'Need scoring',
                ('work', 'sporty','orange'): 'Need scoring',
                ('work', 'sporty','red'): 2,
                ('work', 'sporty','any'): 2,
                
                # Occasion: Wedding
                ('wedding', 'casual','black'): 5,
                ('wedding', 'casual','white'): 5,
                ('wedding', 'casual','brown'): 'Need scoring',
                ('wedding', 'casual','violet'): 'Need scoring',
                ('wedding', 'casual','indigo'): 'Need scoring',
                ('wedding', 'casual','blue'): 'Need scoring',
                ('wedding', 'casual','green'): 'Need scoring',
                ('wedding', 'casual','yellow'): 'Need scoring',
                ('wedding', 'casual','orange'): 'Need scoring',
                ('wedding', 'casual','red'): 5,
                ('wedding', 'casual','any'): 5,
                
                ('wedding', 'formal','black'): 7,
                ('wedding', 'formal','white'): 7,
                ('wedding', 'formal','brown'): 'Need scoring',
                ('wedding', 'formal','violet'): 'Need scoring',
                ('wedding', 'formal','indigo'): 'Need scoring',
                ('wedding', 'formal','blue'): 'Need scoring',
                ('wedding', 'formal','green'): 'Need scoring',
                ('wedding', 'formal','yellow'): 'Need scoring',
                ('wedding', 'formal','orange'): 'Need scoring',
                ('wedding', 'formal','red'): 8,
                ('wedding', 'formal','any'): 8,
                
                ('wedding', 'ethnic','black'): 9,
                ('wedding', 'ethnic','white'): 8,
                ('wedding', 'ethnic','brown'): 'Need scoring',
                ('wedding', 'ethnic','violet'): 'Need scoring',
                ('wedding', 'ethnic','indigo'): 'Need scoring',
                ('wedding', 'ethnic','blue'): 'Need scoring',
                ('wedding', 'ethnic','green'): 'Need scoring',
                ('wedding', 'ethnic','yellow'): 'Need scoring',
                ('wedding', 'ethnic','orange'): 'Need scoring',
                ('wedding', 'ethnic','red'): 10,
                ('wedding', 'ethnic','any'): 9,
                
                ('wedding', 'party','black'): 9,
                ('wedding', 'party','white'): 7,
                ('wedding', 'party','brown'): 'Need scoring',
                ('wedding', 'party','violet'): 'Need scoring',
                ('wedding', 'party','indigo'): 'Need scoring',
                ('wedding', 'party','blue'): 'Need scoring',
                ('wedding', 'party','green'): 'Need scoring',
                ('wedding', 'party','yellow'): 'Need scoring',
                ('wedding', 'party','orange'): 'Need scoring',
                ('wedding', 'party','red'): 10,
                ('wedding', 'party','any'): 9,
                
                ('wedding', 'sporty','black'): 0,
                ('wedding', 'sporty','white'): 0,
                ('wedding', 'sporty','brown'): 'Need scoring',
                ('wedding', 'sporty','violet'): 'Need scoring',
                ('wedding', 'sporty','indigo'): 'Need scoring',
                ('wedding', 'sporty','blue'): 'Need scoring',
                ('wedding', 'sporty','green'): 'Need scoring',
                ('wedding', 'sporty','yellow'): 'Need scoring',
                ('wedding', 'sporty','orange'): 'Need scoring',
                ('wedding', 'sporty','red'): 0,
                ('wedding', 'sporty','any'): 0,
                
                # Occasion: Date
                ('date', 'casual','black'): 7,
                ('date', 'casual','white'): 8,
                ('date', 'casual','brown'): 'Need scoring',
                ('date', 'casual','violet'): 'Need scoring',
                ('date', 'casual','indigo'): 'Need scoring',
                ('date', 'casual','blue'): 'Need scoring',
                ('date', 'casual','green'): 'Need scoring',
                ('date', 'casual','yellow'): 'Need scoring',
                ('date', 'casual','orange'): 'Need scoring',
                ('date', 'casual','red'): 9,
                ('date', 'casual','any'): 9,
                
                ('date', 'formal','black'): 10,
                ('date', 'formal','white'): 10,
                ('date', 'formal','brown'): 'Need scoring',
                ('date', 'formal','violet'): 'Need scoring',
                ('date', 'formal','indigo'): 'Need scoring',
                ('date', 'formal','blue'): 'Need scoring',
                ('date', 'formal','green'): 'Need scoring',
                ('date', 'formal','yellow'): 'Need scoring',
                ('date', 'formal','orange'): 'Need scoring',
                ('date', 'formal','red'): 10,
                ('date', 'formal','any'): 9,
                
                ('date', 'ethnic','black'): 9,
                ('date', 'ethnic','white'): 8,
                ('date', 'ethnic','brown'): 'Need scoring',
                ('date', 'ethnic','violet'): 'Need scoring',
                ('date', 'ethnic','indigo'): 'Need scoring',
                ('date', 'ethnic','blue'): 'Need scoring',
                ('date', 'ethnic','green'): 'Need scoring',
                ('date', 'ethnic','yellow'): 'Need scoring',
                ('date', 'ethnic','orange'): 'Need scoring',
                ('date', 'ethnic','red'): 10,
                ('date', 'ethnic','any'): 10,
                
                ('date', 'party','black'): 8,
                ('date', 'party','white'): 8,
                ('date', 'party','brown'): 'Need scoring',
                ('date', 'party','violet'): 'Need scoring',
                ('date', 'party','indigo'): 'Need scoring',
                ('date', 'party','blue'): 'Need scoring',
                ('date', 'party','green'): 'Need scoring',
                ('date', 'party','yellow'): 'Need scoring',
                ('date', 'party','orange'): 'Need scoring',
                ('date', 'party','red'): 9,
                ('date', 'party','any'): 9,
                
                ('date', 'sporty','black'): 7,
                ('date', 'sporty','white'): 7,
                ('date', 'sporty','brown'): 'Need scoring',
                ('date', 'sporty','violet'): 'Need scoring',
                ('date', 'sporty','indigo'): 'Need scoring',
                ('date', 'sporty','blue'): 'Need scoring',
                ('date', 'sporty','green'): 'Need scoring',
                ('date', 'sporty','yellow'): 'Need scoring',
                ('date', 'sporty','orange'): 'Need scoring',
                ('date', 'sporty','red'): 8,
                ('date', 'sporty','any'): 8,
                
                # Occasion: Vacation
                ('vacation', 'casual','black'): 9,
                ('vacation', 'casual','white'): 9,
                ('vacation', 'casual','red'): 10,
                ('vacation', 'casual','brown'): 'Need scoring',
                ('vacation', 'casual','violet'): 'Need scoring',
                ('vacation', 'casual','indigo'): 'Need scoring',
                ('vacation', 'casual','blue'): 'Need scoring',
                ('vacation', 'casual','green'): 'Need scoring',
                ('vacation', 'casual','yellow'): 'Need scoring',
                ('vacation', 'casual','orange'): 'Need scoring',
                ('vacation', 'casual','any'): 10,
                
                ('vacation', 'formal','black'): 9,
                ('vacation', 'formal','white'): 9,
                ('vacation', 'formal','red'): 10,
                ('vacation', 'formal','brown'): 'Need scoring',
                ('vacation', 'formal','violet'): 'Need scoring',
                ('vacation', 'formal','indigo'): 'Need scoring',
                ('vacation', 'formal','blue'): 'Need scoring',
                ('vacation', 'formal','green'): 'Need scoring',
                ('vacation', 'formal','yellow'): 'Need scoring',
                ('vacation', 'formal','orange'): 'Need scoring',
                ('vacation', 'formal','any'): 10,
                
                ('vacation', 'ethnic','black'): 10,
                ('vacation', 'ethnic','white'): 10,
                ('vacation', 'ethnic','brown'): 'Need scoring',
                ('vacation', 'ethnic','violet'): 'Need scoring',
                ('vacation', 'ethnic','indigo'): 'Need scoring',
                ('vacation', 'ethnic','blue'): 'Need scoring',
                ('vacation', 'ethnic','green'): 'Need scoring',
                ('vacation', 'ethnic','yellow'): 'Need scoring',
                ('vacation', 'ethnic','orange'): 'Need scoring',
                ('vacation', 'ethnic','red'): 10,
                ('vacation', 'ethnic','any'): 10,
                
                ('vacation', 'party','black'): 9,
                ('vacation', 'party','white'): 9,
                ('vacation', 'party','brown'): 'Need scoring',
                ('vacation', 'party','violet'): 'Need scoring',
                ('vacation', 'party','indigo'): 'Need scoring',
                ('vacation', 'party','blue'): 'Need scoring',
                ('vacation', 'party','green'): 'Need scoring',
                ('vacation', 'party','yellow'): 'Need scoring',
                ('vacation', 'party','orange'): 'Need scoring',
                ('vacation', 'party','red'): 10,
                ('vacation', 'party','any'): 10,
                
                ('vacation', 'sporty','black'): 10,
                ('vacation', 'sporty','white'): 8,
                ('vacation', 'sporty','brown'): 'Need scoring',
                ('vacation', 'sporty','violet'): 'Need scoring',
                ('vacation', 'sporty','indigo'): 'Need scoring',
                ('vacation', 'sporty','blue'): 'Need scoring',
                ('vacation', 'sporty','green'): 'Need scoring',
                ('vacation', 'sporty','yellow'): 'Need scoring',
                ('vacation', 'sporty','orange'): 'Need scoring',
                ('vacation', 'sporty','red'): 9,
                ('vacation', 'sporty','any'): 9,
                
                # Occasion: Daily
                ('daily', 'casual','white'): 9,
                ('daily', 'casual','black'): 9,
                ('daily', 'casual','brown'): 'Need scoring',
                ('daily', 'casual','violet'): 'Need scoring',
                ('daily', 'casual','indigo'): 'Need scoring',
                ('daily', 'casual','blue'): 'Need scoring',
                ('daily', 'casual','green'): 'Need scoring',
                ('daily', 'casual','yellow'): 'Need scoring',
                ('daily', 'casual','orange'): 'Need scoring',
                ('daily', 'casual','red'): 8,
                ('daily', 'casual','any'): 10,
                
                ('daily', 'formal','black'): 10,
                ('daily', 'formal','white'): 10,
                ('daily', 'formal','brown'): 'Need scoring',
                ('daily', 'formal','violet'): 'Need scoring',
                ('daily', 'formal','indigo'): 'Need scoring',
                ('daily', 'formal','blue'): 'Need scoring',
                ('daily', 'formal','green'): 'Need scoring',
                ('daily', 'formal','yellow'): 'Need scoring',
                ('daily', 'formal','orange'): 'Need scoring',
                ('daily', 'formal','red'): 10,
                ('daily', 'formal','any'): 9,
                
                ('daily', 'ethnic','black'): 10,
                ('daily', 'ethnic','white'): 9,
                ('daily', 'ethnic','brown'): 'Need scoring',
                ('daily', 'ethnic','violet'): 'Need scoring',
                ('daily', 'ethnic','indigo'): 'Need scoring',
                ('daily', 'ethnic','blue'): 'Need scoring',
                ('daily', 'ethnic','green'): 'Need scoring',
                ('daily', 'ethnic','yellow'): 'Need scoring',
                ('daily', 'ethnic','orange'): 'Need scoring',
                ('daily', 'ethnic','red'): 10,
                ('daily', 'ethnic','any'): 10,
                
                ('daily', 'party','black'): 9,
                ('daily', 'party','white'): 7,
                ('daily', 'party','brown'): 'Need scoring',
                ('daily', 'party','violet'): 'Need scoring',
                ('daily', 'party','indigo'): 'Need scoring',
                ('daily', 'party','blue'): 'Need scoring',
                ('daily', 'party','green'): 'Need scoring',
                ('daily', 'party','yellow'): 'Need scoring',
                ('daily', 'party','orange'): 'Need scoring',
                ('daily', 'party','red'): 7,
                ('daily', 'party','any'): 10,
                
                ('daily', 'sporty','black'): 10,
                ('daily', 'sporty','white'): 5,
                ('daily', 'sporty','brown'): 'Need scoring',
                ('daily', 'sporty','violet'): 'Need scoring',
                ('daily', 'sporty','indigo'): 'Need scoring',
                ('daily', 'sporty','blue'): 'Need scoring',
                ('daily', 'sporty','green'): 'Need scoring',
                ('daily', 'sporty','yellow'): 'Need scoring',
                ('daily', 'sporty','orange'): 'Need scoring',
                ('daily', 'sporty','red'): 7,
                ('daily', 'sporty','any'): 8,
            }
            
            key = (occasion_name, style_name, color_name)
            return COMPATIBILITY_RULES.get(key, 0)
        except AttributeError:
            return 0

class ClothingItem(models.Model):
    class Meta:
       pass
    CATEGORIES = [
        ('top', 'Top'),
        ('bottom', 'Bottom'),
        ('dress', 'Dress'),
        ('outerwear', 'Outerwear'),
        ('accessory', 'Accessory')
    ]
    
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    style = models.ManyToManyField(Style, related_name= 'clothing_items', blank=True)
    color = models.ManyToManyField(Color, related_name= 'clothing_items', blank=True)
    occasion = models.ManyToManyField(Occasion, related_name= 'clothing_items', blank=True)
    image = models.ImageField(upload_to='closet/')
    
    def __str__(self):
        return f"{self.name} ({self.category})"


class Outfit(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    items = models.ManyToManyField(ClothingItem)
    occasion = models.CharField(max_length=20, choices=OCCASION_CHOICES)
    style = models.CharField(max_length=20, choices=STYLE_CHOICES)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES)
    inspiration = models.ForeignKey(
        OutfitImage, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_occasion_display()})"
    
    def get_compatibility(self):
        """
        Get compatibility score and message for this outfit
        """
        outfit_image = OutfitImage()
        return outfit_image.get_compatibility_score(
            self.occasion,
            self.style,
            self.color
        )

class FavoriteOutfit(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    outfit = models.ForeignKey(OutfitImage, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'outfit')  # Prevents duplicate favorites
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} favorites {self.outfit.title}"

class CompatibilityRules(models.Model):
    class Meta:
        unique_together= ['occasion', 'style', 'color']
    
    occasion= models.ForeignKey(Occasion, on_delete= models.CASCADE)
    style= models.ForeignKey(Style, on_delete= models.CASCADE)
    color= models.ForeignKey(Color, on_delete= models.CASCADE)
    score= models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)], default= 5)
    vote_count= models.PositiveIntegerField(default=0)
    last_updated= models.DateTimeField(auto_now= True)   
   
    
    @classmethod
    def get_or_create_rule(cls, occasion_name, style_name, color_hex):
        # Automaitcally create missing occasion/styles/colors
        occasion, _ =Occasion.objects.get_or_create(name= occasion_name.lower())
        style, _ = Style.objects.get_or_create(name= style_name.lower())
        color = Color.get_or_create_by_hex(color_hex)
        
        rule, created = cls.objects.get_or_create(
            occasion= occasion,
            style= style,
            color= color,
            defaults= {'score': 5}
        )
        return rule
    
    @classmethod
    def update_score(cls, occasion_name, style_name, color_hex, user_score):
        # Update existing score with user input using weighted average
        # Formula: (current_score * current_votes + new_score) / (current_votes + 1)
        # First vote (8): (5*0 + 8)/1 = 8
        # Second vote (6): (8*1 + 6)/2 = 7
        # Third vote (5): (7*2 + 5)/3 = 6
        
        rule = cls.get_or_create_rule(occasion_name, style_name, color_hex)
        rule.score= (rule.score * rule.vote_count + user_score) / (rule.vote_count + 1)
        
        rule.vote_count += 1
        rule.save()
        return rule
    
        
    def __str__(self):
        return f"{self.occasion} + {self.style} + {self.color}: {self.score:.2f} ({self.vote_count} votes)"