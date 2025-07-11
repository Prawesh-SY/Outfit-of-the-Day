
from django.contrib import admin
from django.urls import path, include
from . import views

from django.conf import settings
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter
from .viewsets import TitleViewSet

router = DefaultRouter()
router.register(r'titles', TitleViewSet)

urlpatterns = [
    # Core Pages
    path("", views.index, name="home"),
    path("about/", views.about, name="about"),

    # Authentication
    path("signup/", views.sign_up, name="signup"),
    path("login/", views.log_in, name="login"),
    path("logout/", views.log_out, name="logout"),

    # Profile & User Data
    path("profile/", views.profile, name="profile"),
    path("body/", views.body, name="body"),
    path("cup/", views.cup, name="cup"),
    path("closet/", views.closet, name="closet"),

    # Outfit Logic
    path("outfit/", views.outfit, name="outfit"),
    path("favorites/", views.favorite_outfits, name="favorite_outfits"),
    path("favorites/toggle/<int:outfit_id>/", views.toggle_favorite, name="toggle_favorite"),
    
    # Body Type
    path("body/", views.body_type_view, name="body_calculator"),
    

    # API
    path("body-type/", views.get_body_type, name="get_body_type"),
    path('', include(router.urls)),
]

# This serves static files during development and handles media files uploaded by the users
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
