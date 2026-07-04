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

appeals_bp = Blueprint(
    "appeals",
    __name__,
)


@appeals_bp.route(
    "/guild/<guild_id>/appeals",
    methods=["GET", "POST"],
)
@require_feature("appeals")
def appeals(
    guild_id,
    level,
    guild,
):

    db = get_db()

    if request.method == "POST":

        appeal_type = clean_text(
            request.form.get(
                "appeal_type",
                "Ban Appeal",
            ),
            100,
        )

        appeal = clean_text(
            request.form.get(
                "appeal"
            ),
            4000,
        )

        if appeal:

            db.execute(
                """
                INSERT INTO appeals
                (
                    guild_id,
                    user_id,
                    username,
                    appeal_type,
                    appeal,
                    created_at
                )
                VALUES
                (?, ?, ?, ?, ?, ?)
                """,
                (
                    guild_id,
                    current_user_id(),
                    request.form.get(
                        "username",
                        "Unknown",
                    ),
                    appeal_type,
                    appeal,
                    utc_now(),
                ),
            )

            db.commit()

        return redirect(
            url_for(
                "appeals.appeals",
                guild_id=guild_id,
            )
        )

    rows = db.execute(
        """
        SELECT *

        FROM appeals

        WHERE guild_id=?

        ORDER BY id DESC
        """,
        (
            guild_id,
        ),
    ).fetchall()

    db.close()

    return render_template(

        "appeals.html",

        guild_id=guild_id,

        guild_name=guild["name"],

        appeals=rows,

        level=level,

    )
