from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from database import db
from models import Payment


# =========================================================
# CREATE PAYMENT FROM AI
# =========================================================

def create_payment_from_ai(
    user_id,
    payment_data,
    deal_id=None
):

    if not payment_data:
        return None

    if not payment_data.get(
        "detected",
        False
    ):
        return None

    amount = parse_amount(
        payment_data.get("amount")
    )

    if amount is None:
        return None

    currency = (
        payment_data.get("currency")
        or "USD"
    ).upper()

    status = (
        payment_data.get("status")
        or "pending"
    ).lower()

    allowed_statuses = [
        "pending",
        "paid",
        "overdue",
        "cancelled"
    ]

    if status not in allowed_statuses:
        status = "pending"

    due_date = parse_datetime(
        payment_data.get("due_date")
    )

    # -----------------------------------------------------
    # DUPLICATE PROTECTION
    # -----------------------------------------------------

    existing_payment = None

    if deal_id:

        existing_payment = (
            Payment.query.filter_by(
                user_id=user_id,
                deal_id=deal_id,
                amount=amount,
                currency=currency
            ).first()
        )

    if existing_payment:

        if status == "paid":

            existing_payment.status = "paid"

            if not existing_payment.paid_at:

                existing_payment.paid_at = (
                    datetime.utcnow()
                )

        if due_date:

            existing_payment.due_date = (
                due_date
            )

        db.session.commit()

        return existing_payment

    # -----------------------------------------------------
    # CREATE
    # -----------------------------------------------------

    payment = Payment(

        user_id=user_id,

        deal_id=deal_id,

        amount=amount,

        currency=currency,

        status=status,

        due_date=due_date
    )

    if status == "paid":

        payment.paid_at = (
            datetime.utcnow()
        )

    db.session.add(payment)

    db.session.commit()

    return payment


# =========================================================
# CREATE MANUAL PAYMENT
# =========================================================

def create_payment(
    user_id,
    amount,
    currency="USD",
    status="pending",
    invoice_number=None,
    due_date=None,
    deal_id=None
):

    amount = parse_amount(
        amount
    )

    if amount is None:
        return None

    currency = (
        currency
        or "USD"
    ).upper()

    allowed_statuses = [
        "pending",
        "paid",
        "overdue",
        "cancelled"
    ]

    if status not in allowed_statuses:

        status = "pending"

    if isinstance(
        due_date,
        str
    ):

        due_date = parse_datetime(
            due_date
        )

    payment = Payment(

        user_id=user_id,

        deal_id=deal_id,

        amount=amount,

        currency=currency,

        status=status,

        invoice_number=invoice_number,

        due_date=due_date
    )

    if status == "paid":

        payment.paid_at = (
            datetime.utcnow()
        )

    db.session.add(payment)

    db.session.commit()

    return payment


# =========================================================
# GET PAYMENTS
# =========================================================

def get_payments(
    user_id,
    status=None
):

    query = Payment.query.filter_by(
        user_id=user_id
    )

    if status:

        query = query.filter_by(
            status=status
        )

    payments = (
        query
        .order_by(
            Payment.created_at.desc()
        )
        .all()
    )

    return [
        payment_to_dict(payment)
        for payment in payments
    ]


# =========================================================
# GET ONE PAYMENT
# =========================================================

def get_payment(
    user_id,
    payment_id
):

    payment = Payment.query.filter_by(

        id=payment_id,

        user_id=user_id

    ).first()

    if not payment:
        return None

    return payment_to_dict(
        payment
    )


# =========================================================
# MARK PAYMENT PAID
# =========================================================

def mark_payment_paid(
    user_id,
    payment_id
):

    payment = Payment.query.filter_by(

        id=payment_id,

        user_id=user_id

    ).first()

    if not payment:
        return None

    payment.status = "paid"

    payment.paid_at = (
        datetime.utcnow()
    )

    db.session.commit()

    return payment_to_dict(
        payment
    )


# =========================================================
# UPDATE PAYMENT STATUS
# =========================================================

def update_payment_status(
    user_id,
    payment_id,
    status
):

    allowed_statuses = [
        "pending",
        "paid",
        "overdue",
        "cancelled"
    ]

    if status not in allowed_statuses:
        return None

    payment = Payment.query.filter_by(

        id=payment_id,

        user_id=user_id

    ).first()

    if not payment:
        return None

    payment.status = status

    if status == "paid":

        if not payment.paid_at:

            payment.paid_at = (
                datetime.utcnow()
            )

    else:

        payment.paid_at = None

    db.session.commit()

    return payment_to_dict(
        payment
    )


# =========================================================
# UPDATE INVOICE
# =========================================================

def update_invoice(
    user_id,
    payment_id,
    invoice_number=None,
    due_date=None
):

    payment = Payment.query.filter_by(

        id=payment_id,

        user_id=user_id

    ).first()

    if not payment:
        return None

    if invoice_number is not None:

        payment.invoice_number = (
            invoice_number
        )

    if due_date is not None:

        if isinstance(
            due_date,
            str
        ):

            due_date = parse_datetime(
                due_date
            )

        payment.due_date = due_date

    db.session.commit()

    return payment_to_dict(
        payment
    )


# =========================================================
# CHECK OVERDUE PAYMENTS
# =========================================================

def check_overdue_payments(
    user_id
):

    now = datetime.utcnow()

    payments = Payment.query.filter(

        Payment.user_id == user_id,

        Payment.status == "pending",

        Payment.due_date.isnot(None),

        Payment.due_date < now

    ).all()

    updated = []

    for payment in payments:

        payment.status = "overdue"

        updated.append(
            payment
        )

    db.session.commit()

    return [
        payment_to_dict(payment)
        for payment in updated
    ]


# =========================================================
# FINANCE SUMMARY
# =========================================================

def get_finance_summary(
    user_id
):

    payments = Payment.query.filter_by(
        user_id=user_id
    ).all()

    paid = {}

    pending = {}

    overdue = {}

    for payment in payments:

        currency = (
            payment.currency
            or "USD"
        )

        amount = Decimal(
            str(payment.amount)
        )

        if payment.status == "paid":

            paid[currency] = (

                paid.get(
                    currency,
                    Decimal("0")
                )

                + amount

            )

        elif payment.status == "pending":

            pending[currency] = (

                pending.get(
                    currency,
                    Decimal("0")
                )

                + amount

            )

        elif payment.status == "overdue":

            overdue[currency] = (

                overdue.get(
                    currency,
                    Decimal("0")
                )

                + amount

            )

    return {

        "paid":
            convert_money_dict(
                paid
            ),

        "pending":
            convert_money_dict(
                pending
            ),

        "overdue":
            convert_money_dict(
                overdue
            ),

        "payment_count":
            len(payments)

    }


# =========================================================
# DELETE PAYMENT
# =========================================================

def delete_payment(
    user_id,
    payment_id
):

    payment = Payment.query.filter_by(

        id=payment_id,

        user_id=user_id

    ).first()

    if not payment:
        return False

    db.session.delete(
        payment
    )

    db.session.commit()

    return True


# =========================================================
# PARSE AMOUNT
# =========================================================

def parse_amount(
    value
):

    if value is None:
        return None

    try:

        return Decimal(
            str(value)
        )

    except (
        InvalidOperation,
        ValueError,
        TypeError
    ):

        return None


# =========================================================
# PARSE DATETIME
# =========================================================

def parse_datetime(
    value
):

    if not value:
        return None

    if isinstance(
        value,
        datetime
    ):

        parsed = value

    else:

        try:

            parsed = datetime.fromisoformat(

                value.replace(
                    "Z",
                    "+00:00"
                )

            )

        except (
            ValueError,
            TypeError
        ):

            return None

    # -----------------------------------------------------
    # CONVERT TIMEZONE-AWARE DATETIME
    # TO NAIVE UTC DATETIME
    # -----------------------------------------------------

    if parsed.tzinfo is not None:

        parsed = (
            parsed
            .astimezone(
                timezone.utc
            )
            .replace(
                tzinfo=None
            )
        )

    return parsed


# =========================================================
# MONEY DICTIONARY
# =========================================================

def convert_money_dict(
    data
):

    return {

        currency: float(
            amount
        )

        for currency, amount
        in data.items()

    }


# =========================================================
# PAYMENT TO DICTIONARY
# =========================================================

def payment_to_dict(
    payment
):

    return {

        "id":
            payment.id,

        "deal_id":
            payment.deal_id,

        "amount":
            float(
                payment.amount
            ),

        "currency":
            payment.currency,

        "status":
            payment.status,

        "invoice_number":
            payment.invoice_number,

        "due_date": (

            payment.due_date.isoformat()

            if payment.due_date

            else None

        ),

        "paid_at": (

            payment.paid_at.isoformat()

            if payment.paid_at

            else None

        ),

        "created_at": (

            payment.created_at.isoformat()

            if payment.created_at

            else None

        )

    }