from datetime import datetime

from database import db

from models import (
    Email,
    Meeting,
    FollowUp
)

from gmail_service import (
    get_recent_emails,
    clean_html_email,
    clean_email_text
)

from ai_service import (
    analyze_email
)

from crm_service import (
    create_deal_from_ai
)

from task_service import (
    create_task_from_ai
)

from finance_service import (
    create_payment_from_ai
)


# =========================================================
# SAVE EMAIL
# =========================================================

def save_email(
    user_id,
    email_data
):

    gmail_message_id = email_data.get(
        "gmail_message_id"
    )

    if not gmail_message_id:
        return None


    # =====================================================
    # CHECK EXISTING EMAIL
    # =====================================================

    existing_email = (
        Email.query.filter_by(
            user_id=user_id,
            gmail_message_id=gmail_message_id
        )
        .first()
    )


    # =====================================================
    # EXISTING EMAIL
    # CLEAN OLD RAW HTML
    # =====================================================

    if existing_email:

        if existing_email.body:

            try:

                existing_email.body = clean_html_email(
                    existing_email.body
                )

            except Exception:

                existing_email.body = clean_email_text(
                    existing_email.body
                )

            try:

                db.session.commit()

            except Exception as error:

                db.session.rollback()

                print(
                    "Existing email cleanup error:",
                    error
                )

        return existing_email


    # =====================================================
    # CLEAN NEW EMAIL BODY
    # =====================================================

    raw_body = email_data.get(
        "body",
        ""
    )

    clean_body = raw_body


    if raw_body:

        try:

            if (
                "<html" in raw_body.lower()
                or "<div" in raw_body.lower()
                or "<font" in raw_body.lower()
                or "<a " in raw_body.lower()
                or "<body" in raw_body.lower()
            ):

                clean_body = clean_html_email(
                    raw_body
                )

            else:

                clean_body = clean_email_text(
                    raw_body
                )

        except Exception as error:

            print(
                "Email body cleanup error:",
                error
            )

            clean_body = raw_body


    # =====================================================
    # AI ANALYSIS
    # =====================================================

    try:

        ai_result = analyze_email({

            "sender_name":
                email_data.get(
                    "sender_name",
                    ""
                ),

            "sender_email":
                email_data.get(
                    "sender_email",
                    ""
                ),

            "subject":
                email_data.get(
                    "subject",
                    ""
                ),

            "body":
                clean_body

        })


        if not ai_result:

            ai_result = {}

    except Exception as error:

        print(
            "Email AI analysis error:",
            error
        )

        ai_result = {}


    # =====================================================
    # CATEGORY
    # =====================================================

    category = ai_result.get(
        "category",
        "other"
    )


    allowed_categories = [

        "brand_deal",
        "payment",
        "collaboration",
        "meeting",
        "support",
        "spam",
        "other"

    ]


    if category not in allowed_categories:

        category = "other"


    # =====================================================
    # PRIORITY
    # =====================================================

    priority = ai_result.get(
        "priority",
        "low"
    )


    if priority == "high":

        priority = "medium"


    allowed_priorities = [

        "urgent",
        "medium",
        "low",
        "ignore"

    ]


    if priority not in allowed_priorities:

        priority = "low"


    # =====================================================
    # CREATE EMAIL
    # =====================================================

    email = Email(

        user_id=user_id,

        gmail_message_id=
            gmail_message_id,

        thread_id=
            email_data.get(
                "thread_id"
            ),

        sender_name=
            email_data.get(
                "sender_name"
            ),

        sender_email=
            email_data.get(
                "sender_email"
            ),

        subject=
            email_data.get(
                "subject"
            ),

        body=clean_body,

        category=category,

        priority=priority,

        is_read=
            email_data.get(
                "is_read",
                False
            ),

        received_at=
            normalize_datetime(
                email_data.get(
                    "received_at"
                )
            )

    )


    db.session.add(
        email
    )

    db.session.commit()


    # =====================================================
    # MANAGER AUTOMATION
    # =====================================================

    try:

        process_ai_actions(

            user_id=user_id,

            email=email,

            ai_result=ai_result

        )

    except Exception as error:

        print(
            "Manager automation error:",
            error
        )

        db.session.rollback()


    return email


# =========================================================
# MANAGER AI ACTIONS
# =========================================================

