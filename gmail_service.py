import base64
import re

from datetime import datetime, timezone

from flask import session, current_app

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from bs4 import BeautifulSoup

from database import db
from models import User


# =========================================================
# GET CURRENT USER
# =========================================================

def get_current_user(user_id=None):

    if user_id:
        return db.session.get(
            User,
            user_id
        )

    session_user_id = session.get(
        "user_id"
    )

    if not session_user_id:
        return None

    return db.session.get(
        User,
        session_user_id
    )


# =========================================================
# GOOGLE CREDENTIALS
# =========================================================

def get_google_credentials(user_id=None):

    user = get_current_user(
        user_id=user_id
    )

    if not user:
        return None

    if not user.google_access_token:
        return None

    expiry = user.google_token_expiry

    if expiry and expiry.tzinfo is None:

        expiry = expiry.replace(
            tzinfo=timezone.utc
        )

    credentials = Credentials(
        token=user.google_access_token,

        refresh_token=(
            user.google_refresh_token
        ),

        token_uri=(
            "https://oauth2.googleapis.com/token"
        ),

        client_id=(
            current_app.config.get(
                "GOOGLE_CLIENT_ID"
            )
        ),

        client_secret=(
            current_app.config.get(
                "GOOGLE_CLIENT_SECRET"
            )
        ),

        expiry=expiry
    )

    # -----------------------------------------------------
    # REFRESH TOKEN
    # -----------------------------------------------------

    if (
        credentials.expired
        and credentials.refresh_token
    ):

        try:

            credentials.refresh(
                Request()
            )

            user.google_access_token = (
                credentials.token
            )

            if credentials.refresh_token:

                user.google_refresh_token = (
                    credentials.refresh_token
                )

            if credentials.expiry:

                new_expiry = (
                    credentials.expiry
                )

                if new_expiry.tzinfo:

                    new_expiry = (
                        new_expiry
                        .astimezone(
                            timezone.utc
                        )
                        .replace(
                            tzinfo=None
                        )
                    )

                user.google_token_expiry = (
                    new_expiry
                )

            db.session.commit()

        except Exception as error:

            db.session.rollback()

            print(
                "Google token refresh error:",
                error
            )

            return None

    return credentials


# =========================================================
# GMAIL SERVICE
# =========================================================

def get_gmail_service(user_id=None):

    credentials = (
        get_google_credentials(
            user_id=user_id
        )
    )

    if not credentials:
        return None

    try:

        return build(
            "gmail",
            "v1",
            credentials=credentials
        )

    except Exception as error:

        print(
            "Gmail service error:",
            error
        )

        return None


# =========================================================
# GET RECENT EMAILS
# =========================================================

def get_recent_emails(
    max_results=20,
    user_id=None
):

    service = get_gmail_service(
        user_id=user_id
    )

    if not service:
        return []

    try:

        response = (
            service.users()
            .messages()
            .list(
                userId="me",
                maxResults=max_results
            )
            .execute()
        )

        messages = response.get(
            "messages",
            []
        )

        emails = []

        for message in messages:

            message_id = message.get(
                "id"
            )

            email_data = (
                get_email_details(
                    service,
                    message_id
                )
            )

            if email_data:

                emails.append(
                    email_data
                )

        return emails

    except Exception as error:

        print(
            "Gmail fetch error:",
            error
        )

        return []


# =========================================================
# GET EMAIL DETAILS
# =========================================================

def get_email_details(
    service,
    message_id
):

    if not service:
        return None

    if not message_id:
        return None

    try:

        message = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=message_id,
                format="full"
            )
            .execute()
        )

        payload = message.get(
            "payload",
            {}
        )

        headers = payload.get(
            "headers",
            []
        )

        # -------------------------------------------------
        # SUBJECT
        # -------------------------------------------------

        subject = get_header(
            headers,
            "Subject"
        )

        # -------------------------------------------------
        # SENDER
        # -------------------------------------------------

        sender = get_header(
            headers,
            "From"
        )

        sender_name, sender_email = (
            parse_sender(
                sender
            )
        )

        # -------------------------------------------------
        # BODY
        # -------------------------------------------------

        body = extract_email_body(
            payload
        )

        # -------------------------------------------------
        # READ / UNREAD
        # -------------------------------------------------

        label_ids = message.get(
            "labelIds",
            []
        )

        is_read = (
            "UNREAD"
            not in label_ids
        )

        # -------------------------------------------------
        # DATE
        # -------------------------------------------------

        received_at = None

        internal_date = message.get(
            "internalDate"
        )

        if internal_date:

            try:

                received_at = (
                    datetime.fromtimestamp(
                        int(internal_date)
                        / 1000,
                        tz=timezone.utc
                    )
                    .replace(
                        tzinfo=None
                    )
                )

            except (
                ValueError,
                TypeError
            ):

                received_at = None

        return {

            "gmail_message_id":
                message.get("id"),

            "thread_id":
                message.get(
                    "threadId"
                ),

            "sender_name":
                sender_name,

            "sender_email":
                sender_email,

            "subject":
                subject,

            "body":
                body,

            "is_read":
                is_read,

            "received_at":
                received_at
        }

    except Exception as error:

        print(
            "Gmail message error:",
            message_id,
            error
        )

        return None


