import logging

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from subscriptions.models import Expense, Subscription, add_months

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Generate renewal expenses for due subscriptions."

    def handle(self, *args, **options):
        today = timezone.localdate()
        due_subscriptions = Subscription.objects.filter(
            status=Subscription.Status.ACTIVE,
            next_renewal_date__isnull=False,
            next_renewal_date__lte=today,
        ).select_related("user", "category")  # Avoid N+1 queries for FK access.

        created = 0
        skipped = 0

        for subscription in due_subscriptions:
            due_date = subscription.next_renewal_date
            if not due_date:
                skipped += 1
                continue
            logger.info(
                "Due subscription_id=%s name=%s due_date=%s",
                subscription.id,
                subscription.name,
                due_date,
            )

            with transaction.atomic():
                exists = Expense.objects.filter(
                    subscription=subscription,
                    transaction_date=today,
                    source=Expense.Source.SUBSCRIPTION,
                ).exists()
                if exists:
                    skipped += 1
                    continue

                Expense.objects.create(
                    user=subscription.user,
                    subscription=subscription,
                    name=subscription.name,
                    category=subscription.category,
                    amount=subscription.amount,
                    currency=subscription.currency,
                    transaction_date=today,
                    source=Expense.Source.SUBSCRIPTION,
                )

                interval = max(1, subscription.billing_interval_months)
                subscription.next_renewal_date = add_months(today, interval)
                subscription.save(update_fields=["next_renewal_date", "updated_at"])
                created += 1

                transaction.on_commit(
                    lambda sid=subscription.id: logger.info(
                        "Renewal committed for subscription_id=%s", sid
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Renewals complete. Created: {created}, Skipped: {skipped}"
            )
        )
