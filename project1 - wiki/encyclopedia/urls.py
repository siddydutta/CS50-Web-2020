from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<title>", views.get_title, name="title"),
    path("search", views.search, name="search"),
    path("create", views.create, name="create"),
    path("edit/<title>", views.edit, name="edit"),
    path('random', views.random, name="random"),
]
