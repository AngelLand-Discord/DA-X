from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
)

from permissions import require_feature

from database import get_db

from utils import (
    clean_text,
    utc_now,
    current_user_id,
)

tickets_bp = Blueprint(
    "tickets",
    __name__,
)


@tickets_bp.route(
    "/guild/<guild_id>/tickets",
    methods=["GET", "POST"],
)
@require_feature("tickets")
def tickets(
    guild_id,
    level,
    guild,
):

    db = get_db()

    if request.method == "POST":

        action = clean_text(
            request.form.get("action"),
            20,
        ).lower()

        ticket_id = request.form.get(
            "ticket_id"
        )

        # ------------------------
        # Open Ticket
        # ------------------------

        if action == "open":

            subject = clean_text(
                request.form.get(
                    "subject"
                ),
                200,
            )

            if not subject:
                subject = "Support Ticket"

            message = clean_text(
                request.form.get(
                    "message"
                ),
                4000,
            )

            now = utc_now()

            cur = db.execute(
                """
                INSERT INTO tickets
                (
                    guild_id,
                    user_id,
                    username,
                    subject,
                    status,
                    created_at,
                    updated_at
                )
                VALUES
                (
                    ?, ?, ?, ?, 'Open', ?, ?
                )
                """,
                (
                    guild_id,
                    current_user_id(),
                    request.form.get(
                        "username",
                        "Unknown",
                    ),
                    subject,
                    now,
                    now,
                ),
            )

            ticket = cur.lastrowid

            if message:

                db.execute(
                    """
                    INSERT INTO ticket_messages
                    (
                        ticket_id,
                        guild_id,
                        user_id,
                        username,
                        message,
                        created_at
                    )
                    VALUES
                    (
                        ?, ?, ?, ?, ?, ?
                    )
                    """,
                    (
                        ticket,
                        guild_id,
                        current_user_id(),
                        request.form.get(
                            "username",
                            "Unknown",
                        ),
                        message,
                        now,
                    ),
                )

        # ------------------------
        # Reply
        # ------------------------

        elif action == "reply":

            message = clean_text(
                request.form.get(
                    "message"
                ),
                4000,
            )

            if message:

                db.execute(
                    """
                    INSERT INTO ticket_messages
                    (
                        ticket_id,
                        guild_id,
                        user_id,
                        username,
                        message,
                        created_at
                    )
                    VALUES
                    (
                        ?, ?, ?, ?, ?, ?
                    )
                    """,
                    (
                        ticket_id,
                        guild_id,
                        current_user_id(),
                        request.form.get(
                            "username",
                            "Unknown",
                        ),
                        message,
                        utc_now(),
                    ),
                )

                db.execute(
                    """
                    UPDATE tickets

                    SET updated_at=?

                    WHERE id=?
                    """,
                    (
                        utc_now(),
                        ticket_id,
                    ),
                )

        # ------------------------
        # Close
        # ------------------------

        elif action == "close":

            db.execute(
                """
                UPDATE tickets

                SET
                    status='Closed',
                    updated_at=?

                WHERE id=?
                """,
                (
                    utc_now(),
                    ticket_id,
                ),
            )

        # ------------------------
        # Reopen
        # ------------------------

        elif action == "reopen":

            db.execute(
                """
                UPDATE tickets

                SET
                    status='Open',
                    updated_at=?

                WHERE id=?
                """,
                (
                    utc_now(),
                    ticket_id,
                ),
            )

        # ------------------------
        # Delete
        # ------------------------

        elif action == "delete":

            db.execute(
                """
                DELETE FROM ticket_messages

                WHERE ticket_id=?
                """,
                (
                    ticket_id,
                ),
            )

            db.execute(
                """
                DELETE FROM tickets

                WHERE id=?
                """,
                (
                    ticket_id,
                ),
            )

        db.commit()

        return redirect(
            url_for(
                "tickets.tickets",
                guild_id=guild_id,
            )
        )

    tickets = db.execute(
        """
        SELECT *

        FROM tickets

        WHERE guild_id=?

        ORDER BY updated_at DESC
        """,
        (
            guild_id,
        ),
    ).fetchall()

    messages = db.execute(
        """
        SELECT *

        FROM ticket_messages

        WHERE guild_id=?

        ORDER BY created_at
        """,
        (
            guild_id,
        ),
    ).fetchall()

    db.close()

    return render_template(

        "tickets.html",

        guild_id=guild_id,

        guild_name=guild["name"],

        tickets=tickets,

        messages=messages,

        level=level,

    )
