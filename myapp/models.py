from django.utils.translation import gettext_lazy as _ 
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator
import os




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
        """Automatically determine body type based on measurements"""
        if abs(self.bust - self.hips) <= 1 and self.waist < min(self.bust, self.hips) - 2:
            self.body_type = 'hourglass'
        elif self.hips > self.bust + 2 and self.hips > self.waist:
            self.body_type = 'pear'
        elif self.waist > self.bust and self.waist > self.hips:
            self.body_type = 'apple'
        elif abs(self.bust - self.hips) <= 1 and abs(self.bust - self.waist) <= 1:
            self.body_type = 'rectangle'
        elif self.bust > self.hips + 2 and self.bust > self.waist:
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

class OutfitImage(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['style']),
            models.Index(fields=['color']),
        ]
    def image_upload_path(instance, filename):
        return os.path.join('outfits', filename)

    image = models.ImageField(upload_to=image_upload_path)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    style = models.CharField(max_length=20, choices=STYLE_CHOICES)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES)
    
    occasions = models.CharField(
        max_length=200,
        help_text="Comma-separated occasions from: work, wedding, date, vacation, daily"
    )
    
    # Compatibility will be calculated dynamically
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_style_display()})"

    def get_occasion_list(self):
        return [occ.strip() for occ in self.occasions.split(',')]

    def get_compatibility_score(self, occasion, style, color):
        """
        Calculate compatibility score based on provided rules
        Returns a tuple of (score)
        """
        COMPATIBILITY_RULES = {
              # Occasion: Work
            ('work', 'casual','black'): 8,
            ('work', 'casual','white'): 8,
            ('work', 'casual','red'): 8,
            ('work', 'casual','any'): 7,
            
            ('work', 'formal','black'): 10,
            ('work', 'formal','white'): 10,
            ('work', 'formal','red'): 10,
            ('work', 'formal','any'): 9,
            
            ('work', 'ethnic','black'): 9,
            ('work', 'ethnic','white'): 9,
            ('work', 'ethnic','red'): 8,
            ('work', 'ethnic','any'): 9,
            
            ('work', 'party','black'): 9,
            ('work', 'party','white'): 8,
            ('work', 'party','red'): 9,
            ('work', 'party','any'): 9,
            
            ('work', 'sporty','black'): 3,
            ('work', 'sporty','white'): 3,
            ('work', 'sporty','red'): 2,
            ('work', 'sporty','any'): 2,
            
            # Occasion: Wedding
            ('wedding', 'casual','black'): 5,
            ('wedding', 'casual','white'): 5,
            ('wedding', 'casual','red'): 5,
            ('wedding', 'casual','any'): 5,
            
            ('wedding', 'formal','black'): 7,
            ('wedding', 'formal','white'): 7,
            ('wedding', 'formal','red'): 8,
            ('wedding', 'formal','any'): 8,
            
            ('wedding', 'ethnic','black'): 9,
            ('wedding', 'ethnic','white'): 8,
            ('wedding', 'ethnic','red'): 10,
            ('wedding', 'ethnic','any'): 9,
            
            ('wedding', 'party','black'): 9,
            ('wedding', 'party','white'): 7,
            ('wedding', 'party','red'): 10,
            ('wedding', 'party','any'): 9,
            
            ('wedding', 'sporty','black'): 0,
            ('wedding', 'sporty','white'): 0,
            ('wedding', 'sporty','red'): 0,
            ('wedding', 'sporty','any'): 0,
            
            # Occasion: Date
            ('date', 'casual','black'): 7,
            ('date', 'casual','white'): 8,
            ('date', 'casual','red'): 9,
            ('date', 'casual','any'): 9,
            
            ('date', 'formal','black'): 10,
            ('date', 'formal','white'): 10,
            ('date', 'formal','red'): 10,
            ('date', 'formal','any'): 9,
            
            ('date', 'ethnic','black'): 9,
            ('date', 'ethnic','white'): 8,
            ('date', 'ethnic','red'): 10,
            ('date', 'ethnic','any'): 10,
            
            ('date', 'party','black'): 8,
            ('date', 'party','white'): 8,
            ('date', 'party','red'): 9,
            ('date', 'party','any'): 9,
            
            ('date', 'sporty','black'): 7,
            ('date', 'sporty','white'): 7,
            ('date', 'sporty','red'): 8,
            ('date', 'sporty','any'): 8,
            
            # Occasion: Vacation
            ('vacation', 'casual','black'): 9,
            ('vacation', 'casual','white'): 9,
            ('vacation', 'casual','red'): 10,
            ('vacation', 'casual','any'): 10,
            
            ('vacation', 'formal','black'): 9,
            ('vacation', 'formal','white'): 9,
            ('vacation', 'formal','red'): 10,
            ('vacation', 'formal','any'): 10,
            
            ('vacation', 'ethnic','black'): 10,
            ('vacation', 'ethnic','white'): 10,
            ('vacation', 'ethnic','red'): 10,
            ('vacation', 'ethnic','any'): 10,
            
            ('vacation', 'party','black'): 9,
            ('vacation', 'party','white'): 9,
            ('vacation', 'party','red'): 10,
            ('vacation', 'party','any'): 10,
            
            ('vacation', 'sporty','black'): 10,
            ('vacation', 'sporty','white'): 8,
            ('vacation', 'sporty','red'): 9,
            ('vacation', 'sporty','any'): 9,
            
            # Occasion: Daily
            ('daily', 'casual','white'): 9,
            ('daily', 'casual','black'): 9,
            ('daily', 'casual','red'): 8,
            ('daily', 'casual','any'): 10,
            
            ('daily', 'formal','black'): 10,
            ('daily', 'formal','white'): 10,
            ('daily', 'formal','red'): 10,
            ('daily', 'formal','any'): 9,
            
            ('daily', 'ethnic','black'): 10,
            ('daily', 'ethnic','white'): 9,
            ('daily', 'ethnic','red'): 10,
            ('daily', 'ethnic','any'): 10,
            
            ('daily', 'party','black'): 9,
            ('daily', 'party','white'): 7,
            ('daily', 'party','red'): 7,
            ('daily', 'party','any'): 10,
            
            ('daily', 'sporty','black'): 10,
            ('daily', 'sporty','white'): 5,
            ('daily', 'sporty','red'): 7,
            ('daily', 'sporty','any'): 8,
        }
        
        key = (occasion, style, color)
        return COMPATIBILITY_RULES.get(key, 0)

class ClothingItem(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['style']),
            models.Index(fields=['color']),
        ]
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
    style = models.CharField(max_length=20, choices=STYLE_CHOICES)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES)
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

# 