from decimal import Decimal

from celery import shared_task
from django.db import transaction

from billing.models import PaymentTransaction
from commission.models import CommissionLedger
from partners.models import CommissionAgreement, Partner


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
@transaction.atomic
def calculate_commission(self, transaction_id):
    transaction = PaymentTransaction.objects.select_related("client__owning_partner").get(id=transaction_id)
    client_partner = transaction.client.owning_partner
    if client_partner is None:
        return []

    hq = Partner.objects.filter(type="HQ").order_by("id").first()
    if hq is None:
        return []

    chain = []
    current = client_partner
    while current is not None:
        chain.append(current)
        if current.type == "HQ":
            break
        current = current.parent

    if not chain or chain[-1].type != "HQ":
        chain.append(hq)

    partner_chain = [partner for partner in reversed(chain) if partner.type != "HQ"]
    if not partner_chain:
        return []

    ordered_non_hq = list(reversed(partner_chain))
    tx_date = transaction.paid_at.date() if transaction.paid_at else transaction.created_at.date()
    transaction_total = Decimal(str(transaction.amount))

    created_rows = []
    for idx, current_partner in enumerate(ordered_non_hq):
        agreement = CommissionAgreement.objects.get_active_agreement(current_partner, tx_date)
        if agreement is None:
            continue

        if idx == len(ordered_non_hq) - 1:
            retained_percentage = agreement.pool_percentage
        else:
            child_partner = ordered_non_hq[idx + 1]
            child_agreement = CommissionAgreement.objects.get_active_agreement(child_partner, tx_date)
            child_percentage = child_agreement.pool_percentage if child_agreement else Decimal("0")
            retained_percentage = agreement.pool_percentage - child_percentage

        retained_amount = (transaction_total * retained_percentage) / Decimal("100")
        ledger_row, _ = CommissionLedger.objects.get_or_create(
            transaction_id=transaction.id,
            partner_id=current_partner.id,
            defaults={
                "retained_percentage": retained_percentage,
                "retained_amount": retained_amount,
            },
        )
        if ledger_row.retained_percentage != retained_percentage or ledger_row.retained_amount != retained_amount:
            ledger_row.retained_percentage = retained_percentage
            ledger_row.retained_amount = retained_amount
            ledger_row.save(update_fields=["retained_percentage", "retained_amount"])
        created_rows.append(ledger_row)

    top_partner_agreement = CommissionAgreement.objects.get_active_agreement(ordered_non_hq[0], tx_date)
    hq_retained_percentage = Decimal("100") - (top_partner_agreement.pool_percentage if top_partner_agreement else Decimal("0"))
    hq_retained_amount = (transaction_total * hq_retained_percentage) / Decimal("100")
    hq_row, _ = CommissionLedger.objects.get_or_create(
        transaction_id=transaction.id,
        partner_id=hq.id,
        defaults={
            "retained_percentage": hq_retained_percentage,
            "retained_amount": hq_retained_amount,
        },
    )
    if hq_row.retained_percentage != hq_retained_percentage or hq_row.retained_amount != hq_retained_amount:
        hq_row.retained_percentage = hq_retained_percentage
        hq_row.retained_amount = hq_retained_amount
        hq_row.save(update_fields=["retained_percentage", "retained_amount"])
    created_rows.append(hq_row)

    return [
        {
            "partner_id": row.partner_id,
            "retained_percentage": str(row.retained_percentage),
            "retained_amount": str(row.retained_amount),
        }
        for row in created_rows
    ]
