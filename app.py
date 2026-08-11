import os

# =========================================================
# LOCAL OAUTH DEVELOPMENT
# =========================================================

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


from flask import (
    Flask,
    jsonify,
    request,
    session
)

from flask_cors import CORS

from config import Config
from database import db

from auth import auth_bp

from inbox_service import (
    sync_inbox,
    get_inbox,
    get_email,
    mark_email_read
)

from calendar_service import (
    sync_calendar,
    get_meetings
)

from drive_service import (
    sync_drive,
    get_saved_files
)

from sheets_service import (
    read_sheet,
    append_row,
    create_spreadsheet
)

from crm_service import (
    get_deals,
    get_deal,
    create_deal,
    update_deal_status,
    update_deal_value,
    update_deal_notes,
    set_next_follow_up,
    delete_deal,
    deal_to_dict
)

from task_service import (
    get_tasks,
    get_task,
    create_task,
    update_task_status,
    update_task,
    delete_task,
    task_to_dict
)

from finance_service import (
    get_payments,
    get_payment,
    create_payment,
    mark_payment_paid,
    update_payment_status,
    update_invoice,
    check_overdue_payments,
    get_finance_summary,
    delete_payment,
    payment_to_dict
)


# =========================================================
# CREATE APP
# =========================================================

app = Flask(__name__)

app.config.from_object(Config)


# =========================================================
# CORS
# =========================================================

CORS(
    app,
    supports_credentials=True,
    origins=[
        app.config.get(
            "FRONTEND_URL",
            "http://localhost:3000"
        )
    ]
)


# =========================================================
# DATABASE
# =========================================================

db.init_app(app)

with app.app_context():
    db.create_all()


# =========================================================
# AUTH
# =========================================================

app.register_blueprint(auth_bp)


# =========================================================
# HEALTH
# =========================================================

@app.route(
    "/api/health",
    methods=["GET"]
)
def health():

    return jsonify({
        "status": "ok",
        "service": "Manager X"
    }), 200


# =========================================================
# CURRENT USER
# =========================================================

@app.route(
    "/api/me",
    methods=["GET"]
)
def me():

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "authenticated": False
        }), 401

    return jsonify({
        "authenticated": True,
        "user_id": user_id
    }), 200


# =========================================================
# DASHBOARD
# =========================================================

@app.route(
    "/api/dashboard",
    methods=["GET"]
)
def dashboard():

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "authenticated": False
        }), 401

    return jsonify({
        "authenticated": True,
        "message": "Manager X API is running"
    }), 200


# =========================================================
# INBOX
# =========================================================

@app.route(
    "/api/inbox",
    methods=["GET"]
)
def inbox():

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "error": "Authentication required"
        }), 401

    category = request.args.get(
        "category"
    )

    priority = request.args.get(
        "priority"
    )

    try:

        sync_inbox(
            user_id=user_id,
            max_results=20
        )

    except Exception as error:

        print(
            "Inbox sync failed:",
            error
        )

    emails = get_inbox(
        user_id=user_id,
        category=category,
        priority=priority,
        limit=50
    )

    return jsonify({
        "emails": emails
    }), 200


# =========================================================
# GET ONE EMAIL
# =========================================================

@app.route(
    "/api/inbox/<int:email_id>",
    methods=["GET"]
)
def inbox_email(
    email_id
):

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "error": "Authentication required"
        }), 401

    email = get_email(
        user_id=user_id,
        email_id=email_id
    )

    if not email:

        return jsonify({
            "error": "Email not found"
        }), 404

    return jsonify(
        email
    ), 200


# =========================================================
# MARK EMAIL READ
# =========================================================

@app.route(
    "/api/inbox/<int:email_id>/read",
    methods=["PATCH"]
)
def read_email(
    email_id
):

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "error": "Authentication required"
        }), 401

    email = mark_email_read(
        user_id=user_id,
        email_id=email_id
    )

    if not email:

        return jsonify({
            "error": "Email not found"
        }), 404

    return jsonify(
        email
    ), 200


