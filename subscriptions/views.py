from django.db.models import Sum
from django.http import JsonResponse
from django.utils import timezone

from .models import Expense


def expenses_list(request):
    expenses = Expense.objects.select_related("category", "subscription", "user").order_by(
        "-transaction_date", "-id"
    )
    data = [
        {
            "id": expense.id,
            "name": expense.name,
            "amount": str(expense.amount),
            "currency": expense.currency,
            "transaction_date": expense.transaction_date.isoformat(),
            "source": expense.source,
            "category": expense.category.name if expense.category_id else None,
            "subscription": expense.subscription.name if expense.subscription_id else None,
            "user": expense.user.username,
        }
        for expense in expenses
    ]
    return JsonResponse(data, safe=False)


def monthly_spend(request):
    today = timezone.localdate()
    total = (
        Expense.objects.filter(
            transaction_date__year=today.year,
            transaction_date__month=today.month,
        ).aggregate(total=Sum("amount"))["total"]
        or 0
    )
    data = {
        "month": today.strftime("%Y-%m"),
        "total": str(total),
        "currency": "AUD",
    }
    return JsonResponse(data)
