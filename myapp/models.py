from django.utils.translation import gettext_lazy as _ 
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator
import os
from colorfield.fields import ColorField
import webcolors
from webcolors._definitions import _CSS3_NAMES_TO_HEX


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
    
    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.lower()
        super().save(self, *args, **kwargs)
    
    def __str__(self):
        return self.name.title()
    
class Style(models.Model):
    name = models.CharField(max_length=20, unique= True)
    titles= models.ManyToManyField(Title, related_name= 'styles', blank= True)
    description = models.TextField(blank= True)
    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.lower()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name.title()
    
class Color(models.Model):
    name = models.CharField(max_length= 50, unique= True,)
    title= models.ManyToManyField(Title, related_name= 'colors', blank= True)
    hex_code= ColorField(default='#000000', unique= True)
    
    def __str__(self):
        return self.name.title()
    
    @classmethod
    def get_or_create_by_hex(cls, hex_code):
        # Automatically generate color name from hex code if not provided
        try:
            name = webcolors.hex_to_name(hex_code, spec='css3')
        except ValueError:
            rgb = webcolors.hex_to_rgb(hex_code)
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
    title = models.ForeignKey(Title, on_delete= models.PROTECT)
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
    occasion = models.CharField(max_length=20)
    style = models.CharField(max_length=20)
    color = models.CharField(max_length=20)
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