# =========================================================
# MANUAL INBOX SYNC
# =========================================================

@app.route(
    "/api/inbox/sync",
    methods=["POST"]
)
def manual_inbox_sync():

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "error": "Authentication required"
        }), 401

    try:

        emails = sync_inbox(
            user_id=user_id,
            max_results=20
        )

        return jsonify({
            "success": True,
            "count": len(emails),
            "emails": emails
        }), 200

    except Exception as error:

        print(
            "Manual inbox sync error:",
            error
        )

        return jsonify({
            "success": False,
            "error": "Could not sync inbox"
        }), 500


# =========================================================
# CALENDAR
# =========================================================

@app.route(
    "/api/calendar",
    methods=["GET"]
)
def calendar():

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "error": "Authentication required"
        }), 401

    try:

        sync_calendar(
            user_id=user_id,
            max_results=20
        )

        meetings = get_meetings(
            user_id=user_id
        )

        return jsonify({
            "meetings": meetings
        }), 200

    except Exception as error:

        print(
            "Calendar API error:",
            error
        )

        return jsonify({
            "error": "Could not load calendar"
        }), 500


# =========================================================
# DRIVE
# =========================================================

@app.route(
    "/api/drive",
    methods=["GET"]
)
def drive():

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "error": "Authentication required"
        }), 401

    category = request.args.get(
        "category"
    )

    try:

        sync_drive(
            user_id=user_id,
            max_results=50
        )

        files = get_saved_files(
            user_id=user_id,
            category=category
        )

        return jsonify({
            "files": files
        }), 200

    except Exception as error:

        print(
            "Drive API error:",
            error
        )

        return jsonify({
            "error": "Could not load Drive files"
        }), 500


# =========================================================
# SHEETS - READ
# =========================================================

@app.route(
    "/api/sheets/read",
    methods=["GET"]
)
def sheets_read():

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "error": "Authentication required"
        }), 401

    spreadsheet_id = request.args.get(
        "spreadsheet_id"
    )

    range_name = request.args.get(
        "range",
        "Sheet1!A1:G20"
    )

    if not spreadsheet_id:

        return jsonify({
            "error": "Spreadsheet ID is required"
        }), 400

    try:

        rows = read_sheet(
            spreadsheet_id=spreadsheet_id,
            range_name=range_name
        )

        return jsonify({
            "rows": rows
        }), 200

    except Exception as error:

        print(
            "Sheets read API error:",
            error
        )

        return jsonify({
            "error": "Could not read spreadsheet"
        }), 500


# =========================================================
# SHEETS - CREATE
# =========================================================

@app.route(
    "/api/sheets/create",
    methods=["POST"]
)
def sheets_create():

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "error": "Authentication required"
        }), 401

    data = request.get_json(
        silent=True
    ) or {}

    title = data.get(
        "title"
    )

    if not title:

        return jsonify({
            "error": "Spreadsheet title is required"
        }), 400

    try:

        spreadsheet = create_spreadsheet(
            title=title
        )

        if not spreadsheet:

            return jsonify({
                "error": "Could not create spreadsheet"
            }), 500

        return jsonify(
            spreadsheet
        ), 200

    except Exception as error:

        print(
            "Sheets create API error:",
            error
        )

        return jsonify({
            "error": "Could not create spreadsheet"
        }), 500


# =========================================================
# SHEETS - APPEND
# =========================================================

