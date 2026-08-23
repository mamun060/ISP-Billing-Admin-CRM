from decimal import Decimal

from django.db import IntegrityError, transaction

from .models import Client, PaymentTransaction
from .tasks import calculate_commission


def record_payment(client_id, amount, method, gateway_ref):
    amount = Decimal(str(amount))
    if amount <= 0:
        raise ValueError("Payment amount must be greater than zero.")

    client = Client.objects.get(pk=client_id)

    try:
        with transaction.atomic():
            existing = PaymentTransaction.objects.filter(gateway_ref=gateway_ref).first()
            if existing:
                if existing.status == "paid":
                    return existing
                raise IntegrityError("Duplicate gateway reference detected.")

            transaction_obj = PaymentTransaction.objects.create(
                client=client,
                package=client.package,
                amount=amount,
                method=method,
                gateway_ref=gateway_ref,
                status="paid",
                paid_at=transaction.now(),
            )

            calculate_commission.delay(transaction_obj.id)
            return transaction_obj
    except IntegrityError:
        raise ValueError("Duplicate gateway reference detected.")
