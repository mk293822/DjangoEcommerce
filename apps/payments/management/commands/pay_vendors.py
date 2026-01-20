from django.utils import timezone
from django.conf import settings
from django.core.management.base import BaseCommand
import stripe
from django.db import transaction
from apps.payments.models import Payout
from apps.payments.choices import Status

stripe.api_key = settings.STRIPE_API_KEY

class Command(BaseCommand):
    help = "Pay vendors based on Payout records"

    def handle(self, *args, **options):
        payouts = Payout.objects.select_related("vendor").filter(
            status=Status.PENDING
        )

        self.stdout.write(f"Processing {payouts.count()} payouts...")
        

        for payout in payouts:
            vendor_user = payout.vendor
            vendor = vendor_user.vendor_details
            

            if not vendor.can_receive_payouts:
                self._mark_failed(payout, "Vendor not connected to Stripe")
                continue

            amount_cents = int(payout.amount * 100)

            if amount_cents <= 0:
                self._mark_failed(payout, "Invalid payout amount")
                continue
            
            balance = stripe.Balance.retrieve()
            available_usd = next(
                (b.amount for b in balance.available if b.currency == "usd"), 0
            )
            if payout.amount * 100 > available_usd:
                self._mark_failed(payout, "Insufficient available balance")
                continue

            try:
                with transaction.atomic():
                    transfer = stripe.Transfer.create(
                        amount=amount_cents,
                        currency="usd",
                        destination=vendor.stripe_account_id,
                        description=f"Payout {payout.id}",
                        metadata={
                            "payout_id": str(payout.id),
                            "vendor_id": str(vendor_user.id),
                        },
                    )

                    payout.stripe_transfer_id = transfer.id
                    payout.status = Status.PAID
                    payout.updated_at = timezone.now()
                    payout.until = timezone.now()
                    payout.save(update_fields=[
                        "stripe_transfer_id",
                        "status",
                        "updated_at",
                        "until"
                    ])

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Paid {vendor_user.email} → {payout.amount}"
                        )
                    )

            except Exception as e:
                self._mark_failed(payout, str(e))

        self.stdout.write("Payout job finished.")

    # ----------------------------------

    def _mark_failed(self, payout, reason):
        payout.status = Status.FAILED
        payout.save(update_fields=["status"])
        self.stderr.write(
            self.style.ERROR(
                f"Payout {payout.id} failed: {reason}"
            )
        )
