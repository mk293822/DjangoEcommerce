# services/user_services.py
import stripe
from django.conf import settings


class UserServices:
    
    stripe.api_key = settings.STRIPE_API_KEY

    @staticmethod
    def create_express_account(user):
        """
        Create Stripe Express account for vendor
        """
        vendor = user.vendor_details
        account = stripe.Account.create(
            type="express",
            email=user.email,
            capabilities={
                "transfers": {"requested": True},
            },
        )

        vendor.stripe_account_id = account.id
        vendor.save()

        return account
    
    @staticmethod
    def create_onboarding_link(vendor, refresh_url, return_url):
        return stripe.AccountLink.create(
            account=vendor.stripe_account_id,
            refresh_url=refresh_url,
            return_url=return_url,
            type="account_onboarding",
        )

    @staticmethod
    def update_user_information(post_data, files, user):
        name = post_data.get("name", "").strip()
        email = post_data.get("email", "").strip()
        avatar = files.get("avatar")

        fields = []

        # ---- changes ----
        if name != user.name:
            user.name = name
            fields.append("name")

        if email != user.email:
            user.email = email
            fields.append("email")

        if avatar:
            user.avatar = avatar
            fields.append("avatar")

        if not fields:
            return {"updated": False}

        user.save(update_fields=fields)

        return {"updated": True}
        