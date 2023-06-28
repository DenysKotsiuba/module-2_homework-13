from django.urls import path

from . import views


app_name = "quotes"

urlpatterns = [
    path("", views.main, name="root"),
    path("add_quote/", views.add_quote, name="add_quote"),
    path("<int:page>", views.main, name="root_paginate"),
]