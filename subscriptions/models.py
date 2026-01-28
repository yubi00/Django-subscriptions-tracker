import calendar
from datetime import date

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


def add_months(value: date, months: int) -> date:
    """Return a date advanced by N months, clamped to month end when needed."""
    year = value.year + (value.month - 1 + months) // 12
    month = (value.month - 1 + months) % 12 + 1
    last_day = calendar.monthrange(year, month)[1]
    day = min(value.day, last_day)
    return date(year, month, day)


class Category(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categories",
    )
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"], name="uniq_category_name_per_user"
            )
        ]
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Subscription(models.Model):
    class BillingCycle(models.TextChoices):
        # First value is stored in DB, second is human-readable label.
        MONTHLY = "monthly", "Monthly"
        YEARLY = "yearly", "Yearly"
        CUSTOM = "custom", "Custom"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    name = models.CharField(max_length=200)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="subscriptions"
    )
    billing_cycle = models.CharField(
        max_length=10, choices=BillingCycle.choices, default=BillingCycle.MONTHLY
    )
    billing_interval_months = models.PositiveSmallIntegerField(
        default=1,
        help_text="For custom billing: every N months. Auto-set for monthly/yearly.",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="AUD")
    billing_date = models.DateField(help_text="Anchor date for billing calculations.")
    next_renewal_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.ACTIVE
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gte=0),
                name="subscription_amount_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(billing_interval_months__gte=1),
                name="subscription_interval_min_1",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "status"]),
        ]
        ordering = ["next_renewal_date", "name"]

    def clean(self) -> None:
        """Model validation hook used by Django admin and full_clean()."""
        super().clean()
        if self.billing_cycle == self.BillingCycle.MONTHLY:
            self.billing_interval_months = 1
        elif self.billing_cycle == self.BillingCycle.YEARLY:
            self.billing_interval_months = 12

    def save(self, *args, **kwargs):
        """Normalize interval + compute next renewal before saving."""
        if self.billing_cycle == self.BillingCycle.MONTHLY:
            self.billing_interval_months = 1
        elif self.billing_cycle == self.BillingCycle.YEARLY:
            self.billing_interval_months = 12

        if not self.next_renewal_date and self.billing_date:
            months = self.billing_interval_months
            self.next_renewal_date = add_months(self.billing_date, months)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name} ({self.amount} {self.currency})"


class Expense(models.Model):
    class Source(models.TextChoices):
        SUBSCRIPTION = "subscription", "Subscription"
        MANUAL = "manual", "Manual"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expenses",
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="expenses",
    )
    name = models.CharField(max_length=200)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="expenses",
        null=True,
        blank=True,
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="AUD")
    transaction_date = models.DateField(help_text="When the expense actually happened.")
    source = models.CharField(
        max_length=12, choices=Source.choices, default=Source.MANUAL
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gte=0),
                name="expense_amount_non_negative",
            )
        ]
        indexes = [
            models.Index(fields=["transaction_date"]),
            models.Index(fields=["user", "transaction_date"]),
        ]
        ordering = ["-transaction_date", "-id"]

    def clean(self) -> None:
        """Validate source/subscription/category consistency."""
        super().clean()
        if not self.name:
            raise ValidationError({"name": "Name is required."})
        if self.subscription and self.source != self.Source.SUBSCRIPTION:
            raise ValidationError(
                {
                    "source": "Source must be 'subscription' when linked to a subscription."
                }
            )
        if not self.subscription and self.source == self.Source.SUBSCRIPTION:
            raise ValidationError(
                {
                    "subscription": "Subscription is required when source is 'subscription'."
                }
            )
        if not self.category and not self.subscription:
            raise ValidationError(
                {"category": "Category is required for manual expenses."}
            )

    def save(self, *args, **kwargs):
        """Auto-fill fields from subscription before saving."""
        if self.subscription:
            self.source = self.Source.SUBSCRIPTION
            if not self.name:
                self.name = self.subscription.name
            if not self.category:
                self.category = self.subscription.category
            if not self.amount:
                self.amount = self.subscription.amount
            if not self.currency:
                self.currency = self.subscription.currency
            if not self.transaction_date:
                self.transaction_date = self.subscription.billing_date
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.amount} {self.currency} on {self.transaction_date}"