@app.route(
    "/api/sheets/append",
    methods=["POST"]
)
def sheets_append():

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "error": "Authentication required"
        }), 401

    data = request.get_json(
        silent=True
    ) or {}

    spreadsheet_id = data.get(
        "spreadsheet_id"
    )

    range_name = data.get(
        "range",
        "Sheet1!A1"
    )

    values = data.get(
        "values"
    )

    if not spreadsheet_id:

        return jsonify({
            "error": "Spreadsheet ID is required"
        }), 400

    if not values:

        return jsonify({
            "error": "Values are required"
        }), 400

    try:

        success = append_row(
            spreadsheet_id=spreadsheet_id,
            range_name=range_name,
            values=values
        )

        if not success:

            return jsonify({
                "error": "Could not append row"
            }), 500

        return jsonify({
            "success": True,
            "message": "Row added successfully"
        }), 200

    except Exception as error:

        print(
            "Sheets append API error:",
            error
        )

        return jsonify({
            "error": "Could not append row"
        }), 500


# =========================================================
# CRM - GET ALL
# =========================================================

@app.route(
    "/api/deals",
    methods=["GET"]
)
def deals():

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "error": "Authentication required"
        }), 401

    try:

        deals_list = get_deals(
            user_id=user_id
        )

        return jsonify({
            "deals": deals_list
        }), 200

    except Exception as error:

        print(
            "CRM get deals error:",
            error
        )

        return jsonify({
            "error": "Could not load deals"
        }), 500


# =========================================================
# CRM - GET ONE
# =========================================================

@app.route(
    "/api/deals/<int:deal_id>",
    methods=["GET"]
)
def get_one_deal(
    deal_id
):

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "error": "Authentication required"
        }), 401

    deal = get_deal(
        user_id=user_id,
        deal_id=deal_id
    )

    if not deal:

        return jsonify({
            "error": "Deal not found"
        }), 404

    return jsonify(
        deal
    ), 200


# =========================================================
# CRM - CREATE
# =========================================================

@app.route(
    "/api/deals",
    methods=["POST"]
)
def create_new_deal():

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "error": "Authentication required"
        }), 401

    data = request.get_json(
        silent=True
    ) or {}

    company = data.get(
        "company"
    )

    if not company:

        return jsonify({
            "error": "Company is required"
        }), 400

    try:

        deal = create_deal(

            user_id=user_id,

            company=company,

            contact_name=
                data.get("contact_name"),

            contact_email=
                data.get("contact_email"),

            deal_value=
                data.get("deal_value"),

            currency=(
                data.get("currency")
                or "USD"
            ),

            status=(
                data.get("status")
                or "new"
            ),

            notes=
                data.get("notes")
        )

        if not deal:

            return jsonify({
                "error": "Could not create deal"
            }), 400

        return jsonify(
            deal_to_dict(deal)
        ), 201

    except Exception as error:

        db.session.rollback()

        print(
            "CRM create deal error:",
            error
        )

        return jsonify({
            "error": "Could not create deal"
        }), 500


# =========================================================
# CRM - UPDATE STATUS
# =========================================================

@app.route(
    "/api/deals/<int:deal_id>/status",
    methods=["PATCH"]
)
def change_deal_status(
    deal_id
):

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "error": "Authentication required"
        }), 401

    data = request.get_json(
        silent=True
    ) or {}

    status = data.get(
        "status"
    )

    if not status:

        return jsonify({
            "error": "Status is required"
        }), 400

    deal = update_deal_status(
        user_id=user_id,
        deal_id=deal_id,
        status=status
    )

    if not deal:

        return jsonify({
            "error":
                "Deal not found or invalid status"
        }), 400

    return jsonify(
        deal
    ), 200


# =========================================================
# CRM - UPDATE VALUE
# =========================================================

@app.route(
    "/api/deals/<int:deal_id>/value",
    methods=["PATCH"]
)
def change_deal_value(
    deal_id
):

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "error": "Authentication required"
        }), 401

    data = request.get_json(
        silent=True
    ) or {}

    if "deal_value" not in data:

        return jsonify({
            "error": "Deal value is required"
        }), 400

    deal = update_deal_value(

        user_id=user_id,

        deal_id=deal_id,

        deal_value=
            data.get("deal_value"),

        currency=
            data.get("currency")
    )

    if not deal:

        return jsonify({
            "error": "Deal not found"
        }), 404

    return jsonify(
        deal
    ), 200


