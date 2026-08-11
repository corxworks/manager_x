from flask import session, current_app

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from database import db
from models import User, DriveFile


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
# GET GOOGLE CREDENTIALS
# =========================================================

def get_google_credentials(user_id=None):

    user = get_current_user(
        user_id=user_id
    )

    if not user:
        return None

    if not user.google_access_token:
        return None

    # IMPORTANT:
    # Database stores token expiry as naive UTC datetime.
    # Keep it naive here as well.

    expiry = user.google_token_expiry

    credentials = Credentials(

        token=(
            user.google_access_token
        ),

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


    # =====================================================
    # REFRESH EXPIRED TOKEN
    # =====================================================

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

                # Google may return timezone-aware
                # datetime. Store it as naive UTC.

                if new_expiry.tzinfo:

                    new_expiry = (
                        new_expiry
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
# GOOGLE DRIVE SERVICE
# =========================================================

def get_drive_service(user_id=None):

    credentials = (
        get_google_credentials(
            user_id=user_id
        )
    )

    if not credentials:
        return None

    try:

        return build(
            "drive",
            "v3",
            credentials=credentials
        )

    except Exception as error:

        print(
            "Drive service error:",
            error
        )

        return None


# =========================================================
# GET DRIVE FILES
# =========================================================

def get_drive_files(
    max_results=50,
    user_id=None
):

    service = get_drive_service(
        user_id=user_id
    )

    if not service:
        return []

    try:

        response = (
            service.files()
            .list(

                pageSize=max_results,

                fields=(
                    "files("
                    "id,"
                    "name,"
                    "mimeType,"
                    "webViewLink,"
                    "createdTime,"
                    "modifiedTime"
                    ")"
                ),

                orderBy=(
                    "modifiedTime desc"
                ),

                q="trashed = false"
            )
            .execute()
        )


        files = response.get(
            "files",
            []
        )


        results = []


        for file_data in files:

            results.append({

                "google_file_id": (
                    file_data.get(
                        "id"
                    )
                ),

                "name": (
                    file_data.get(
                        "name"
                    )
                ),

                "file_type": (
                    file_data.get(
                        "mimeType"
                    )
                ),

                "drive_url": (
                    file_data.get(
                        "webViewLink"
                    )
                ),

                "created_time": (
                    file_data.get(
                        "createdTime"
                    )
                ),

                "modified_time": (
                    file_data.get(
                        "modifiedTime"
                    )
                )

            })


        return results


    except Exception as error:

        print(
            "Drive fetch error:",
            error
        )

        return []


# =========================================================
# DETECT FILE CATEGORY
# =========================================================

def detect_file_category(
    file_name
):

    if not file_name:
        return "other"


    name = file_name.lower()


    # Contract

    if (
        "contract" in name
        or "agreement" in name
    ):

        return "contract"


    # Invoice

    if (
        "invoice" in name
        or "bill" in name
    ):

        return "invoice"


    # Media Kit

    if (
        "media kit" in name
        or "mediakit" in name
    ):

        return "media_kit"


    # Sponsor assets

    if (
        "sponsor" in name
        or "campaign" in name
        or "brand asset" in name
        or "creative asset" in name
    ):

        return "sponsor_asset"


    return "other"


# =========================================================
# SAVE DRIVE FILE
# =========================================================

def save_drive_file(
    user_id,
    file_data,
    deal_id=None
):

    google_file_id = (
        file_data.get(
            "google_file_id"
        )
    )


    if not google_file_id:
        return None


    # -----------------------------------------------------
    # CHECK EXISTING FILE
    # -----------------------------------------------------

    existing_file = (
        DriveFile.query.filter_by(

            user_id=user_id,

            google_file_id=(
                google_file_id
            )

        )
        .first()
    )


    # -----------------------------------------------------
    # UPDATE EXISTING FILE
    # -----------------------------------------------------

    if existing_file:

        if file_data.get("name"):

            existing_file.name = (
                file_data.get(
                    "name"
                )
            )


        if file_data.get(
            "file_type"
        ):

            existing_file.file_type = (
                file_data.get(
                    "file_type"
                )
            )


        if file_data.get(
            "drive_url"
        ):

            existing_file.drive_url = (
                file_data.get(
                    "drive_url"
                )
            )


        existing_file.category = (
            detect_file_category(
                existing_file.name
            )
        )


        if deal_id is not None:

            existing_file.deal_id = (
                deal_id
            )


        db.session.commit()


        return existing_file


    # -----------------------------------------------------
    # CREATE NEW FILE
    # -----------------------------------------------------

    file_name = (
        file_data.get(
            "name"
        )
        or "Untitled File"
    )


    drive_file = DriveFile(

        user_id=user_id,

        deal_id=deal_id,

        google_file_id=(
            google_file_id
        ),

        name=file_name,

        file_type=(
            file_data.get(
                "file_type"
            )
        ),

        category=(
            detect_file_category(
                file_name
            )
        ),

        drive_url=(
            file_data.get(
                "drive_url"
            )
        )

    )


    db.session.add(
        drive_file
    )

    db.session.commit()


    return drive_file


# =========================================================
# SYNC GOOGLE DRIVE
# =========================================================

def sync_drive(
    user_id,
    max_results=50
):

    files = get_drive_files(

        max_results=max_results,

        user_id=user_id

    )


    synced_files = []


    for file_data in files:

        try:

            drive_file = (
                save_drive_file(

                    user_id=user_id,

                    file_data=file_data

                )
            )


            if drive_file:

                synced_files.append(

                    drive_file_to_dict(
                        drive_file
                    )

                )


        except Exception as error:

            db.session.rollback()

            print(
                "Drive sync error:",
                error
            )


    return synced_files


# =========================================================
# GET SAVED FILES
# =========================================================

def get_saved_files(
    user_id,
    category=None,
    deal_id=None
):

    query = (
        DriveFile.query
        .filter_by(
            user_id=user_id
        )
    )


    if category:

        query = query.filter_by(
            category=category
        )


    if deal_id is not None:

        query = query.filter_by(
            deal_id=deal_id
        )


    files = (
        query
        .order_by(
            DriveFile.created_at.desc()
        )
        .all()
    )


    return [

        drive_file_to_dict(
            file
        )

        for file in files

    ]


# =========================================================
# GET ONE SAVED FILE
# =========================================================

def get_saved_file(
    user_id,
    file_id
):

    file = (
        DriveFile.query.filter_by(

            id=file_id,

            user_id=user_id

        )
        .first()
    )


    if not file:
        return None


    return drive_file_to_dict(
        file
    )


# =========================================================
# ATTACH FILE TO DEAL
# =========================================================

def attach_file_to_deal(
    user_id,
    file_id,
    deal_id
):

    file = (
        DriveFile.query.filter_by(

            id=file_id,

            user_id=user_id

        )
        .first()
    )


    if not file:
        return None


    file.deal_id = deal_id


    db.session.commit()


    return drive_file_to_dict(
        file
    )


# =========================================================
# REMOVE FILE FROM DEAL
# =========================================================

def remove_file_from_deal(
    user_id,
    file_id
):

    file = (
        DriveFile.query.filter_by(

            id=file_id,

            user_id=user_id

        )
        .first()
    )


    if not file:
        return None


    file.deal_id = None


    db.session.commit()


    return drive_file_to_dict(
        file
    )


# =========================================================
# UPDATE FILE CATEGORY
# =========================================================

def update_file_category(
    user_id,
    file_id,
    category
):

    allowed_categories = [

        "contract",

        "invoice",

        "media_kit",

        "sponsor_asset",

        "other"

    ]


    if category not in allowed_categories:

        return None


    file = (
        DriveFile.query.filter_by(

            id=file_id,

            user_id=user_id

        )
        .first()
    )


    if not file:
        return None


    file.category = category


    db.session.commit()


    return drive_file_to_dict(
        file
    )


# =========================================================
# DRIVE FILE TO DICTIONARY
# =========================================================

def drive_file_to_dict(
    file
):

    return {

        "id": file.id,

        "google_file_id": (
            file.google_file_id
        ),

        "name": file.name,

        "file_type": (
            file.file_type
        ),

        "category": (
            file.category
        ),

        "drive_url": (
            file.drive_url
        ),

        "deal_id": (
            file.deal_id
        ),

        "created_at": (

            file.created_at.isoformat()

            if file.created_at

            else None

        )

    }