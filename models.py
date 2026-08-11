from datetime import datetime

from database import db


# =========================================================
# USER
# =========================================================

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    google_id = db.Column(
        db.String(255),
        unique=True,
        nullable=False
    )

    name = db.Column(
        db.String(150)
    )

    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False
    )

    profile_picture = db.Column(
        db.Text
    )


    # -----------------------------------------------------
    # GOOGLE OAUTH CREDENTIALS
    # -----------------------------------------------------

    google_access_token = db.Column(
        db.Text
    )

    google_refresh_token = db.Column(
        db.Text
    )

    google_token_expiry = db.Column(
        db.DateTime
    )


    # -----------------------------------------------------
    # ACCOUNT
    # -----------------------------------------------------

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# =========================================================
# EMAIL
# =========================================================

class Email(db.Model):
    __tablename__ = "emails"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    gmail_message_id = db.Column(
        db.String(255),
        nullable=False
    )

    thread_id = db.Column(
        db.String(255)
    )

    sender_name = db.Column(
        db.String(150)
    )

    sender_email = db.Column(
        db.String(255)
    )

    subject = db.Column(
        db.Text
    )

    body = db.Column(
        db.Text
    )

    category = db.Column(
        db.String(50),
        default="other"
    )

    priority = db.Column(
        db.String(20),
        default="low"
    )

    is_read = db.Column(
        db.Boolean,
        default=False
    )

    received_at = db.Column(
        db.DateTime
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "gmail_message_id",
            name="unique_user_gmail_message"
        ),
    )


# =========================================================
# BRAND DEAL
# =========================================================

class Deal(db.Model):
    __tablename__ = "deals"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    email_id = db.Column(
        db.Integer,
        db.ForeignKey("emails.id")
    )

    company = db.Column(
        db.String(150),
        nullable=False
    )

    contact_name = db.Column(
        db.String(150)
    )

    contact_email = db.Column(
        db.String(255)
    )

    deal_value = db.Column(
        db.Numeric(12, 2)
    )

    currency = db.Column(
        db.String(10),
        default="USD"
    )

    status = db.Column(
        db.String(50),
        default="new"
    )

    last_reply_at = db.Column(
        db.DateTime
    )

    next_follow_up = db.Column(
        db.DateTime
    )

    notes = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


# =========================================================
# TASK
# =========================================================

class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    deal_id = db.Column(
        db.Integer,
        db.ForeignKey("deals.id")
    )

    email_id = db.Column(
        db.Integer,
        db.ForeignKey("emails.id")
    )

    title = db.Column(
        db.String(255),
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    priority = db.Column(
        db.String(20),
        default="medium"
    )

    status = db.Column(
        db.String(30),
        default="pending"
    )

    deadline = db.Column(
        db.DateTime
    )

    created_by_ai = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    completed_at = db.Column(
        db.DateTime
    )


# =========================================================
# MEETING
# =========================================================

class Meeting(db.Model):
    __tablename__ = "meetings"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    deal_id = db.Column(
        db.Integer,
        db.ForeignKey("deals.id")
    )

    google_event_id = db.Column(
        db.String(255)
    )

    title = db.Column(
        db.String(255),
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    start_time = db.Column(
        db.DateTime
    )

    end_time = db.Column(
        db.DateTime
    )

    meeting_link = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# =========================================================
# DRIVE FILE
# =========================================================

class DriveFile(db.Model):
    __tablename__ = "drive_files"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    deal_id = db.Column(
        db.Integer,
        db.ForeignKey("deals.id")
    )

    google_file_id = db.Column(
        db.String(255),
        nullable=False
    )

    name = db.Column(
        db.String(255),
        nullable=False
    )

    file_type = db.Column(
        db.String(100)
    )

    category = db.Column(
        db.String(50),
        default="other"
    )

    drive_url = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "google_file_id",
            name="unique_user_drive_file"
        ),
    )


# =========================================================
# PAYMENT
# =========================================================

class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    deal_id = db.Column(
        db.Integer,
        db.ForeignKey("deals.id")
    )

    amount = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    currency = db.Column(
        db.String(10),
        default="USD"
    )

    status = db.Column(
        db.String(30),
        default="pending"
    )

    invoice_number = db.Column(
        db.String(100)
    )

    due_date = db.Column(
        db.DateTime
    )

    paid_at = db.Column(
        db.DateTime
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# =========================================================
# FOLLOW UP
# =========================================================

class FollowUp(db.Model):
    __tablename__ = "follow_ups"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    deal_id = db.Column(
        db.Integer,
        db.ForeignKey("deals.id")
    )

    email_id = db.Column(
        db.Integer,
        db.ForeignKey("emails.id")
    )

    title = db.Column(
        db.String(255),
        nullable=False
    )

    follow_up_at = db.Column(
        db.DateTime,
        nullable=False
    )

    status = db.Column(
        db.String(30),
        default="pending"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )