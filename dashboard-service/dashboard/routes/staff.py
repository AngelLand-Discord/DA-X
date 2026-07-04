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
    valid_discord_id,
)

staff_bp = Blueprint(
    "staff",
    __name__,
)


@staff_bp.route(
    "/guild/<guild_id>/staff-access",
    methods=["GET", "POST"],
)
@require_feature("staff_access")
def staff_access(
    guild_id,
    level,
    guild,
):

    db = get_db()

    if request.method == "POST":

        action = request.form.get(
            "action",
            "add",
        )

        user_id = clean_text(
            request.form.get("user_id"),
            25,
        )

        if not valid_discord_id(user_id):

            db.close()

            return render_template(

                "error.html",

                title="Invalid User ID",

                message="Discord IDs must be numeric.",

            ), 400

        if action == "remove":

            db.execute(
                """
                DELETE FROM guild_permissions

                WHERE guild_id=?

                AND user_id=?
                """,
                (
                    guild_id,
                    user_id,
                ),
            )

        else:

            db.execute(
                """
                INSERT OR REPLACE INTO guild_permissions
                (
                    guild_id,
                    user_id,
                    role,
                    added_by,
                    created_at
                )
                VALUES
                (?, ?, ?, ?, ?)
                """,
                (
                    guild_id,
                    user_id,
                    "staff",
                    current_user_id(),
                    utc_now(),
                ),
            )

        db.commit()

        return redirect(
            url_for(
                "staff.staff_access",
                guild_id=guild_id,
            )
        )

    staff = db.execute(
        """
        SELECT *

        FROM guild_permissions

        WHERE guild_id=?

        ORDER BY user_id
        """,
        (
            guild_id,
        ),
    ).fetchall()

    db.close()

    return render_template(

        "staff_access.html",

        guild_id=guild_id,

        guild_name=guild["name"],

        staff_users=staff,

    )
