from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, BodyMeasurement, BraSize, OutfitImage, ClothingItem, Outfit, FavoriteOutfit

class CustomUserAdmin(UserAdmin):
    # Remove username from fieldsets and add your custom fields
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'dob')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    # Change ordering to use email instead of username
    ordering = ('email',)
    # Update list_display to show relevant fields
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    # Update add_fieldsets for creating users in admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'dob'),
        }),
    )

# Register your models with the custom admin class
admin.site.register(User, CustomUserAdmin)
admin.site.register(BodyMeasurement)
admin.site.register(BraSize)
admin.site.register(OutfitImage)
admin.site.register(ClothingItem)
admin.site.register(Outfit)
admin.site.register(FavoriteOutfit)