# =========================================================
# CRM - UPDATE NOTES
# =========================================================

@app.route(
    "/api/deals/<int:deal_id>/notes",
    methods=["PATCH"]
)
def change_deal_notes(
    deal_id
):

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "error": "Authentication required"
        }), 401

    data = request.get_json(
        silent=True
    ) or {}

    notes = data.get(
        "notes",
        ""
    )

    deal = update_deal_notes(

        user_id=user_id,

        deal_id=deal_id,

        notes=notes
    )

    if not deal:

        return jsonify({
            "error": "Deal not found"
        }), 404

    return jsonify(
        deal
    ), 200


# =========================================================
# CRM - FOLLOW UP
# =========================================================

@app.route(
    "/api/deals/<int:deal_id>/follow-up",
    methods=["PATCH"]
)
def change_deal_follow_up(
    deal_id
):

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "error": "Authentication required"
        }), 401

    data = request.get_json(
        silent=True
    ) or {}

    follow_up_time = data.get(
        "follow_up_at"
    )

    if not follow_up_time:

        return jsonify({
            "error":
                "follow_up_at is required"
        }), 400

    try:

        from datetime import datetime

        follow_up_time = datetime.fromisoformat(
            follow_up_time.replace(
                "Z",
                ""
            )
        )

    except Exception:

        return jsonify({
            "error":
                "Invalid follow-up date"
        }), 400

    deal = set_next_follow_up(

        user_id=user_id,

        deal_id=deal_id,

        follow_up_time=
            follow_up_time
    )

    if not deal:

        return jsonify({
            "error": "Deal not found"
        }), 404

    return jsonify(
        deal
    ), 200


# =========================================================
# CRM - DELETE
# =========================================================

@app.route(
    "/api/deals/<int:deal_id>",
    methods=["DELETE"]
)
def remove_deal(
    deal_id
):

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "error": "Authentication required"
        }), 401

    success = delete_deal(
        user_id=user_id,
        deal_id=deal_id
    )

    if not success:

        return jsonify({
            "error": "Deal not found"
        }), 404

    return jsonify({
        "success": True,
        "message": "Deal deleted"
    }), 200


# =========================================================
# TASKS - GET
# =========================================================

@app.route(
    "/api/tasks",
    methods=["GET"]
)
def tasks():

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "error": "Authentication required"
        }), 401

    status = request.args.get(
        "status"
    )

    try:

        task_list = get_tasks(
            user_id=user_id,
            status=status
        )

        return jsonify({
            "tasks": task_list
        }), 200

    except Exception as error:

        print(
            "Tasks get error:",
            error
        )

        return jsonify({
            "error": "Could not load tasks"
        }), 500


# =========================================================
# TASKS - GET ONE
# =========================================================

@app.route(
    "/api/tasks/<int:task_id>",
    methods=["GET"]
)
def get_one_task(
    task_id
):

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "error": "Authentication required"
        }), 401

    task = get_task(
        user_id=user_id,
        task_id=task_id
    )

    if not task:

        return jsonify({
            "error": "Task not found"
        }), 404

    return jsonify(
        task
    ), 200


# =========================================================
# TASKS - CREATE
# =========================================================

@app.route(
    "/api/tasks",
    methods=["POST"]
)
def create_new_task():

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "error": "Authentication required"
        }), 401

    data = request.get_json(
        silent=True
    ) or {}

    title = data.get(
        "title"
    )

    if not title:

        return jsonify({
            "error":
                "Task title is required"
        }), 400

    try:

        task = create_task(

            user_id=user_id,

            title=title,

            description=
                data.get("description"),

            priority=(
                data.get("priority")
                or "medium"
            ),

            deadline=
                data.get("deadline"),

            deal_id=
                data.get("deal_id"),

            email_id=
                data.get("email_id")
        )

        if not task:

            return jsonify({
                "error":
                    "Could not create task"
            }), 400

        return jsonify(
            task_to_dict(task)
        ), 201

    except Exception as error:

        db.session.rollback()

        print(
            "Task create error:",
            error
        )

        return jsonify({
            "error":
                "Could not create task"
        }), 500


