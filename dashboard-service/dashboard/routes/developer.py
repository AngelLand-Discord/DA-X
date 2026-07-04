import json

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
)

from ..permissions import require_feature

from ..database import (
    add_command,
    fetchall,
)

from ..utils import (
    current_user_id,
    utc_now,
)

developer_bp = Blueprint(
    "developer",
    __name__,
)


@developer_bp.route(
    "/guild/<guild_id>/developer",
    methods=["GET", "POST"],
)
@require_feature("developer")
def developer(
    guild_id,
    level,
    guild,
):

    if request.method == "POST":

        action = (
            request.form.get("action", "")
            .strip()
            .upper()
        )

        payload = {
            "guild_id": guild_id
        }

        # --------------------------
        # LEAVE
        # --------------------------

        if action == "LEAVE":

            pass

        # --------------------------
        # RELOAD
        # --------------------------

        elif action == "RELOAD":

            pass

        # --------------------------
        # SYNC
        # --------------------------

        elif action == "SYNC":

            pass

        # --------------------------
        # STOP
        # --------------------------

        elif action == "STOP":

            pass

        # --------------------------
        # BROADCAST
        # --------------------------

        elif action == "BROADCAST":

            payload["message"] = request.form.get(
                "message",
                "",
            )

        # --------------------------

        add_command(

            guild_id=guild_id,

            requested_by=current_user_id(),

            command_type="DEVELOPER",

            command_name=action,

            payload=json.dumps(payload),

            created_at=utc_now(),

        )

        return redirect(
            url_for(
                "developer.developer",
                guild_id=guild_id,
            )
        )

    queue = fetchall(
        """
        SELECT *

        FROM command_queue

        ORDER BY id DESC

        LIMIT 100
        """
    )

    return render_template(

        "developer.html",

        guild_id=guild_id,

        guild_name=guild["name"],

        queue=queue,

    )
