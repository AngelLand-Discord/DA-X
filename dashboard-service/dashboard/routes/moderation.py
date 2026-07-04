import json

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
)

from ..permissions import require_feature
from ..database import get_db
from ..utils import (
    clean_text,
    current_user_id,
    utc_now,
)
from ..services.moderation_service import ModerationService


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
        ).upper()

        user_id = clean_text(
            request.form.get("user_id"),
            25,
        )

        reason = clean_text(
            request.form.get("reason"),
            500,
        )

        if action == "WARN":

            ModerationService.warn(
                guild_id,
                user_id,
                reason,
            )

        elif action == "KICK":

            ModerationService.kick(
                guild_id,
                user_id,
                reason,
            )

        elif action == "BAN":

            ModerationService.ban(
                guild_id,
                user_id,
                reason,
            )

        elif action == "TIMEOUT":

            duration = int(
                request.form.get(
                    "duration",
                    10,
                )
            )

            ModerationService.timeout(
                guild_id,
                user_id,
                duration,
                reason,
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
            (
                ?, ?, ?, ?, ?, ?
            )
            """,
            (
                guild_id,
                action,
                user_id,
                current_user_id(),
                reason,
                utc_now(),
            ),
        )

        db.commit()

        return redirect(
            url_for(
                "moderation.moderation",
                guild_id=guild_id,
            )
        )

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

        level=level,

    )
