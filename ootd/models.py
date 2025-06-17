"""
Models required:
1. Closet- The user can upload the photos of their clothes. Later outfit can be made by combining the cloth items from the closet

"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class BodyMeasurement(models.Model):
    BODY_TYPES= [
        ('hourglass','Hourglass'),
        ('pear','Pear'),
        ('apple','Apple'),
        ('rectangle','Rectangle'),
        ('inverted','Inverted Triangle'),
    ]
    
    user = models.ForeignKey("User", verbose_name=_("User"), on_delete=models.CASCADE)
    bust = models.FloatField(_("Bust"),validators=[MinValueValidator(20), MaxValueValidator(80)])
    waist = models.FloatField(_("Waist"),validators=[MinValueValidator(20), MaxValueValidator(80)])
    hips = models.FloatField(_("Hips"),validators=[MinValueValidator(20), MaxValueValidator(80)])
    body_type = models.CharField(_("Body Type"), max_length=50, choices=BODY_TYPES, blank= True)
    last_updated = models.DateTimeField(_("Last Updated"), auto_now=True)
    
    def save(self,*args, **kwargs):
        # Auto-calculate body type when saving
        self.calculate_body_type()
        super().save(*args, **kwargs)
        
    def calculate_body_type(self):
        if self.bust == self.hips and self.waist < self.bust:
            self.body_type = 'hourglass'
        elif self.hips > self.bust and self.hips > self.waist:
            self.body_type = 'pear'
        elif self.waist > self.bust and self.waist > self.hips:
            self.body_type = 'apple'
        elif abs(self.bust - self.hips) <= 1 and abs(self.bust - self.waist) <= 1:
            self.body_type = 'rectangle'
        elif self.bust > self.hips and self.bust > self.waist:
            self.body_type = 'inverted'
        else:
            self.body_type = ''
            
class BraSize(models.Model):
    user = models.ForeignKey("User", verbose_name=_("User"), on_delete=models.CASCADE)
    underbust = models.FloatField(validators=[MinValueValidator(20), MaxValueValidator(60)])
    overbust = models.FloatField(validators=[MinValueValidator(20), MaxValueValidator(80)])
    band_size = models.PositiveSmallIntegerField()
    cup_size = models.CharField(max_length=2)
    last_updated = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Auto-calculate bra size when saving
        self.calculate_size()
        super().save(*args, **kwargs)
    
    def calculate_size(self):
        # Calculate band size (round to nearest even number)
        self.band_size = round(self.underbust / 2) * 2
        
        # Calculate cup size
        difference = self.overbust - self.underbust
        cup_sizes = ['AA', 'A', 'B', 'C', 'D', 'DD', 'E', 'F', 'G', 'H']
        index = min(max(0, int(difference - 1)), len(cup_sizes) - 1)
        self.cup_size = cup_sizes[index] 
        