import json

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
)

from ..permissions import require_feature

from ..database import (
    get_db,
    add_command,
)

from ..utils import (
    clean_text,
    current_user_id,
    utc_now,
)


moderation_bp = Blueprint(
    "moderation",
    __name__,
)


@moderation_bp.route(
    "/guild/<guild_id>/moderation",
    methods=["GET", "POST"],
)
@require_feature("moderation")
def moderation(
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

        user_id = clean_text(
            request.form.get("user_id"),
            25,
        )

        reason = clean_text(
            request.form.get("reason"),
            500,
        )

        payload = {

            "guild_id": guild_id,

            "user_id": user_id,

            "reason": reason,

        }

        if action == "timeout":

            payload["duration"] = int(
                request.form.get(
                    "duration",
                    10,
                )
            )

        add_command(

            guild_id=guild_id,

            requested_by=current_user_id(),

            command_type="MODERATION",

            command_name=action.upper(),

            payload=json.dumps(payload),

            created_at=utc_now(),

        )

        db.execute(
            """
            INSERT INTO modlogs
            (
                guild_id,
                action,
                target,
                moderator,
                reason,
                timestamp
            )
            VALUES
            (?, ?, ?, ?, ?, ?)
            """,
            (
                guild_id,
                action.upper(),
                user_id,
                current_user_id(),
                reason,
                utc_now(),
            ),
        )

        db.commit()

    rows = db.execute(
        """
        SELECT *

        FROM modlogs

        WHERE guild_id=?

        ORDER BY id DESC

        LIMIT 50
        """,
        (
            guild_id,
        ),
    ).fetchall()

    db.close()

    return render_template(

        "moderation.html",

        guild_id=guild_id,

        guild_name=guild["name"],

        logs=rows,

    )
