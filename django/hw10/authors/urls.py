from django.urls import path

from . import views


app_name = "authors"

urlpatterns = [
    path("add_author/", views.add_author, name="add_author" ),
    path("<str:author_fullname>/", views.author, name="author"),
]
