from celery_config import celery

from app import app

from models import User

from inbox_service import (
    sync_inbox
)

from calendar_service import (
    sync_calendar
)

from drive_service import (
    sync_drive
)

from finance_service import (
    check_overdue_payments
)

from notification_service import (
    get_due_follow_ups
)


# =========================================================
# TEST WORKER
# =========================================================

@celery.task(
    name="manager_x.test_worker"
)
def test_worker():

    return {
        "status": "ok",
        "message": (
            "Manager X worker is running"
        )
    }


# =========================================================
# SYNC ONE USER INBOX
# =========================================================

@celery.task(
    name="manager_x.sync_user_inbox"
)
def sync_user_inbox(user_id):

    with app.app_context():

        try:

            emails = sync_inbox(
                user_id=user_id,
                max_results=20
            )

            return {
                "status": "success",
                "user_id": user_id,
                "emails_synced": len(emails)
            }

        except Exception as error:

            print(
                "Inbox worker error:",
                error
            )

            return {
                "status": "error",
                "user_id": user_id,
                "message": str(error)
            }


# =========================================================
# SYNC ONE USER CALENDAR
# =========================================================

@celery.task(
    name="manager_x.sync_user_calendar"
)
def sync_user_calendar(user_id):

    with app.app_context():

        try:

            meetings = sync_calendar(
                user_id=user_id,
                max_results=20
            )

            return {
                "status": "success",
                "user_id": user_id,
                "meetings_synced": (
                    len(meetings)
                )
            }

        except Exception as error:

            print(
                "Calendar worker error:",
                error
            )

            return {
                "status": "error",
                "user_id": user_id,
                "message": str(error)
            }


# =========================================================
# SYNC ONE USER DRIVE
# =========================================================

@celery.task(
    name="manager_x.sync_user_drive"
)
def sync_user_drive(user_id):

    with app.app_context():

        try:

            files = sync_drive(
                user_id=user_id,
                max_results=50
            )

            return {
                "status": "success",
                "user_id": user_id,
                "files_synced": len(files)
            }

        except Exception as error:

            print(
                "Drive worker error:",
                error
            )

            return {
                "status": "error",
                "user_id": user_id,
                "message": str(error)
            }


# =========================================================
# CHECK ONE USER PAYMENTS
# =========================================================

@celery.task(
    name="manager_x.check_user_payments"
)
def check_user_payments(user_id):

    with app.app_context():

        try:

            payments = (
                check_overdue_payments(
                    user_id
                )
            )

            return {
                "status": "success",
                "user_id": user_id,
                "overdue_payments": (
                    len(payments)
                )
            }

        except Exception as error:

            print(
                "Payment worker error:",
                error
            )

            return {
                "status": "error",
                "user_id": user_id,
                "message": str(error)
            }


# =========================================================
# CHECK ONE USER FOLLOW UPS
# =========================================================

@celery.task(
    name="manager_x.check_user_followups"
)
def check_user_followups(user_id):

    with app.app_context():

        try:

            follow_ups = (
                get_due_follow_ups(
                    user_id
                )
            )

            return {
                "status": "success",
                "user_id": user_id,
                "due_follow_ups": (
                    len(follow_ups)
                )
            }

        except Exception as error:

            print(
                "Follow-up worker error:",
                error
            )

            return {
                "status": "error",
                "user_id": user_id,
                "message": str(error)
            }


# =========================================================
# RUN COMPLETE MANAGER FOR ONE USER
# =========================================================

@celery.task(
    name="manager_x.run_user_manager"
)
def run_user_manager(user_id):

    with app.app_context():

        result = {
            "status": "success",
            "user_id": user_id,

            "emails_synced": 0,
            "meetings_synced": 0,
            "files_synced": 0,

            "overdue_payments": 0,
            "due_follow_ups": 0,

            "errors": []
        }


        # -------------------------------------------------
        # INBOX
        # -------------------------------------------------

        try:

            emails = sync_inbox(
                user_id=user_id,
                max_results=20
            )

            result[
                "emails_synced"
            ] = len(emails)

        except Exception as error:

            result["errors"].append(
                "Inbox: "
                + str(error)
            )


        # -------------------------------------------------
        # CALENDAR
        # -------------------------------------------------

        try:

            meetings = sync_calendar(
                user_id=user_id,
                max_results=20
            )

            result[
                "meetings_synced"
            ] = len(meetings)

        except Exception as error:

            result["errors"].append(
                "Calendar: "
                + str(error)
            )


        # -------------------------------------------------
        # DRIVE
        # -------------------------------------------------

        try:

            files = sync_drive(
                user_id=user_id,
                max_results=50
            )

            result[
                "files_synced"
            ] = len(files)

        except Exception as error:

            result["errors"].append(
                "Drive: "
                + str(error)
            )


        # -------------------------------------------------
        # PAYMENTS
        # -------------------------------------------------

        try:

            payments = (
                check_overdue_payments(
                    user_id
                )
            )

            result[
                "overdue_payments"
            ] = len(payments)

        except Exception as error:

            result["errors"].append(
                "Payments: "
                + str(error)
            )


        # -------------------------------------------------
        # FOLLOW UPS
        # -------------------------------------------------

        try:

            follow_ups = (
                get_due_follow_ups(
                    user_id
                )
            )

            result[
                "due_follow_ups"
            ] = len(follow_ups)

        except Exception as error:

            result["errors"].append(
                "Follow-ups: "
                + str(error)
            )


        # -------------------------------------------------
        # FINAL STATUS
        # -------------------------------------------------

        if result["errors"]:

            result["status"] = (
                "partial_success"
            )

        return result


# =========================================================
# RUN MANAGER FOR ALL USERS
# =========================================================

@celery.task(
    name="manager_x.run_all_managers"
)
def run_all_managers():

    with app.app_context():

        try:

            users = User.query.all()

            started = 0
            skipped = 0


            for user in users:

                # Google connection required
                if not (
                    user.google_access_token
                    or user.google_refresh_token
                ):

                    skipped += 1
                    continue


                # -----------------------------------------
                # SEND USER JOB TO CELERY
                # -----------------------------------------

                run_user_manager.delay(
                    user.id
                )

                started += 1


            return {
                "status": "success",

                "users_found": (
                    len(users)
                ),

                "manager_jobs_started": (
                    started
                ),

                "users_skipped": (
                    skipped
                )
            }

        except Exception as error:

            print(
                "All managers worker error:",
                error
            )

            return {
                "status": "error",
                "message": str(error)
            }