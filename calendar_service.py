from datetime import datetime, timezone

from flask import session, current_app

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from database import db
from models import User, Meeting


# =========================================================
# GET USER
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

    # Database stores token expiry as naive UTC.
    # Keep it naive when passing it to Google Credentials.

    expiry = user.google_token_expiry

    credentials = Credentials(
        token=user.google_access_token,

        refresh_token=user.google_refresh_token,

        token_uri=(
            "https://oauth2.googleapis.com/token"
        ),

        client_id=current_app.config.get(
            "GOOGLE_CLIENT_ID"
        ),

        client_secret=current_app.config.get(
            "GOOGLE_CLIENT_SECRET"
        ),

        expiry=expiry
    )


    # -----------------------------------------------------
    # REFRESH TOKEN IF EXPIRED
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

                # Store naive UTC datetime
                if new_expiry.tzinfo:

                    new_expiry = (
                        new_expiry.replace(
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
# CALENDAR SERVICE
# =========================================================

def get_calendar_service(
    user_id=None
):

    credentials = (
        get_google_credentials(
            user_id=user_id
        )
    )

    if not credentials:
        return None

    try:

        return build(
            "calendar",
            "v3",
            credentials=credentials
        )

    except Exception as error:

        print(
            "Calendar service error:",
            error
        )

        return None


# =========================================================
# UPCOMING EVENTS
# =========================================================

def get_upcoming_events(
    max_results=20,
    user_id=None
):

    service = get_calendar_service(
        user_id=user_id
    )

    if not service:
        return []

    try:

        now = datetime.now(
            timezone.utc
        ).isoformat()

        response = (
            service.events()
            .list(
                calendarId="primary",

                timeMin=now,

                maxResults=max_results,

                singleEvents=True,

                orderBy="startTime"
            )
            .execute()
        )

        events = response.get(
            "items",
            []
        )

        results = []

        for event in events:

            start = event.get(
                "start",
                {}
            )

            end = event.get(
                "end",
                {}
            )

            results.append({

                "google_event_id": (
                    event.get("id")
                ),

                "title": event.get(
                    "summary",
                    "Untitled Meeting"
                ),

                "description": (
                    event.get(
                        "description"
                    )
                ),

                "start_time": (
                    start.get("dateTime")
                    or start.get("date")
                ),

                "end_time": (
                    end.get("dateTime")
                    or end.get("date")
                ),

                "meeting_link": (
                    get_meeting_link(
                        event
                    )
                )
            })

        return results

    except Exception as error:

        print(
            "Calendar fetch error:",
            error
        )

        return []


# =========================================================
# CREATE EVENT
# =========================================================

def create_calendar_event(
    title,
    start_time,
    end_time,
    description=None,
    meeting_link=None,
    timezone_name="UTC",
    user_id=None
):

    service = get_calendar_service(
        user_id=user_id
    )

    if not service:
        return None

    if (
        not title
        or not start_time
        or not end_time
    ):
        return None

    event_body = {

        "summary": title,

        "description": (
            description or ""
        ),

        "start": {

            "dateTime": start_time,

            "timeZone": timezone_name
        },

        "end": {

            "dateTime": end_time,

            "timeZone": timezone_name
        }
    }

    if meeting_link:

        event_body["description"] += (
            "\n\nMeeting link: "
            + meeting_link
        )

    try:

        return (
            service.events()
            .insert(
                calendarId="primary",

                body=event_body
            )
            .execute()
        )

    except Exception as error:

        print(
            "Calendar create error:",
            error
        )

        return None


# =========================================================
# SAVE MEETING
# =========================================================

def save_meeting(
    user_id,
    event_data,
    deal_id=None
):

    google_event_id = (
        event_data.get(
            "google_event_id"
        )
    )

    existing = None

    if google_event_id:

        existing = (
            Meeting.query.filter_by(
                user_id=user_id,

                google_event_id=(
                    google_event_id
                )
            )
            .first()
        )

    start_time = parse_datetime(
        event_data.get(
            "start_time"
        )
    )

    end_time = parse_datetime(
        event_data.get(
            "end_time"
        )
    )

    # -----------------------------------------------------
    # UPDATE EXISTING MEETING
    # -----------------------------------------------------

    if existing:

        existing.title = (
            event_data.get(
                "title"
            )
            or existing.title
        )

        existing.description = (
            event_data.get(
                "description"
            )
        )

        existing.start_time = (
            start_time
        )

        existing.end_time = (
            end_time
        )

        existing.meeting_link = (
            event_data.get(
                "meeting_link"
            )
        )

        if deal_id:

            existing.deal_id = (
                deal_id
            )

        db.session.commit()

        return existing


    # -----------------------------------------------------
    # CREATE NEW MEETING
    # -----------------------------------------------------

    meeting = Meeting(

        user_id=user_id,

        deal_id=deal_id,

        google_event_id=(
            google_event_id
        ),

        title=event_data.get(
            "title",
            "Untitled Meeting"
        ),

        description=event_data.get(
            "description"
        ),

        start_time=start_time,

        end_time=end_time,

        meeting_link=event_data.get(
            "meeting_link"
        )
    )

    db.session.add(
        meeting
    )

    db.session.commit()

    return meeting


# =========================================================
# SYNC CALENDAR
# =========================================================

def sync_calendar(
    user_id,
    max_results=20
):

    events = get_upcoming_events(
        max_results=max_results,
        user_id=user_id
    )

    synced = []

    for event in events:

        try:

            meeting = save_meeting(
                user_id=user_id,

                event_data=event
            )

            if meeting:

                synced.append(
                    meeting_to_dict(
                        meeting
                    )
                )

        except Exception as error:

            db.session.rollback()

            print(
                "Calendar sync error:",
                error
            )

    return synced


# =========================================================
# CREATE MEETING FROM AI
# =========================================================

def create_meeting_from_ai(
    user_id,
    meeting_data,
    deal_id=None
):

    if not meeting_data:
        return None

    if not meeting_data.get(
        "detected",
        False
    ):
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

    if (
        not title
        or not start_time
        or not end_time
    ):
        return None

    event = create_calendar_event(

        title=title,

        start_time=start_time,

        end_time=end_time,

        description=(
            meeting_data.get(
                "description"
            )
        ),

        meeting_link=(
            meeting_data.get(
                "meeting_link"
            )
        ),

        user_id=user_id
    )

    if not event:
        return None

    event_data = {

        "google_event_id": (
            event.get("id")
        ),

        "title": event.get(
            "summary",
            title
        ),

        "description": (
            event.get(
                "description"
            )
        ),

        "start_time": (
            event
            .get(
                "start",
                {}
            )
            .get("dateTime")
        ),

        "end_time": (
            event
            .get(
                "end",
                {}
            )
            .get("dateTime")
        ),

        "meeting_link": (
            get_meeting_link(
                event
            )
        )
    }

    return save_meeting(

        user_id=user_id,

        event_data=event_data,

        deal_id=deal_id
    )


# =========================================================
# GET SAVED MEETINGS
# =========================================================

def get_meetings(
    user_id
):

    meetings = (
        Meeting.query
        .filter_by(
            user_id=user_id
        )
        .order_by(
            Meeting.start_time.asc()
        )
        .all()
    )

    return [
        meeting_to_dict(
            meeting
        )
        for meeting in meetings
    ]


# =========================================================
# DELETE EVENT
# =========================================================

def delete_calendar_event(
    user_id,
    meeting_id
):

    meeting = (
        Meeting.query.filter_by(
            id=meeting_id,
            user_id=user_id
        )
        .first()
    )

    if not meeting:
        return False

    if meeting.google_event_id:

        service = (
            get_calendar_service(
                user_id=user_id
            )
        )

        if service:

            try:

                (
                    service.events()
                    .delete(
                        calendarId="primary",

                        eventId=(
                            meeting
                            .google_event_id
                        )
                    )
                    .execute()
                )

            except Exception as error:

                print(
                    "Calendar delete error:",
                    error
                )

                return False

    db.session.delete(
        meeting
    )

    db.session.commit()

    return True


# =========================================================
# GET MEETING LINK
# =========================================================

def get_meeting_link(
    event
):

    link = event.get(
        "hangoutLink"
    )

    if link:
        return link

    conference_data = event.get(
        "conferenceData",
        {}
    )

    entries = conference_data.get(
        "entryPoints",
        []
    )

    for entry in entries:

        if (
            entry.get(
                "entryPointType"
            )
            == "video"
        ):

            return entry.get(
                "uri"
            )

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

            parsed = (
                datetime.fromisoformat(
                    value.replace(
                        "Z",
                        "+00:00"
                    )
                )
            )

        except (
            ValueError,
            TypeError
        ):

            return None

    # Store naive UTC datetime in database

    if parsed.tzinfo:

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
# MEETING TO DICTIONARY
# =========================================================

def meeting_to_dict(
    meeting
):

    return {

        "id": meeting.id,

        "google_event_id": (
            meeting.google_event_id
        ),

        "title": meeting.title,

        "description": (
            meeting.description
        ),

        "start_time": (
            meeting.start_time.isoformat()
            if meeting.start_time
            else None
        ),

        "end_time": (
            meeting.end_time.isoformat()
            if meeting.end_time
            else None
        ),

        "meeting_link": (
            meeting.meeting_link
        ),

        "deal_id": (
            meeting.deal_id
        )
    }