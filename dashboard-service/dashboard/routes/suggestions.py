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

suggestions_bp = Blueprint(
    "suggestions",
    __name__,
)


@suggestions_bp.route(
    "/guild/<guild_id>/suggestions",
    methods=["GET", "POST"],
)
@require_feature("suggestions")
def suggestions(
    guild_id,
    level,
    guild,
):

    db = get_db()

    if request.method == "POST":

        suggestion = clean_text(
            request.form.get("suggestion"),
            4000,
        )

        if suggestion:

            db.execute(
                """
                INSERT INTO suggestions
                (
                    guild_id,
                    user_id,
                    username,
                    suggestion,
                    created_at
                )
                VALUES
                (?, ?, ?, ?, ?)
                """,
                (
                    guild_id,
                    current_user_id(),
                    request.form.get(
                        "username",
                        "Unknown",
                    ),
                    suggestion,
                    utc_now(),
                ),
            )

            db.commit()

        return redirect(
            url_for(
                "suggestions.suggestions",
                guild_id=guild_id,
            )
        )

    rows = db.execute(
        """
        SELECT *

        FROM suggestions

        WHERE guild_id=?

        ORDER BY id DESC
        """,
        (
            guild_id,
        ),
    ).fetchall()

    db.close()

    return render_template(

        "suggestions.html",

        guild_id=guild_id,

        guild_name=guild["name"],

        suggestions=rows,

        level=level,

    )
