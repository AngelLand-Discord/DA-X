from flask import (
    Blueprint,
    render_template,
)

from ..permissions import require_feature
from ..database import fetchall

logs_bp = Blueprint(
    "logs",
    __name__,
)


@logs_bp.route(
    "/guild/<guild_id>/logs"
)
@require_feature("logs")
def logs(
    guild_id,
    level,
    guild,
):

    rows = fetchall(
        """
        SELECT *

        FROM modlogs

        WHERE guild_id=?

        ORDER BY id DESC

        LIMIT 200
        """,
        (
            guild_id,
        ),
    )

    return render_template(

        "logs.html",

        guild_id=guild_id,

        guild_name=guild["name"],

        logs=rows,

        level=level,

    )
