import json
from datetime import datetime, timezone

from dashboard.database import (
    execute,
    fetch_all,
    fetch_one,
)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def add_command(
    guild_id,
    requested_by,
    command_type,
    command_name,
    payload=None,
):

    if payload is None:
        payload = {}

    return execute(
        """
        INSERT INTO command_queue
        (
            guild_id,
            requested_by,
            command_type,
            command_name,
            payload,
            status,
            created_at
        )
        VALUES
        (
            ?,
            ?,
            ?,
            ?,
            ?,
            'Pending',
            ?
        )
        """,
        (
            str(guild_id),
            str(requested_by),
            command_type,
            command_name,
            json.dumps(payload),
            utc_now(),
        ),
    )


def get_pending_commands():

    return fetch_all(
        """
        SELECT *
        FROM command_queue
        WHERE status='Pending'
        ORDER BY id ASC
        """
    )


def get_command(command_id):

    return fetch_one(
        """
        SELECT *
        FROM command_queue
        WHERE id=?
        """,
        (command_id,),
    )


def mark_running(command_id):

    execute(
        """
        UPDATE command_queue
        SET status='Running'
        WHERE id=?
        """,
        (command_id,),
    )


def mark_completed(
    command_id,
    result="Completed",
):

    execute(
        """
        UPDATE command_queue
        SET
            status='Completed',
            result=?,
            completed_at=?
        WHERE id=?
        """,
        (
            result,
            utc_now(),
            command_id,
        ),
    )


def mark_failed(
    command_id,
    reason,
):

    execute(
        """
        UPDATE command_queue
        SET
            status='Failed',
            result=?,
            completed_at=?
        WHERE id=?
        """,
        (
            str(reason),
            utc_now(),
            command_id,
        ),
    )


def cancel_command(command_id):

    execute(
        """
        UPDATE command_queue
        SET
            status='Cancelled',
            completed_at=?
        WHERE id=?
        """,
        (
            utc_now(),
            command_id,
        ),
    )


def clear_completed():

    execute(
        """
        DELETE
        FROM command_queue
        WHERE status='Completed'
        """
    )


def queue_stats():

    pending = fetch_one(
        """
        SELECT COUNT(*) AS total
        FROM command_queue
        WHERE status='Pending'
        """
    )["total"]

    running = fetch_one(
        """
        SELECT COUNT(*) AS total
        FROM command_queue
        WHERE status='Running'
        """
    )["total"]

    completed = fetch_one(
        """
        SELECT COUNT(*) AS total
        FROM command_queue
        WHERE status='Completed'
        """
    )["total"]

    failed = fetch_one(
        """
        SELECT COUNT(*) AS total
        FROM command_queue
        WHERE status='Failed'
        """
    )["total"]

    return {
        "pending": pending,
        "running": running,
        "completed": completed,
        "failed": failed,
    }
