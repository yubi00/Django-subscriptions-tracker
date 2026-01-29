from django.urls import path

from . import views

urlpatterns = [
    path("api/expenses/", views.expenses_list, name="api_expenses"),
    path("api/monthly-spend/", views.monthly_spend, name="api_monthly_spend"),
]
