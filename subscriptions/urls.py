from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .api import CategoryViewSet, ExpenseViewSet, SubscriptionViewSet

router = DefaultRouter()
router.register("api/categories", CategoryViewSet)
router.register("api/subscriptions", SubscriptionViewSet)
router.register("api/expenses", ExpenseViewSet)

urlpatterns = [
    path("api/expenses-legacy/", views.expenses_list, name="api_expenses_legacy"),
    path("api/monthly-spend/", views.monthly_spend, name="api_monthly_spend"),
    path("", include(router.urls)),
]