# =========================================================
# GET HEADER
# =========================================================

def get_header(
    headers,
    name
):

    if not headers:
        return ""

    for header in headers:

        header_name = header.get(
            "name",
            ""
        )

        if (
            header_name.lower()
            == name.lower()
        ):

            return header.get(
                "value",
                ""
            )

    return ""


# =========================================================
# PARSE SENDER
# =========================================================

def parse_sender(sender):

    if not sender:
        return "", ""

    if (
        "<" in sender
        and ">" in sender
    ):

        name = (
            sender
            .split("<")[0]
            .strip()
            .strip('"')
        )

        email = (
            sender
            .split("<")[1]
            .split(">")[0]
            .strip()
        )

        return (
            name,
            email
        )

    return (
        "",
        sender.strip()
    )


# =========================================================
# EXTRACT EMAIL BODY
# =========================================================

def extract_email_body(payload):

    if not payload:
        return ""

    # -----------------------------------------------------
    # TEXT/PLAIN FIRST
    # -----------------------------------------------------

    plain_text = find_plain_text(
        payload
    )

    if plain_text:

        return clean_email_text(
            plain_text
        )

    # -----------------------------------------------------
    # HTML FALLBACK
    # -----------------------------------------------------

    html = find_html(
        payload
    )

    if html:

        return clean_html_email(
            html
        )

    return ""


# =========================================================
# FIND TEXT/PLAIN RECURSIVELY
# =========================================================

def find_plain_text(part):

    if not part:
        return ""

    mime_type = part.get(
        "mimeType",
        ""
    )

    body_data = (
        part
        .get(
            "body",
            {}
        )
        .get("data")
    )

    if (
        mime_type == "text/plain"
        and body_data
    ):

        return decode_base64(
            body_data
        )

    parts = part.get(
        "parts",
        []
    )

    for child in parts:

        result = find_plain_text(
            child
        )

        if result:
            return result

    return ""


# =========================================================
# FIND HTML RECURSIVELY
# =========================================================

def find_html(part):

    if not part:
        return ""

    mime_type = part.get(
        "mimeType",
        ""
    )

    body_data = (
        part
        .get(
            "body",
            {}
        )
        .get("data")
    )

    if (
        mime_type == "text/html"
        and body_data
    ):

        return decode_base64(
            body_data
        )

    parts = part.get(
        "parts",
        []
    )

    for child in parts:

        result = find_html(
            child
        )

        if result:
            return result

    return ""


# =========================================================
# CLEAN HTML EMAIL
# =========================================================

def clean_html_email(html):

    if not html:
        return ""

    try:

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        for element in soup.find_all(
            [
                "script",
                "style",
                "noscript",
                "head",
                "meta",
                "title",
                "svg",
                "iframe",
                "form"
            ]
        ):

            element.decompose()

        # Remove tracking / empty links
        for link in soup.find_all(
            "a"
        ):

            visible_text = (
                link.get_text(
                    " ",
                    strip=True
                )
            )

            if visible_text:

                link.replace_with(
                    visible_text
                )

            else:

                link.decompose()

        # Remove images
        for image in soup.find_all(
            "img"
        ):

            alt = image.get(
                "alt",
                ""
            ).strip()

            if alt:

                image.replace_with(
                    alt
                )

            else:

                image.decompose()

        text = soup.get_text(
            "\n",
            strip=True
        )

        return clean_email_text(
            text
        )

    except Exception as error:

        print(
            "HTML cleaning error:",
            error
        )

        return clean_email_text(
            html
        )


# =========================================================
# CLEAN EMAIL TEXT
# =========================================================