def process_ai_actions(
    user_id,
    email,
    ai_result
):

    if not ai_result:

        return


    # =====================================================
    # CREATE DEAL
    # =====================================================

    deal = None


    if ai_result.get(
        "create_deal",
        False
    ):

        deal_data = ai_result.get(
            "deal"
        )


        if deal_data:

            try:

                deal = create_deal_from_ai(

                    user_id=user_id,

                    email_id=email.id,

                    deal_data=deal_data

                )


                if deal:

                    print(
                        "Manager created deal:",
                        deal.company
                    )


            except Exception as error:

                print(
                    "Deal creation error:",
                    error
                )

                db.session.rollback()


    # =====================================================
    # CREATE TASK
    # =====================================================

    task = None


    if ai_result.get(
        "create_task",
        False
    ):

        task_data = ai_result.get(
            "task"
        )


        if task_data:

            try:

                task = create_task_from_ai(

                    user_id=user_id,

                    email_id=email.id,

                    task_data=task_data,

                    deal_id=(
                        deal.id
                        if deal
                        else None
                    )

                )


                if task:

                    print(
                        "Manager created task:",
                        task.title
                    )


            except Exception as error:

                print(
                    "Task creation error:",
                    error
                )

                db.session.rollback()


    # =====================================================
    # CREATE PAYMENT
    # =====================================================

    payment_data = ai_result.get(
        "payment"
    )


    if payment_data:

        try:

            payment = create_payment_from_ai(

                user_id=user_id,

                payment_data=payment_data,

                deal_id=(
                    deal.id
                    if deal
                    else None
                )

            )


            if payment:

                print(
                    "Manager created payment:",
                    payment.amount,
                    payment.currency
                )


        except Exception as error:

            print(
                "Payment creation error:",
                error
            )

            db.session.rollback()


    # =====================================================
    # CREATE FOLLOW-UP
    # =====================================================

    if ai_result.get(
        "create_follow_up",
        False
    ):

        follow_up_data = ai_result.get(
            "follow_up"
        )


        if follow_up_data:

            try:

                create_follow_up_from_ai(

                    user_id=user_id,

                    email_id=email.id,

                    deal_id=(
                        deal.id
                        if deal
                        else None
                    ),

                    follow_up_data=
                        follow_up_data

                )


            except Exception as error:

                print(
                    "Follow-up creation error:",
                    error
                )

                db.session.rollback()


    # =====================================================
    # CREATE MEETING
    # =====================================================

    meeting_data = ai_result.get(
        "meeting"
    )


    if meeting_data:

        try:

            create_meeting_from_ai(

                user_id=user_id,

                email_id=email.id,

                deal_id=(
                    deal.id
                    if deal
                    else None
                ),

                meeting_data=meeting_data

            )


        except Exception as error:

            print(
                "Meeting creation error:",
                error
            )

            db.session.rollback()


# =========================================================
# CREATE FOLLOW-UP
# =========================================================

def create_follow_up_from_ai(
    user_id,
    email_id,
    deal_id,
    follow_up_data
):

    if not follow_up_data:

        return None


    title = follow_up_data.get(
        "title"
    )


    follow_up_at = follow_up_data.get(
        "follow_up_at"
    )


    if not title:

        return None


    if not follow_up_at:

        return None


    follow_up_at = normalize_datetime(
        follow_up_at
    )


    if not follow_up_at:

        return None


    existing = (
        FollowUp.query.filter_by(

            user_id=user_id,

            email_id=email_id,

            title=title

        )
        .first()
    )


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


    db.session.add(
        follow_up
    )

    db.session.commit()


    print(
        "Manager created follow-up:",
        title
    )


    return follow_up


# =========================================================
# CREATE MEETING
# =========================================================

def create_meeting_from_ai(
    user_id,
    email_id,
    deal_id,
    meeting_data
):

    if not meeting_data:

        return None


    detected = meeting_data.get(
        "detected",
        False
    )


    if not detected:

        return None


    title = meeting_data.get(
        "title"
    )


    start_time = meeting_data.get(
        "start_time"
    )


    end_time = meeting_data.get(
        "end_time"
    )


    if not title:

        return None


    start_time = normalize_datetime(
        start_time
    )


    if not start_time:

        return None


    end_time = normalize_datetime(
        end_time
    )


    existing = (
        Meeting.query.filter_by(

            user_id=user_id,

            title=title,

            start_time=start_time

        )
        .first()
    )


    if existing:

        return existing


    meeting = Meeting(

        user_id=user_id,

        deal_id=deal_id,

        google_event_id=None,

        title=title,

        description=None,

        start_time=start_time,

        end_time=end_time,

        meeting_link=(
            meeting_data.get(
                "meeting_link"
            )
        )

    )


    db.session.add(
        meeting
    )

    db.session.commit()


    print(
        "Manager created meeting:",
        title
    )


    return meeting


