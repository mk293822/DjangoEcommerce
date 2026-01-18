from django.contrib import admin

from apps.payments.models import Payout

# Register your models here.
@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    model = Payout