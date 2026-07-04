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
    current_user_id,
    utc_now,
)

automod_bp = Blueprint(
    "automod",
    __name__,
)

RULES = [
    "bad_words",
    "spam",
    "invite_links",
    "caps_spam",
    "mass_mentions",
]


@automod_bp.route(
    "/guild/<guild_id>/automod",
    methods=["GET", "POST"],
)
@require_feature("settings")
def automod(
    guild_id,
    level,
    guild,
):

    db = get_db()

    if request.method == "POST":

        for rule in RULES:

            enabled = (
                1
                if request.form.get(
                    f"{rule}_enabled"
                ) == "on"
                else 0
            )

            config = clean_text(
                request.form.get(
                    f"{rule}_config"
                ),
                2000,
            )

            db.execute(
                """
                INSERT INTO automod_rules
                (
                    guild_id,
                    rule_type,
                    enabled,
                    config,
                    updated_by,
                    updated_at
                )
                VALUES
                (
                    ?, ?, ?, ?, ?, ?
                )

                ON CONFLICT
                (
                    guild_id,
                    rule_type
                )

                DO UPDATE SET

                    enabled=excluded.enabled,

                    config=excluded.config,

                    updated_by=excluded.updated_by,

                    updated_at=excluded.updated_at
                """,
                (
                    guild_id,
                    rule,
                    enabled,
                    config,
                    current_user_id(),
                    utc_now(),
                ),
            )

        db.commit()

        return redirect(
            url_for(
                "automod.automod",
                guild_id=guild_id,
            )
        )

    rows = db.execute(
        """
        SELECT *

        FROM automod_rules

        WHERE guild_id=?

        ORDER BY rule_type
        """,
        (
            guild_id,
        ),
    ).fetchall()

    db.close()

    rules = {

        row["rule_type"]: row

        for row in rows

    }

    return render_template(

        "automod.html",

        guild_id=guild_id,

        guild_name=guild["name"],

        rules=rules,

        level=level,

    )
