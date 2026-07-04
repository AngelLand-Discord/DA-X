import json

from .database import add_command
from .utils import utc_now, current_user_id


class Queue:

    @staticmethod
    def push(
        guild_id,
        command_type,
        command_name,
        payload,
    ):

        add_command(

            guild_id=guild_id,

            requested_by=current_user_id(),

            command_type=command_type.upper(),

            command_name=command_name.upper(),

            payload=json.dumps(payload),

            created_at=utc_now(),

        )

    # ----------------------------
    # Moderation
    # ----------------------------

    @staticmethod
    def warn(guild_id, user_id, reason):

        Queue.push(

            guild_id,

            "MODERATION",

            "WARN",

            {

                "guild_id": guild_id,

                "user_id": user_id,

                "reason": reason,

            },

        )

    @staticmethod
    def kick(guild_id, user_id, reason):

        Queue.push(

            guild_id,

            "MODERATION",

            "KICK",

            {

                "guild_id": guild_id,

                "user_id": user_id,

                "reason": reason,

            },

        )

    @staticmethod
    def ban(guild_id, user_id, reason):

        Queue.push(

            guild_id,

            "MODERATION",

            "BAN",

            {

                "guild_id": guild_id,

                "user_id": user_id,

                "reason": reason,

            },

        )

    @staticmethod
    def timeout(
        guild_id,
        user_id,
        duration,
        reason,
    ):

        Queue.push(

            guild_id,

            "MODERATION",

            "TIMEOUT",

            {

                "guild_id": guild_id,

                "user_id": user_id,

                "duration": duration,

                "reason": reason,

            },

        )

    # ----------------------------
    # Developer
    # ----------------------------

    @staticmethod
    def reload():

        Queue.push(

            "0",

            "DEVELOPER",

            "RELOAD",

            {},

        )

    @staticmethod
    def sync():

        Queue.push(

            "0",

            "DEVELOPER",

            "SYNC",

            {},

        )

    @staticmethod
    def stop():

        Queue.push(

            "0",

            "DEVELOPER",

            "STOP",

            {},

        )

    @staticmethod
    def broadcast(message):

        Queue.push(

            "0",

            "DEVELOPER",

            "BROADCAST",

            {

                "message": message,

            },

        )
