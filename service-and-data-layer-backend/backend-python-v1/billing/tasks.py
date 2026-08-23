from celery import shared_task

from .models import PaymentTransaction


@shared_task(bind=True, default_retry_delay=30, max_retries=3)
def calculate_commission(self, transaction_id):
    transaction = PaymentTransaction.objects.select_related("client", "package").get(id=transaction_id)
    # Placeholder commission logic; real implementation can be expanded later.
    return {
        "transaction_id": transaction.id,
        "client_id": transaction.client_id,
        "package_id": transaction.package_id,
        "amount": str(transaction.amount),
        "status": "processed",
    }