# =========================================================
# TASKS - COMPLETE
# =========================================================

@app.route(
    "/api/tasks/<int:task_id>/complete",
    methods=["PATCH"]
)
def complete_task(
    task_id
):

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "error": "Authentication required"
        }), 401

    task = update_task_status(

        user_id=user_id,

        task_id=task_id,

        status="completed"
    )

    if not task:

        return jsonify({
            "error": "Task not found"
        }), 404

    return jsonify(
        task
    ), 200


# =========================================================
# TASKS - STATUS
# =========================================================

@app.route(
    "/api/tasks/<int:task_id>/status",
    methods=["PATCH"]
)
def change_task_status(
    task_id
):

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "error":
                "Authentication required"
        }), 401

    data = request.get_json(
        silent=True
    ) or {}

    status = data.get(
        "status"
    )

    if not status:

        return jsonify({
            "error":
                "Status is required"
        }), 400

    task = update_task_status(

        user_id=user_id,

        task_id=task_id,

        status=status
    )

    if not task:

        return jsonify({
            "error":
                "Task not found or invalid status"
        }), 400

    return jsonify(
        task
    ), 200


# =========================================================
# TASKS - UPDATE
# =========================================================

@app.route(
    "/api/tasks/<int:task_id>",
    methods=["PATCH"]
)
def edit_task(
    task_id
):

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "error":
                "Authentication required"
        }), 401

    data = request.get_json(
        silent=True
    ) or {}

    task = update_task(

        user_id=user_id,

        task_id=task_id,

        title=data.get(
            "title"
        ),

        description=data.get(
            "description"
        ),

        priority=data.get(
            "priority"
        ),

        deadline=data.get(
            "deadline"
        )
    )

    if not task:

        return jsonify({
            "error": "Task not found"
        }), 404

    return jsonify(
        task
    ), 200


# =========================================================
# TASKS - DELETE
# =========================================================

@app.route(
    "/api/tasks/<int:task_id>",
    methods=["DELETE"]
)
def remove_task(
    task_id
):

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "error":
                "Authentication required"
        }), 401

    success = delete_task(

        user_id=user_id,

        task_id=task_id
    )

    if not success:

        return jsonify({
            "error": "Task not found"
        }), 404

    return jsonify({
        "success": True,
        "message": "Task deleted"
    }), 200


# =========================================================
# FINANCE - GET PAYMENTS
# =========================================================

@app.route(
    "/api/finance",
    methods=["GET"]
)
def finance():

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "error":
                "Authentication required"
        }), 401

    status = request.args.get(
        "status"
    )

    try:

        check_overdue_payments(
            user_id=user_id
        )

        payments = get_payments(
            user_id=user_id,
            status=status
        )

        summary = get_finance_summary(
            user_id=user_id
        )

        paid = summary.get(
            "paid",
            {}
        )

        pending = summary.get(
            "pending",
            {}
        )

        overdue = summary.get(
            "overdue",
            {}
        )

        total_revenue = sum(
            paid.values()
        )

        pending_amount = (
            sum(pending.values())
            +
            sum(overdue.values())
        )

        return jsonify({

            "payments": payments,

            "summary": {

                "total_revenue":
                    total_revenue,

                "pending_amount":
                    pending_amount,

                "paid":
                    paid,

                "pending":
                    pending,

                "overdue":
                    overdue,

                "payment_count":
                    summary.get(
                        "payment_count",
                        0
                    )
            }

        }), 200

    except Exception as error:

        print(
            "Finance API error:",
            error
        )

        return jsonify({
            "error":
                "Could not load finance"
        }), 500


# =========================================================
# FINANCE - GET ONE
# =========================================================

