from datetime import datetime

from database import db
from models import Task


# =========================================================
# CREATE TASK FROM AI
# =========================================================

def create_task_from_ai(
    user_id,
    email_id,
    task_data,
    deal_id=None
):

    if not task_data:
        return None

    title = task_data.get("title")

    if not title:
        return None

    # Prevent duplicate AI task from same email
    existing_task = Task.query.filter_by(
        user_id=user_id,
        email_id=email_id,
        title=title
    ).first()

    if existing_task:
        return existing_task

    deadline = parse_datetime(
        task_data.get("deadline")
    )

    priority = task_data.get(
        "priority",
        "medium"
    )

    allowed_priorities = [
        "urgent",
        "high",
        "medium",
        "low"
    ]

    if priority not in allowed_priorities:
        priority = "medium"

    task = Task(
        user_id=user_id,

        email_id=email_id,
        deal_id=deal_id,

        title=title,

        description=task_data.get(
            "description"
        ),

        priority=priority,

        deadline=deadline,

        status="pending",

        created_by_ai=True
    )

    db.session.add(task)
    db.session.commit()

    return task


# =========================================================
# CREATE MANUAL TASK
# =========================================================

def create_task(
    user_id,
    title,
    description=None,
    priority="medium",
    deadline=None,
    deal_id=None,
    email_id=None
):

    if not title:
        return None

    allowed_priorities = [
        "urgent",
        "high",
        "medium",
        "low"
    ]

    if priority not in allowed_priorities:
        priority = "medium"

    if isinstance(deadline, str):
        deadline = parse_datetime(deadline)

    task = Task(
        user_id=user_id,

        deal_id=deal_id,
        email_id=email_id,

        title=title,
        description=description,

        priority=priority,
        deadline=deadline,

        status="pending",

        created_by_ai=False
    )

    db.session.add(task)
    db.session.commit()

    return task


# =========================================================
# GET ALL TASKS
# =========================================================

def get_tasks(
    user_id,
    status=None
):

    query = Task.query.filter_by(
        user_id=user_id
    )

    if status:
        query = query.filter_by(
            status=status
        )

    tasks = (
        query
        .order_by(Task.created_at.desc())
        .all()
    )

    return [
        task_to_dict(task)
        for task in tasks
    ]


# =========================================================
# GET ONE TASK
# =========================================================

def get_task(
    user_id,
    task_id
):

    task = Task.query.filter_by(
        id=task_id,
        user_id=user_id
    ).first()

    if not task:
        return None

    return task_to_dict(task)


# =========================================================
# UPDATE TASK STATUS
# =========================================================

def update_task_status(
    user_id,
    task_id,
    status
):

    allowed_statuses = [
        "pending",
        "in_progress",
        "completed",
        "cancelled"
    ]

    if status not in allowed_statuses:
        return None

    task = Task.query.filter_by(
        id=task_id,
        user_id=user_id
    ).first()

    if not task:
        return None

    task.status = status

    if status == "completed":

        task.completed_at = datetime.utcnow()

    else:

        task.completed_at = None

    db.session.commit()

    return task_to_dict(task)


# =========================================================
# UPDATE TASK
# =========================================================

def update_task(
    user_id,
    task_id,
    title=None,
    description=None,
    priority=None,
    deadline=None
):

    task = Task.query.filter_by(
        id=task_id,
        user_id=user_id
    ).first()

    if not task:
        return None

    if title is not None and title.strip():
        task.title = title.strip()

    if description is not None:
        task.description = description

    if priority is not None:

        allowed_priorities = [
            "urgent",
            "high",
            "medium",
            "low"
        ]

        if priority in allowed_priorities:
            task.priority = priority

    if deadline is not None:

        if isinstance(deadline, str):
            deadline = parse_datetime(deadline)

        task.deadline = deadline

    db.session.commit()

    return task_to_dict(task)


# =========================================================
# DELETE TASK
# =========================================================

def delete_task(
    user_id,
    task_id
):

    task = Task.query.filter_by(
        id=task_id,
        user_id=user_id
    ).first()

    if not task:
        return False

    db.session.delete(task)
    db.session.commit()

    return True


# =========================================================
# PARSE DATE
# =========================================================

def parse_datetime(value):

    if not value:
        return None

    if isinstance(value, datetime):
        return value

    try:

        # Handles values like:
        # 2026-08-10T16:00:00
        # 2026-08-10T16:00:00+05:30

        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )

    except (ValueError, TypeError):

        return None


# =========================================================
# TASK TO DICTIONARY
# =========================================================

def task_to_dict(task):

    return {
        "id": task.id,

        "title": task.title,

        "description": task.description,

        "priority": task.priority,

        "status": task.status,

        "deadline": (
            task.deadline.isoformat()
            if task.deadline
            else None
        ),

        "created_by_ai": task.created_by_ai,

        "deal_id": task.deal_id,
        "email_id": task.email_id,

        "created_at": (
            task.created_at.isoformat()
            if task.created_at
            else None
        ),

        "completed_at": (
            task.completed_at.isoformat()
            if task.completed_at
            else None
        )
    }