# =========================================================
# SYNC INBOX
# =========================================================

def sync_inbox(
    user_id,
    max_results=20
):

    gmail_emails = get_recent_emails(

        max_results=max_results,

        user_id=user_id

    )


    synced_emails = []


    for email_data in gmail_emails:

        try:

            email = save_email(

                user_id=user_id,

                email_data=email_data

            )


            if email:

                synced_emails.append(

                    email_to_dict(
                        email
                    )

                )


        except Exception as error:

            db.session.rollback()

            print(
                "Inbox sync error:",
                error
            )


    return synced_emails


# =========================================================
# GET INBOX
# =========================================================

def get_inbox(
    user_id,
    category=None,
    priority=None,
    limit=50
):

    query = Email.query.filter_by(

        user_id=user_id

    )


    if category:

        query = query.filter_by(
            category=category
        )


    if priority:

        query = query.filter_by(
            priority=priority
        )


    emails = (

        query

        .order_by(
            Email.received_at.desc()
        )

        .limit(limit)

        .all()

    )


    return [

        email_to_dict(
            email
        )

        for email in emails

    ]


# =========================================================
# GET ONE EMAIL
# =========================================================

def get_email(
    user_id,
    email_id
):

    email = (

        Email.query.filter_by(

            id=email_id,

            user_id=user_id

        )

        .first()

    )


    if not email:

        return None


    return email_to_dict(
        email
    )


# =========================================================
# GET IMPORTANT EMAILS
# =========================================================

def get_important_emails(
    user_id,
    limit=20
):

    emails = (

        Email.query

        .filter(

            Email.user_id == user_id,

            Email.priority.in_([
                "urgent",
                "medium"
            ]),

            Email.category != "spam"

        )

        .order_by(
            Email.received_at.desc()
        )

        .limit(limit)

        .all()

    )


    return [

        email_to_dict(
            email
        )

        for email in emails

    ]


# =========================================================
# MARK EMAIL READ
# =========================================================

def mark_email_read(
    user_id,
    email_id
):

    email = (

        Email.query.filter_by(

            id=email_id,

            user_id=user_id

        )

        .first()

    )


    if not email:

        return None


    email.is_read = True

    db.session.commit()


    return email_to_dict(
        email
    )


# =========================================================
# UPDATE EMAIL PRIORITY
# =========================================================

def update_email_priority(
    user_id,
    email_id,
    priority
):

    allowed_priorities = [

        "urgent",
        "medium",
        "low",
        "ignore"

    ]


    if priority not in allowed_priorities:

        return None


    email = (

        Email.query.filter_by(

            id=email_id,

            user_id=user_id

        )

        .first()

    )


    if not email:

        return None


    email.priority = priority

    db.session.commit()


    return email_to_dict(
        email
    )


# =========================================================
# UPDATE EMAIL CATEGORY
# =========================================================

def update_email_category(
    user_id,
    email_id,
    category
):

    allowed_categories = [

        "brand_deal",

        "payment",

        "collaboration",

        "meeting",

        "support",

        "spam",

        "other"

    ]


    if category not in allowed_categories:

        return None


    email = (

        Email.query.filter_by(

            id=email_id,

            user_id=user_id

        )

        .first()

    )


    if not email:

        return None


    email.category = category

    db.session.commit()


    return email_to_dict(
        email
    )


# =========================================================
# NORMALIZE DATETIME
# =========================================================

def normalize_datetime(
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

                str(value).replace(
                    "Z",
                    "+00:00"
                )

            )

        except (
            ValueError,
            TypeError
        ):

            return None


    if parsed.tzinfo is not None:

        from datetime import timezone

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
# EMAIL TO DICTIONARY
# =========================================================

def email_to_dict(
    email
):

    return {

        "id":
            email.id,

        "gmail_message_id":
            email.gmail_message_id,

        "thread_id":
            email.thread_id,

        "sender_name":
            email.sender_name,

        "sender_email":
            email.sender_email,

        "subject":
            email.subject,

        "body":
            email.body,

        "category":
            email.category,

        "priority":
            email.priority,

        "is_read":
            email.is_read,

        "received_at": (

            email.received_at.isoformat()

            if email.received_at

            else None

        ),

        "created_at": (

            email.created_at.isoformat()

            if email.created_at

            else None

        )

    }