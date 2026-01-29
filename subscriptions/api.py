from rest_framework import viewsets

from .models import Category, Expense, Subscription
from .serializers import CategorySerializer, ExpenseSerializer, SubscriptionSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all().order_by("next_renewal_date", "name")
    serializer_class = SubscriptionSerializer


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all().order_by("-transaction_date", "-id")
    serializer_class = ExpenseSerializer
