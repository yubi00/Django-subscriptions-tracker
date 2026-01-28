from django import forms
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, reverse

from .models import Category, Expense, Subscription


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user", "created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ("user",)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "user",
        "category",
        "billing_cycle",
        "billing_date",
        "amount",
        "currency",
        "next_renewal_date",
        "status",
        "updated_at",
    )
    list_filter = ("status", "billing_cycle", "category", "user")
    search_fields = ("name",)


class ExpenseAdminForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        subscription_id = None
        if self.data:
            subscription_id = self.data.get("subscription") or None
        elif self.instance and self.instance.subscription_id:
            subscription_id = self.instance.subscription_id

        if subscription_id:
            for field_name in (
                "source",
                "category",
                "amount",
                "currency",
                "transaction_date",
            ):
                self.fields[field_name].required = False

        info_url = reverse(
            "admin:subscriptions_expense_subscription_info", args=[0]
        ).rsplit("0/", 1)[0]
        self.fields["subscription"].widget.attrs["data-subscription-info-url"] = (
            info_url
        )

    def clean(self):
        cleaned = super().clean()
        subscription = cleaned.get("subscription")
        if subscription:
            cleaned["source"] = Expense.Source.SUBSCRIPTION
            cleaned.setdefault("name", subscription.name)
            cleaned.setdefault("category", subscription.category)
            cleaned.setdefault("amount", subscription.amount)
            cleaned.setdefault("currency", subscription.currency)
            cleaned.setdefault("transaction_date", subscription.billing_date)
        return cleaned


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    form = ExpenseAdminForm
    list_display = (
        "id",
        "name",
        "transaction_date",
        "amount",
        "currency",
        "category",
        "source",
        "subscription",
        "user",
        "updated_at",
    )
    list_filter = ("source", "category", "user")
    search_fields = ("notes",)

    class Media:
        js = ("subscriptions/expense_admin.js",)

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "subscription-info/<int:subscription_id>/",
                self.admin_site.admin_view(self.subscription_info),
                name="subscriptions_expense_subscription_info",
            )
        ]
        return custom + urls

    def subscription_info(self, request, subscription_id: int):
        subscription = Subscription.objects.get(pk=subscription_id)
        data = {
            "name": subscription.name,
            "amount": str(subscription.amount),
            "currency": subscription.currency,
            "category_id": subscription.category_id,
            "transaction_date": subscription.billing_date.isoformat(),
        }
        return JsonResponse(data)