@app.route(
    "/api/finance/<int:payment_id>",
    methods=["GET"]
)
def finance_payment(
    payment_id
):

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "error":
                "Authentication required"
        }), 401

    payment = get_payment(

        user_id=user_id,

        payment_id=payment_id
    )

    if not payment:

        return jsonify({
            "error":
                "Payment not found"
        }), 404

    return jsonify(
        payment
    ), 200


# =========================================================
# FINANCE - CREATE
# =========================================================

@app.route(
    "/api/finance",
    methods=["POST"]
)
def create_finance_payment():

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "error":
                "Authentication required"
        }), 401

    data = request.get_json(
        silent=True
    ) or {}

    amount = data.get(
        "amount"
    )

    if amount is None:

        return jsonify({
            "error":
                "Amount is required"
        }), 400

    try:

        payment = create_payment(

            user_id=user_id,

            amount=amount,

            currency=(
                data.get(
                    "currency"
                )
                or "USD"
            ),

            status=(
                data.get(
                    "status"
                )
                or "pending"
            ),

            invoice_number=
                data.get(
                    "invoice_number"
                ),

            due_date=
                data.get(
                    "due_date"
                ),

            deal_id=
                data.get(
                    "deal_id"
                )
        )

        if not payment:

            return jsonify({
                "error":
                    "Could not create payment"
            }), 400

        return jsonify(
            payment_to_dict(
                payment
            )
        ), 201

    except Exception as error:

        db.session.rollback()

        print(
            "Create payment error:",
            error
        )

        return jsonify({
            "error":
                "Could not create payment"
        }), 500


# =========================================================
# FINANCE - MARK PAID
# =========================================================

@app.route(
    "/api/finance/<int:payment_id>/paid",
    methods=["PATCH"]
)
def finance_mark_paid(
    payment_id
):

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "error":
                "Authentication required"
        }), 401

    payment = mark_payment_paid(

        user_id=user_id,

        payment_id=payment_id
    )

    if not payment:

        return jsonify({
            "error":
                "Payment not found"
        }), 404

    return jsonify(
        payment
    ), 200


# =========================================================
# FINANCE - UPDATE STATUS
# =========================================================

@app.route(
    "/api/finance/<int:payment_id>/status",
    methods=["PATCH"]
)
def finance_status(
    payment_id
):

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "error":
                "Authentication required"
        }), 401

    data = request.get_json(
        silent=True
    ) or {}

    status = data.get(
        "status"
    )

    if not status:

        return jsonify({
            "error":
                "Status is required"
        }), 400

    payment = update_payment_status(

        user_id=user_id,

        payment_id=payment_id,

        status=status
    )

    if not payment:

        return jsonify({
            "error":
                "Payment not found or invalid status"
        }), 400

    return jsonify(
        payment
    ), 200


# =========================================================
# FINANCE - UPDATE INVOICE
# =========================================================

@app.route(
    "/api/finance/<int:payment_id>/invoice",
    methods=["PATCH"]
)
def finance_invoice(
    payment_id
):

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "error":
                "Authentication required"
        }), 401

    data = request.get_json(
        silent=True
    ) or {}

    payment = update_invoice(

        user_id=user_id,

        payment_id=payment_id,

        invoice_number=
            data.get(
                "invoice_number"
            ),

        due_date=
            data.get(
                "due_date"
            )
    )

    if not payment:

        return jsonify({
            "error":
                "Payment not found"
        }), 404

    return jsonify(
        payment
    ), 200


# =========================================================
# FINANCE - DELETE
# =========================================================

@app.route(
    "/api/finance/<int:payment_id>",
    methods=["DELETE"]
)
def finance_delete(
    payment_id
):

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify({
            "error":
                "Authentication required"
        }), 401

    success = delete_payment(

        user_id=user_id,

        payment_id=payment_id
    )

    if not success:

        return jsonify({
            "error":
                "Payment not found"
        }), 404

    return jsonify({

        "success": True,

        "message":
            "Payment deleted"

    }), 200


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )