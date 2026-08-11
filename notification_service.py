from datetime import datetime, timedelta

from database import db
from models import FollowUp, Task, Payment, Meeting


# =========================================================
# CREATE FOLLOW-UP
# =========================================================

def create_follow_up(
    user_id,
    title,
    follow_up_at,
    deal_id=None,
    email_id=None
):

    if not title or not follow_up_at:
        return None

    follow_up_at = parse_datetime(
        follow_up_at
    )

    if not follow_up_at:
        return None

    # Prevent duplicate follow-up
    existing = FollowUp.query.filter_by(
        user_id=user_id,
        deal_id=deal_id,
        email_id=email_id,
        title=title,
        status="pending"
    ).first()

    if existing:
        return existing

    follow_up = FollowUp(
        user_id=user_id,

        deal_id=deal_id,
        email_id=email_id,

        title=title,

        follow_up_at=follow_up_at,

        status="pending"
    )

    db.session.add(follow_up)
    db.session.commit()

    return follow_up


# =========================================================
# CREATE FOLLOW-UP FROM AI
# =========================================================

def create_follow_up_from_ai(
    user_id,
    follow_up_data,
    deal_id=None,
    email_id=None
):

    if not follow_up_data:
        return None

    title = follow_up_data.get(
        "title"
    )

    follow_up_at = follow_up_data.get(
        "follow_up_at"
    )

    if not title or not follow_up_at:
        return None

    return create_follow_up(
        user_id=user_id,

        title=title,

        follow_up_at=follow_up_at,

        deal_id=deal_id,
        email_id=email_id
    )


# =========================================================
# GET FOLLOW-UPS
# =========================================================

def get_follow_ups(
    user_id,
    status=None
):

    query = FollowUp.query.filter_by(
        user_id=user_id
    )

    if status:
        query = query.filter_by(
            status=status
        )

    follow_ups = (
        query
        .order_by(
            FollowUp.follow_up_at.asc()
        )
        .all()
    )

    return [
        follow_up_to_dict(follow_up)
        for follow_up in follow_ups
    ]


# =========================================================
# COMPLETE FOLLOW-UP
# =========================================================

def complete_follow_up(
    user_id,
    follow_up_id
):

    follow_up = FollowUp.query.filter_by(
        id=follow_up_id,
        user_id=user_id
    ).first()

    if not follow_up:
        return None

    follow_up.status = "completed"

    db.session.commit()

    return follow_up_to_dict(
        follow_up
    )


# =========================================================
# DELETE FOLLOW-UP
# =========================================================

def delete_follow_up(
    user_id,
    follow_up_id
):

    follow_up = FollowUp.query.filter_by(
        id=follow_up_id,
        user_id=user_id
    ).first()

    if not follow_up:
        return False

    db.session.delete(follow_up)
    db.session.commit()

    return True


# =========================================================
# GET DUE FOLLOW-UPS
# =========================================================

def get_due_follow_ups(user_id):

    now = datetime.utcnow()

    follow_ups = FollowUp.query.filter(
        FollowUp.user_id == user_id,
        FollowUp.status == "pending",
        FollowUp.follow_up_at <= now
    ).order_by(
        FollowUp.follow_up_at.asc()
    ).all()

    return [
        follow_up_to_dict(follow_up)
        for follow_up in follow_ups
    ]


# =========================================================
# GET UPCOMING MEETINGS
# =========================================================

def get_upcoming_meeting_alerts(
    user_id,
    hours=24
):

    now = datetime.utcnow()

    until = now + timedelta(
        hours=hours
    )

    meetings = Meeting.query.filter(
        Meeting.user_id == user_id,
        Meeting.start_time.isnot(None),
        Meeting.start_time >= now,
        Meeting.start_time <= until
    ).order_by(
        Meeting.start_time.asc()
    ).all()

    alerts = []

    for meeting in meetings:

        alerts.append({
            "type": "meeting",

            "priority": "high",

            "title": meeting.title,

            "message": (
                "Upcoming meeting"
            ),

            "meeting_id": meeting.id,

            "time": (
                meeting.start_time.isoformat()
            ),

            "meeting_link": (
                meeting.meeting_link
            )
        })

    return alerts


