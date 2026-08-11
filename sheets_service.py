from datetime import timezone

from flask import session, current_app

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from database import db
from models import User


# =========================================================
# GET CURRENT USER
# =========================================================

def get_current_user():

    user_id = session.get("user_id")

    if not user_id:
        return None

    return db.session.get(
        User,
        user_id
    )


# =========================================================
# GET GOOGLE CREDENTIALS
# =========================================================

def get_google_credentials():

    user = get_current_user()

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

        client_id=current_app.config.get(
            "GOOGLE_CLIENT_ID"
        ),

        client_secret=current_app.config.get(
            "GOOGLE_CLIENT_SECRET"
        ),

        expiry=expiry
    )


    # -----------------------------------------------------
    # REFRESH EXPIRED TOKEN
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

                refreshed_expiry = (
                    credentials.expiry
                )

                if refreshed_expiry.tzinfo:

                    refreshed_expiry = (
                        refreshed_expiry
                        .astimezone(
                            timezone.utc
                        )
                        .replace(
                            tzinfo=None
                        )
                    )

                user.google_token_expiry = (
                    refreshed_expiry
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
# GOOGLE SHEETS SERVICE
# =========================================================

def get_sheets_service():

    credentials = get_google_credentials()

    if not credentials:
        return None

    return build(
        "sheets",
        "v4",
        credentials=credentials
    )


# =========================================================
# READ SHEET
# =========================================================

def read_sheet(
    spreadsheet_id,
    range_name
):

    service = get_sheets_service()

    if not service:
        return []

    try:

        result = (
            service.spreadsheets()
            .values()
            .get(
                spreadsheetId=(
                    spreadsheet_id
                ),

                range=range_name
            )
            .execute()
        )

        return result.get(
            "values",
            []
        )

    except Exception as error:

        print(
            "Google Sheets read error:",
            error
        )

        return []


# =========================================================
# APPEND ROW
# =========================================================

def append_row(
    spreadsheet_id,
    range_name,
    values
):

    service = get_sheets_service()

    if not service:
        return False

    if not values:
        return False

    try:

        body = {
            "values": [
                values
            ]
        }

        (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=(
                    spreadsheet_id
                ),

                range=range_name,

                valueInputOption=(
                    "USER_ENTERED"
                ),

                insertDataOption=(
                    "INSERT_ROWS"
                ),

                body=body
            )
            .execute()
        )

        return True

    except Exception as error:

        print(
            "Google Sheets append error:",
            error
        )

        return False


# =========================================================
# UPDATE SHEET RANGE
# =========================================================

def update_sheet(
    spreadsheet_id,
    range_name,
    values
):

    service = get_sheets_service()

    if not service:
        return False

    if not values:
        return False

    try:

        body = {
            "values": values
        }

        (
            service.spreadsheets()
            .values()
            .update(
                spreadsheetId=(
                    spreadsheet_id
                ),

                range=range_name,

                valueInputOption=(
                    "USER_ENTERED"
                ),

                body=body
            )
            .execute()
        )

        return True

    except Exception as error:

        print(
            "Google Sheets update error:",
            error
        )

        return False


# =========================================================
# CLEAR RANGE
# =========================================================

def clear_sheet_range(
    spreadsheet_id,
    range_name
):

    service = get_sheets_service()

    if not service:
        return False

    try:

        (
            service.spreadsheets()
            .values()
            .clear(
                spreadsheetId=(
                    spreadsheet_id
                ),

                range=range_name,

                body={}
            )
            .execute()
        )

        return True

    except Exception as error:

        print(
            "Google Sheets clear error:",
            error
        )

        return False


# =========================================================
# CREATE SPREADSHEET
# =========================================================

def create_spreadsheet(
    title
):

    service = get_sheets_service()

    if not service:
        return None

    if not title:
        return None

    try:

        spreadsheet = (
            service.spreadsheets()
            .create(
                body={
                    "properties": {
                        "title": title
                    }
                }
            )
            .execute()
        )

        return {
            "spreadsheet_id": (
                spreadsheet.get(
                    "spreadsheetId"
                )
            ),

            "url": (
                spreadsheet.get(
                    "spreadsheetUrl"
                )
            ),

            "title": (
                spreadsheet
                .get(
                    "properties",
                    {}
                )
                .get("title")
            )
        }

    except Exception as error:

        print(
            "Google Sheets creation error:",
            error
        )

        return None


# =========================================================
# EXPORT DEALS TO SHEET
# =========================================================

def export_deals_to_sheet(
    spreadsheet_id,
    deals
):

    if not deals:
        return False

    rows = [
        [
            "Company",
            "Contact",
            "Email",
            "Deal Value",
            "Currency",
            "Status",
            "Next Follow Up"
        ]
    ]

    for deal in deals:

        rows.append([
            deal.get(
                "company",
                ""
            ),

            deal.get(
                "contact_name",
                ""
            ),

            deal.get(
                "contact_email",
                ""
            ),

            deal.get(
                "deal_value",
                ""
            ),

            deal.get(
                "currency",
                ""
            ),

            deal.get(
                "status",
                ""
            ),

            deal.get(
                "next_follow_up",
                ""
            )
        ])

    return update_sheet(
        spreadsheet_id=(
            spreadsheet_id
        ),

        range_name=(
            "Sheet1!A1:G"
        ),

        values=rows
    )


# =========================================================
# EXPORT PAYMENTS TO SHEET
# =========================================================

def export_payments_to_sheet(
    spreadsheet_id,
    payments
):

    if not payments:
        return False

    rows = [
        [
            "Amount",
            "Currency",
            "Status",
            "Invoice",
            "Due Date",
            "Paid At"
        ]
    ]

    for payment in payments:

        rows.append([
            payment.get(
                "amount",
                ""
            ),

            payment.get(
                "currency",
                ""
            ),

            payment.get(
                "status",
                ""
            ),

            payment.get(
                "invoice_number",
                ""
            ),

            payment.get(
                "due_date",
                ""
            ),

            payment.get(
                "paid_at",
                ""
            )
        ])

    return update_sheet(
        spreadsheet_id=(
            spreadsheet_id
        ),

        range_name=(
            "Sheet1!A1:F"
        ),

        values=rows
    )