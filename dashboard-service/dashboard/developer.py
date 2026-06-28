from dashboard.config import DEV_ID
from dashboard.queue import add_command


class DeveloperManager:

    @staticmethod
    def is_developer(user_id):

        return int(user_id) == DEV_ID

    @staticmethod
    def send_command(
        guild_id,
        user_id,
        command,
        payload=None
    ):

        if not DeveloperManager.is_developer(user_id):

            raise PermissionError(
                "Only the developer can use developer commands."
            )

        return add_command(
            guild_id=guild_id,
            requested_by=user_id,
            command_type="DEVELOPER",
            command_name=command.upper(),
            payload=payload or {}
        )

    @staticmethod
    def reload_bot(
        guild_id,
        user_id,
    ):

        return DeveloperManager.send_command(
            guild_id,
            user_id,
            "RELOAD"
        )

    @staticmethod
    def leave_server(
        guild_id,
        user_id,
    ):

        return DeveloperManager.send_command(
            guild_id,
            user_id,
            "LEAVE"
        )

    @staticmethod
    def shutdown(
        guild_id,
        user_id,
    ):

        return DeveloperManager.send_command(
            guild_id,
            user_id,
            "STOP"
        )

    @staticmethod
    def sync_commands(
        guild_id,
        user_id,
    ):

        return DeveloperManager.send_command(
            guild_id,
            user_id,
            "SYNC"
        )

    @staticmethod
    def restart_cogs(
        guild_id,
        user_id,
    ):

        return DeveloperManager.send_command(
            guild_id,
            user_id,
            "RESTART_COGS"
        )

    @staticmethod
    def broadcast(
        guild_id,
        user_id,
        message
    ):

        return DeveloperManager.send_command(
            guild_id,
            user_id,
            "BROADCAST",
            {
                "message": message
            }
        )

    @staticmethod
    def execute(
        guild_id,
        user_id,
        command,
        payload=None
    ):

        return DeveloperManager.send_command(
            guild_id,
            user_id,
            command,
            payload
        )
