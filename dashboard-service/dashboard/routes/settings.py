from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
)

from permissions import require_feature
from database import (
    get_db,
    fetchone,
)
from utils import (
    clean_text,
    valid_discord_id,
)

settings_bp = Blueprint(
    "settings",
    __name__,
)


@settings_bp.route(
    "/guild/<guild_id>/settings",
    methods=["GET", "POST"],
)
@require_feature("settings")
def settings(
    guild_id,
    level,
    guild,
):

    db = get_db()

    if request.method == "POST":

        log_channel = clean_text(
            request.form.get("log_channel"),
            25,
        )

        mod_role = clean_text(
            request.form.get("mod_role"),
            25,
        )

        announcement_channel = clean_text(
            request.form.get("announcement_channel"),
            25,
        )

        for value in (
            log_channel,
            mod_role,
            announcement_channel,
        ):

            if value and not valid_discord_id(value):

                db.close()

                return render_template(

                    "error.html",

                    title="Invalid Discord ID",

                    message="One or more IDs are invalid.",

                ), 400

        db.execute(
            """
            INSERT INTO settings
            (
                guild_id,
                log_channel,
                mod_role,
                announcement_channel
            )
            VALUES
            (
                ?, ?, ?, ?
            )

            ON CONFLICT(guild_id)

            DO UPDATE SET

                log_channel=excluded.log_channel,

                mod_role=excluded.mod_role,

                announcement_channel=excluded.announcement_channel
            """,
            (
                guild_id,
                log_channel,
                mod_role,
                announcement_channel,
            ),
        )

        db.commit()

        db.close()

        return redirect(
            url_for(
                "settings.settings",
                guild_id=guild_id,
            )
        )

    row = fetchone(
        """
        SELECT *

        FROM settings

        WHERE guild_id=?
        """,
        (
            guild_id,
        ),
    )

    db.close()

    return render_template(

        "settings.html",

        guild_id=guild_id,

        guild_name=guild["name"],

        settings=row,

        level=level,

    )
