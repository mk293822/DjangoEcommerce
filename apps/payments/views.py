from django.conf import settings
from django.shortcuts import redirect, render
from django.db import transaction
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import stripe
import json
from apps.carts.models import CartItem
from apps.carts.services import CartServices
from apps.orders.models import Order, OrderItem
from apps.orders import choices
from apps.products.services.product_details import ProductServices

stripe.api_key = settings.STRIPE_API_KEY


@login_required
@transaction.atomic
def stripe_success(request):
    session_id = request.GET.get('session_id')

    if not session_id:
        return redirect('stripe_failure')

    try:
        # =============================
        # STRIPE FETCH
        # =============================
        session = stripe.checkout.Session.retrieve(session_id)
        payment_intent = stripe.PaymentIntent.retrieve(
            session.payment_intent
        )

        if payment_intent.status != 'succeeded':
            return redirect('stripe_failure')
        
        # =============================
        # FETCH ORDERS
        # =============================
        orders = Order.objects.prefetch_related(
            'items__product',
            'items__variation',
            'vendor__vendor_details',
        ).filter(
            stripe_checkout_session_id=session.id
        )

        if not orders.exists():
            messages.error(request, f"No orders found for session {session.id}")
            return redirect('stripe_failure')

        product_ids_to_remove = []

        # =============================
        # UPDATE ORDERS + STOCK
        # =============================
        for order in orders:
            order.stripe_payment_intent_id = payment_intent.id
            order.status = choices.Status.PAID
            order.save(update_fields=[
                'stripe_payment_intent_id',
                'status'
            ])

            for item in order.items.all():
                product_ids_to_remove.append(item.product_id)

                if item.variation:
                    item.variation.stock -= item.quantity
                    item.variation.save(update_fields=['stock'])
                else:
                    item.product.stock -= item.quantity
                    item.product.save(update_fields=['stock'])

        # =============================
        # CLEAR CART
        # =============================
        CartItem.objects.filter(
            cart__user=request.user,
            product_id__in=product_ids_to_remove
        ).delete()

        # =============================
        # FEES CALCULATION
        # =============================

        platform_fee_percent = settings.PLATFORM_FEE_PERCENT

        for order in orders:
            order.platform_fee = (order.total_amount * platform_fee_percent) / 100
            order.vendor_amount = (
                order.total_amount - order.platform_fee
            )

            order.save(update_fields=[
                'platform_fee',
                'vendor_amount'
            ])

        return render(request, 'payments/stripe_success.html', {
            'orders': orders,
        })

    except stripe.error.StripeError as e:
        messages.error(request, "Stripe API error")
        return redirect('stripe_failure')

    except Exception as e:
        messages.error(request, f"Unexpected error in stripe_success view {e}")
        return redirect('stripe_failure')
    
    
def stripe_failure(request):
    context = {
        "js_messages": json.dumps([
        {"tags": m.tags, "text": m.message} 
        for m in messages.get_messages(request)
    ])
    }
    return render(request, 'payments/stripe_failure.html', context)


@login_required(login_url='login')
@require_POST
def checkout(request):
    user = request.user
    vendor_id = request.POST.get("vendor_id")

    all_cart_items = CartServices.get_grouped_cart_items(user)

    # normalize data → ALWAYS LIST
    if vendor_id:
        try:
            checkout_cart_items = [all_cart_items[int(vendor_id)]]
        except KeyError:
            messages.error(request, "Invalid vendor.")
            return redirect("carts")
    else:
        checkout_cart_items = list(all_cart_items.values())

    try:
        with transaction.atomic():
            orders = []
            stripe_line_items = []

            for data in checkout_cart_items:
                vendor = data["vendor"]
                cart_items = data["items"]
                total_price = data["total_price"]

                order = Order.objects.create(
                    user=user,
                    vendor=vendor,
                    total_amount=total_price,
                    status=choices.Status.DRAFT
                )
                orders.append(order)

                for row in cart_items:
                    cart_item = row["cart_item"]

                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        price=cart_item.price(),
                        variation=cart_item.variation
                    )
                    
                    options = ProductServices.get_selected_options(
                        product=cart_item.product, 
                        variation=cart_item.variation,
                        return_ids=False,
                        match_product_price=False,
                    )
                    
                    description = ", ".join([
                        f"{type_name}: {option.name}" for type_name, option in options.items()
                    ])

                    line_item = {
                        "price_data": {
                            "currency": settings.CURRENCY_FORMAT,
                            "product_data": {
                                "name": cart_item.product.name,
                                "images": [cart_item.image]
                            },
                            "unit_amount": int(cart_item.price() * 100),
                        },
                        "quantity": cart_item.quantity,
                    }
                    
                    if description:
                        line_item["price_data"]["product_data"]["description"] = description
                        
                        
                    stripe_line_items.append(line_item)
                    
            session = stripe.checkout.Session.create(
                customer_email=user.email,
                line_items=stripe_line_items,
                mode="payment",
                success_url=request.build_absolute_uri(reverse('stripe_success')) + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=request.build_absolute_uri(reverse('stripe_failure')),
            )
            
            for order in orders:
                order.stripe_checkout_session_id = session.id
                order.save(update_fields=['stripe_checkout_session_id'])
                
            return redirect(session.url)
    except Exception as e:
        print("Checkout exception:", e)
        messages.error(request, f"Something went wrong.")
        return redirect("carts")


