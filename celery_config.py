from celery import Celery
from celery.schedules import crontab

from config import Config


# =========================================================
# CREATE CELERY
# =========================================================

def create_celery():

    celery = Celery(
        "manager_x",

        broker=Config.REDIS_URL,

        backend=Config.REDIS_URL,

        include=[
            "worker"
        ]
    )


    # =====================================================
    # CELERY SETTINGS
    # =====================================================

    celery.conf.update(

        # -------------------------------------------------
        # TASK FORMAT
        # -------------------------------------------------

        task_serializer="json",

        result_serializer="json",

        accept_content=[
            "json"
        ],


        # -------------------------------------------------
        # TIMEZONE
        # -------------------------------------------------

        timezone="UTC",

        enable_utc=True,


        # -------------------------------------------------
        # TASK SETTINGS
        # -------------------------------------------------

        task_track_started=True,

        task_acks_late=True,

        worker_prefetch_multiplier=1,


        # -------------------------------------------------
        # RESULT SETTINGS
        # -------------------------------------------------

        result_expires=3600,


        # -------------------------------------------------
        # CONNECTION SETTINGS
        # -------------------------------------------------

        broker_connection_retry_on_startup=True
    )


    # =====================================================
    # AUTOMATIC SCHEDULE
    # =====================================================

    celery.conf.beat_schedule = {


        # -------------------------------------------------
        # COMPLETE MANAGER SYNC
        #
        # Gmail
        # Calendar
        # Drive
        # Payments
        # Follow-ups
        #
        # Runs every 15 minutes
        # -------------------------------------------------

        "run-manager-every-15-minutes": {

            "task": (
                "manager_x.run_all_managers"
            ),

            "schedule": 15 * 60
        },


        # -------------------------------------------------
        # PAYMENT CHECK
        #
        # Runs every day
        # 01:00 UTC
        # -------------------------------------------------

        "daily-payment-check": {

            "task": (
                "manager_x.check_all_payments"
            ),

            "schedule": crontab(
                hour=1,
                minute=0
            )
        },


        # -------------------------------------------------
        # FOLLOW-UP CHECK
        #
        # Runs every hour
        # -------------------------------------------------

        "hourly-followup-check": {

            "task": (
                "manager_x.check_all_followups"
            ),

            "schedule": crontab(
                minute=0
            )
        }
    }


    return celery


# =========================================================
# CELERY INSTANCE
# =========================================================

celery = create_celery()