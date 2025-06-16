# from django.db import models
# from django.contrib.auth.models import User
# from django.core.validators import MinValueValidator, MaxValueValidator

# class ClothingItem(models.Model):
#     CATEGORY_CHOICES= [
#         ()
#     ]
    

#     class Meta:
#         verbose_name = _("ClothingItem")
#         verbose_name_plural = _("ClothingItems")

#     def __str__(self):
#         return f"{self.name} ({self.category})"

#     def get_absolute_url(self):
#         return reverse("ClothingItem_detail", kwargs={"pk": self.pk})