def clean_email_text(text):

    if not text:
        return ""

    text = str(text)

    # -----------------------------------------------------
    # HTML ENTITIES
    # -----------------------------------------------------

    replacements = {
        "&nbsp;": " ",
        "&amp;": "&",
        "&lt;": "<",
        "&gt;": ">",
        "&quot;": '"',
        "&#39;": "'"
    }

    for old, new in replacements.items():

        text = text.replace(
            old,
            new
        )

    # -----------------------------------------------------
    # INVISIBLE CHARACTERS
    # -----------------------------------------------------

    text = re.sub(
        r"[\u200B\u200C\u200D\uFEFF]",
        "",
        text
    )

    # -----------------------------------------------------
    # MARKDOWN LINKS
    # -----------------------------------------------------

    text = re.sub(
        r"\[([^\]]+)\]\([^)]+\)",
        r"\1",
        text
    )

    # -----------------------------------------------------
    # RAW URLS
    # -----------------------------------------------------

    text = re.sub(
        r"https?://\S+",
        "",
        text,
        flags=re.IGNORECASE
    )

    # -----------------------------------------------------
    # NORMALIZE
    # -----------------------------------------------------

    text = (
        text
        .replace(
            "\r\n",
            "\n"
        )
        .replace(
            "\r",
            "\n"
        )
    )

    raw_lines = text.split(
        "\n"
    )

    lines = []

    for line in raw_lines:

        line = re.sub(
            r"[ \t]+",
            " ",
            line
        ).strip()

        if line:

            lines.append(
                line
            )

    # -----------------------------------------------------
    # REMOVE EMAIL FOOTER
    # -----------------------------------------------------

    stop_phrases = [

        "unsubscribe",

        "privacy policy",

        "legal documents",

        "terms and conditions",

        "terms & conditions",

        "manage your preferences",

        "email preferences",

        "notification settings",

        "update your notification settings",

        "do not reply to this email",

        "please do not reply",

        "view this email as a web page",

        "view this email in your browser",

        "if you no longer wish to receive",

        "you are receiving this email because",

        "you're receiving this email because",

        "this email was sent to",

        "this email was intended for",

        "you received this email because",

        "all rights reserved",

        "legal notice",

        "risk warning"
    ]

    cleaned = []

    for line in lines:

        lower_line = line.lower()

        found_stop = False

        for phrase in stop_phrases:

            if phrase in lower_line:

                found_stop = True
                break

        if found_stop:

            break

        cleaned.append(
            line
        )

    lines = cleaned

    # -----------------------------------------------------
    # REMOVE SOCIAL FOOTER ITEMS
    # -----------------------------------------------------

    social_words = {
        "facebook",
        "instagram",
        "linkedin",
        "youtube",
        "spotify",
        "twitter",
        "tiktok"
    }

    filtered = []

    for line in lines:

        if (
            line
            .lower()
            .strip()
            in social_words
        ):

            continue

        filtered.append(
            line
        )

    lines = filtered

    # -----------------------------------------------------
    # REMOVE TRACKING GARBAGE
    # -----------------------------------------------------

    final_lines = []

    for line in lines:

        line = re.sub(
            r"https?://\S+",
            "",
            line
        ).strip()

        if not line:
            continue

        lower_line = line.lower()

        if (
            len(line) > 300
            and (
                "mkt_tok" in lower_line
                or "utm_" in lower_line
                or "email." in lower_line
            )
        ):

            continue

        final_lines.append(
            line
        )

    # -----------------------------------------------------
    # REMOVE DUPLICATES
    # -----------------------------------------------------

    result = []

    previous = ""

    for line in final_lines:

        normalized = (
            line
            .lower()
            .strip()
        )

        if normalized == previous:
            continue

        result.append(
            line
        )

        previous = normalized

    # -----------------------------------------------------
    # FINAL BODY
    # -----------------------------------------------------

    text = "\n".join(
        result
    )

    text = re.sub(
        r"[ ]{2,}",
        " ",
        text
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    if len(text) > 12000:

        text = (
            text[:12000]
            + "\n\n[Email content truncated]"
        )

    return text.strip()


# =========================================================
# DECODE BASE64
# =========================================================

def decode_base64(data):

    if not data:
        return ""

    try:

        decoded = (
            base64.urlsafe_b64decode(
                data + "==="
            )
        )

        return decoded.decode(
            "utf-8",
            errors="ignore"
        )

    except Exception as error:

        print(
            "Email decode error:",
            error
        )

        return ""