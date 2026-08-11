from datetime import datetime

from database import db
from models import Deal


# =========================================================
# CREATE DEAL FROM AI
# =========================================================

def create_deal_from_ai(user_id, email_id, deal_data):

    if not deal_data:
        return None

    company = deal_data.get("company")

    # A deal without a company is not useful
    if not company:
        return None

    # Prevent duplicate deal creation from same email
    existing_deal = Deal.query.filter_by(
        user_id=user_id,
        email_id=email_id
    ).first()

    if existing_deal:
        return existing_deal

    deal = Deal(
        user_id=user_id,
        email_id=email_id,

        company=company,

        contact_name=deal_data.get(
            "contact_name"
        ),

        contact_email=deal_data.get(
            "contact_email"
        ),

        deal_value=deal_data.get(
            "deal_value"
        ),

        currency=(
            deal_data.get("currency")
            or "USD"
        ),

        status=(
            deal_data.get("status")
            or "new"
        )
    )

    db.session.add(deal)
    db.session.commit()

    return deal


# =========================================================
# CREATE MANUAL DEAL
# =========================================================

def create_deal(
    user_id,
    company,
    contact_name=None,
    contact_email=None,
    deal_value=None,
    currency="USD",
    status="new",
    notes=None
):

    if not company:
        return None

    deal = Deal(
        user_id=user_id,

        company=company,

        contact_name=contact_name,
        contact_email=contact_email,

        deal_value=deal_value,
        currency=currency,

        status=status,

        notes=notes
    )

    db.session.add(deal)
    db.session.commit()

    return deal


# =========================================================
# GET ALL DEALS
# =========================================================

def get_deals(user_id):

    deals = (
        Deal.query
        .filter_by(user_id=user_id)
        .order_by(Deal.created_at.desc())
        .all()
    )

    results = []

    for deal in deals:

        results.append(
            deal_to_dict(deal)
        )

    return results


# =========================================================
# GET ONE DEAL
# =========================================================

def get_deal(user_id, deal_id):

    deal = Deal.query.filter_by(
        id=deal_id,
        user_id=user_id
    ).first()

    if not deal:
        return None

    return deal_to_dict(deal)


# =========================================================
# UPDATE DEAL STATUS
# =========================================================

def update_deal_status(
    user_id,
    deal_id,
    status
):

    deal = Deal.query.filter_by(
        id=deal_id,
        user_id=user_id
    ).first()

    if not deal:
        return None

    allowed_statuses = [
        "new",
        "contacted",
        "negotiating",
        "accepted",
        "in_progress",
        "completed",
        "paid",
        "rejected",
        "cancelled"
    ]

    if status not in allowed_statuses:
        return None

    deal.status = status

    db.session.commit()

    return deal_to_dict(deal)


# =========================================================
# UPDATE DEAL VALUE
# =========================================================

def update_deal_value(
    user_id,
    deal_id,
    deal_value,
    currency=None
):

    deal = Deal.query.filter_by(
        id=deal_id,
        user_id=user_id
    ).first()

    if not deal:
        return None

    deal.deal_value = deal_value

    if currency:
        deal.currency = currency

    db.session.commit()

    return deal_to_dict(deal)


# =========================================================
# UPDATE DEAL NOTES
# =========================================================

def update_deal_notes(
    user_id,
    deal_id,
    notes
):

    deal = Deal.query.filter_by(
        id=deal_id,
        user_id=user_id
    ).first()

    if not deal:
        return None

    deal.notes = notes

    db.session.commit()

    return deal_to_dict(deal)


# =========================================================
# UPDATE LAST REPLY
# =========================================================

def update_last_reply(
    user_id,
    deal_id,
    reply_time=None
):

    deal = Deal.query.filter_by(
        id=deal_id,
        user_id=user_id
    ).first()

    if not deal:
        return None

    deal.last_reply_at = (
        reply_time
        or datetime.utcnow()
    )

    db.session.commit()

    return deal_to_dict(deal)


# =========================================================
# SET NEXT FOLLOW-UP
# =========================================================

def set_next_follow_up(
    user_id,
    deal_id,
    follow_up_time
):

    deal = Deal.query.filter_by(
        id=deal_id,
        user_id=user_id
    ).first()

    if not deal:
        return None

    deal.next_follow_up = follow_up_time

    db.session.commit()

    return deal_to_dict(deal)


# =========================================================
# DELETE DEAL
# =========================================================

def delete_deal(user_id, deal_id):

    deal = Deal.query.filter_by(
        id=deal_id,
        user_id=user_id
    ).first()

    if not deal:
        return False

    db.session.delete(deal)
    db.session.commit()

    return True


# =========================================================
# DEAL TO DICTIONARY
# =========================================================

def deal_to_dict(deal):

    return {
        "id": deal.id,

        "company": deal.company,

        "contact_name": deal.contact_name,
        "contact_email": deal.contact_email,

        "deal_value": (
            float(deal.deal_value)
            if deal.deal_value is not None
            else None
        ),

        "currency": deal.currency,

        "status": deal.status,

        "notes": deal.notes,

        "email_id": deal.email_id,

        "last_reply_at": (
            deal.last_reply_at.isoformat()
            if deal.last_reply_at
            else None
        ),

        "next_follow_up": (
            deal.next_follow_up.isoformat()
            if deal.next_follow_up
            else None
        ),

        "created_at": (
            deal.created_at.isoformat()
            if deal.created_at
            else None
        ),

        "updated_at": (
            deal.updated_at.isoformat()
            if deal.updated_at
            else None
        )
    }