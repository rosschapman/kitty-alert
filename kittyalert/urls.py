"""
URL configuration for kittyalert project.

The `urlpatterns` list routes URLs to views. For more information please see:
        https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
        1. Add an import:  from my_app import views
        2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
        1. Add an import:  from other_app.views import Home
        2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
        1. Import the include() function: from django.urls import include, path
        2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.home, name="home"),
    path(
        "adopters/<int:adopter_id>/", views.adopter_dashboard, name="adopter_dashboard"
    ),
    path(
        "shelters/<int:shelter_id>/",
        views.shelter_kitty_list,
        name="shelter_kitty_list",
    ),
    path("adopters/<int:adopter_id>/save/", views.kitty_save, name="kitty_save"),
    path(
        "adopters/<int:adopter_id>/unsave/<int:kitty_id>/",
        views.kitty_unsave,
        name="kitty_unsave",
    ),
    path(
        "adopters/<int:adopter_id>/subscribe/<int:shelter_id>/",
        views.subscribe_to_shelter,
        name="subscribe_to_shelter",
    ),
    path(
        "adopters/<int:adopter_id>/unsubscribe/<int:shelter_id>/",
        views.unsubscribe_from_shelter,
        name="unsubscribe_from_shelter",
    ),
] + debug_toolbar_urls()
