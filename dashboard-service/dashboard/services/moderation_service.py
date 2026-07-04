from ..queue import Queue


class ModerationService:

    @staticmethod
    def warn(guild_id, user_id, reason):

        Queue.warn(
            guild_id,
            user_id,
            reason,
        )

    @staticmethod
    def kick(guild_id, user_id, reason):

        Queue.kick(
            guild_id,
            user_id,
            reason,
        )

    @staticmethod
    def ban(guild_id, user_id, reason):

        Queue.ban(
            guild_id,
            user_id,
            reason,
        )

    @staticmethod
    def timeout(
        guild_id,
        user_id,
        duration,
        reason,
    ):

        Queue.timeout(
            guild_id,
            user_id,
            duration,
            reason,
        )