# =========================================================
# GET DEADLINE ALERTS
# =========================================================

def get_task_deadline_alerts(
    user_id,
    hours=24
):

    now = datetime.utcnow()

    until = now + timedelta(
        hours=hours
    )

    tasks = Task.query.filter(
        Task.user_id == user_id,
        Task.status != "completed",
        Task.status != "cancelled",
        Task.deadline.isnot(None),
        Task.deadline >= now,
        Task.deadline <= until
    ).order_by(
        Task.deadline.asc()
    ).all()

    alerts = []

    for task in tasks:

        alerts.append({
            "type": "task",

            "priority": task.priority,

            "title": task.title,

            "message": (
                "Task deadline approaching"
            ),

            "task_id": task.id,

            "time": (
                task.deadline.isoformat()
            )
        })

    return alerts


# =========================================================
# GET OVERDUE PAYMENT ALERTS
# =========================================================

def get_overdue_payment_alerts(
    user_id
):

    now = datetime.utcnow()

    payments = Payment.query.filter(
        Payment.user_id == user_id,
        Payment.status.in_(
            ["pending", "overdue"]
        ),
        Payment.due_date.isnot(None),
        Payment.due_date < now
    ).order_by(
        Payment.due_date.asc()
    ).all()

    alerts = []

    for payment in payments:

        # Keep database status updated
        if payment.status == "pending":
            payment.status = "overdue"

        alerts.append({
            "type": "payment",

            "priority": "urgent",

            "title": "Payment overdue",

            "message": (
                f"{payment.currency} "
                f"{float(payment.amount):,.2f} "
                f"is overdue"
            ),

            "payment_id": payment.id,

            "deal_id": payment.deal_id,

            "amount": float(
                payment.amount
            ),

            "currency": (
                payment.currency
            ),

            "due_date": (
                payment.due_date.isoformat()
            )
        })

    db.session.commit()

    return alerts


# =========================================================
# GET FOLLOW-UP ALERTS
# =========================================================

def get_follow_up_alerts(user_id):

    follow_ups = get_due_follow_ups(
        user_id
    )

    alerts = []

    for follow_up in follow_ups:

        alerts.append({
            "type": "follow_up",

            "priority": "high",

            "title": (
                follow_up["title"]
            ),

            "message": (
                "Follow-up is due"
            ),

            "follow_up_id": (
                follow_up["id"]
            ),

            "deal_id": (
                follow_up["deal_id"]
            ),

            "email_id": (
                follow_up["email_id"]
            ),

            "time": (
                follow_up["follow_up_at"]
            )
        })

    return alerts


# =========================================================
# GET ALL IMPORTANT ALERTS
# =========================================================

def get_manager_alerts(user_id):

    alerts = []

    alerts.extend(
        get_overdue_payment_alerts(
            user_id
        )
    )

    alerts.extend(
        get_follow_up_alerts(
            user_id
        )
    )

    alerts.extend(
        get_task_deadline_alerts(
            user_id
        )
    )

    alerts.extend(
        get_upcoming_meeting_alerts(
            user_id
        )
    )

    priority_order = {
        "urgent": 1,
        "high": 2,
        "medium": 3,
        "low": 4
    }

    alerts.sort(
        key=lambda alert:
        priority_order.get(
            alert.get(
                "priority",
                "low"
            ),
            4
        )
    )

    return alerts


# =========================================================
# PARSE DATETIME
# =========================================================

def parse_datetime(value):

    if not value:
        return None

    if isinstance(value, datetime):
        return value

    try:

        return datetime.fromisoformat(
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


# =========================================================
# FOLLOW-UP TO DICTIONARY
# =========================================================

def follow_up_to_dict(
    follow_up
):

    return {
        "id": follow_up.id,

        "title": follow_up.title,

        "status": follow_up.status,

        "deal_id": follow_up.deal_id,

        "email_id": follow_up.email_id,

        "follow_up_at": (
            follow_up.follow_up_at.isoformat()
            if follow_up.follow_up_at
            else None
        ),

        "created_at": (
            follow_up.created_at.isoformat()
            if follow_up.created_at
            else None
        )
    }